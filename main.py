import asyncio
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import metadata, reflect_tables, engine
from autocrud import create_dynamic_crud_router
from auth import get_current_user

app = FastAPI(
    title="AutoCRUD API",
    description="Automatically generated CRUD API endpoints",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Reflect tables and register routes on startup
@app.on_event("startup")
async def startup():
    # Reflect tables
    async with engine.begin() as conn:
        await conn.run_sync(metadata.reflect)

    # Register routes for all tables
    for table_name in metadata.tables.keys():
        router = create_dynamic_crud_router(table_name)
        # Add authentication to all routes
        router.dependencies = [Depends(get_current_user)]
        app.include_router(router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}