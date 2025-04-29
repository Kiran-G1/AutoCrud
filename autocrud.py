from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import create_model
from sqlalchemy import select, update, delete, insert, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import metadata, get_db
from typing import Optional, Dict, Any

def create_dynamic_crud_router(table_name: str):
    router = APIRouter(prefix=f"/{table_name}", tags=[table_name])
    table = metadata.tables[table_name]
    columns = table.columns

    # Dynamically create Pydantic models
    # For POST/PUT requests (all fields required unless nullable)
    fields_create = {
        col.name: (col.type.python_type, ... if not col.nullable else None)
        for col in columns
    }
    CreateModel = create_model(f"{table_name}Create", **fields_create)

    # For responses (all fields optional)
    fields_response = {col.name: (col.type.python_type, None) for col in columns}
    ResponseModel = create_model(f"{table_name}Response", **fields_response)

    # For paginated response
    PaginatedResponse = create_model(
        f"{table_name}PaginatedResponse",
        items=(list[ResponseModel], ...),
        total=(int, ...),
        page=(int, ...),
        size=(int, ...),
        pages=(int, ...)
    )

    # Get identifier columns (primary key or all columns if no primary key)
    identifier_columns = table.primary_key.columns if table.primary_key else columns

    # --- CRUD Endpoints ---
    # GET All with pagination and filtering
    @router.get("/", response_model=PaginatedResponse)
    async def get_all(
        db: AsyncSession = Depends(get_db),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(10, ge=1, le=100, description="Items per page"),
        **filters: Any
    ):
        # Base query
        base_query = select(table)
        
        # Apply filters if provided
        if filters:
            filter_conditions = []
            for field, value in filters.items():
                if value is not None and hasattr(table.c, field):
                    filter_conditions.append(getattr(table.c, field) == value)
            if filter_conditions:
                base_query = base_query.where(and_(*filter_conditions))

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await db.scalar(count_query)

        # Calculate pagination
        total_pages = (total + size - 1) // size
        offset = (page - 1) * size

        # Get paginated results
        query = base_query.offset(offset).limit(size)
        result = await db.execute(query)
        items = [dict(row._mapping) for row in result.fetchall()]

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": total_pages
        }

    # GET Single
    @router.get("/{item_id}", response_model=ResponseModel)
    async def get_single(item_id: int, db: AsyncSession = Depends(get_db)):
        # For tables without primary key, we'll use the first column as identifier
        if not table.primary_key:
            first_column = list(columns)[0]
            result = await db.execute(
                select(table).where(getattr(table.c, first_column.name) == item_id)
            )
        else:
            # For tables with primary key, use the first primary key column
            pk_column = list(table.primary_key.columns)[0]
            result = await db.execute(
                select(table).where(getattr(table.c, pk_column.name) == item_id)
            )
        
        item = result.fetchone()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return dict(item._mapping)

    # POST
    @router.post("/", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
    async def create_item(item: CreateModel, db: AsyncSession = Depends(get_db)):
        data = item.dict()
        result = await db.execute(insert(table).values(**data).returning(table))
        await db.commit()
        new_item = result.fetchone()
        return dict(new_item._mapping)

    # PUT
    @router.put("/{item_id}", response_model=ResponseModel)
    async def update_item(
        item_id: int, 
        item: CreateModel, 
        db: AsyncSession = Depends(get_db)
    ):
        # Get update data (exclude unset fields for partial updates)
        update_data = item.dict(exclude_unset=True)

        # Build where clause using all identifier columns
        where_clause = and_(*[getattr(table.c, col.name) == item_id for col in identifier_columns])

        # Execute update
        result = await db.execute(
            update(table)
            .where(where_clause)
            .values(**update_data)
            .returning(table)
        )
        await db.commit()
        updated_item = result.fetchone()
        
        if not updated_item:
            raise HTTPException(status_code=404, detail="Item not found")
        return dict(updated_item._mapping)

    # DELETE
    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
        # Build where clause using all identifier columns
        where_clause = and_(*[getattr(table.c, col.name) == item_id for col in identifier_columns])
        
        result = await db.execute(
            delete(table).where(where_clause)
        )
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")

    return router