# AutoCrud

> **TL;DR:** Point AutoCrud at your SQL Server instance, and you instantly get a self-documenting REST API for every table—perfect for prototypes, admin portals, or data engineering pipelines.


## 📚 Introduction

**AutoCrud** is a lightweight FastAPI service that **discovers every table in a SQL Server database and exposes fully-featured CRUD (Create / Read / Update / Delete) REST endpoints on the fly—no hand-written routers or models required.**  
At startup, AutoCrud inspects SQL Server’s catalog views (`sys.tables`, `sys.columns`, `sys.foreign_keys`, …), converts the metadata into Pydantic schemas, and mounts dynamic FastAPI routers for each table. The resulting API ships with auto-generated OpenAPI/Swagger docs, ready for immediate consumption by front-end apps, scripts, or BI tools.

### 🔑 Key Features
- **Zero-boilerplate CRUD** – create, read, update, delete, and list rows in any table without writing a single line of endpoint code.  
- **Schema-driven** – changes to the underlying database (new tables/columns) are reflected at the next app restart; no code-gen step needed.  
- **Type-safe models** – Pydantic schemas are built from SQL types at runtime, providing request validation and clear API docs.  
- **Pagination & filtering** – endpoints accept standard `limit`, `offset`, and column-based query parameters out of the box.  
- **Pluggable policies** – hook in your own auth, RBAC, or soft-delete logic via dependency injection.  
- **Instant docs** – Swagger UI and ReDoc are served automatically, complete with per-table examples.  

### 🚀 Why AutoCrud?
Developers often spend hours scaffolding the same CRUD plumbing for internal tools, admin dashboards, or data-ops scripts. AutoCrud eliminates that busywork, letting you:
1. **Prototype in minutes** – stand up an API against an existing database for ad-hoc integrations or analytics.  
2. **Keep pace with schema drift** – when tables evolve, simply restart the service; the endpoints stay in sync.  
3. **Stay lean** – focus on business logic, not repetitive boilerplate.

### 🛠️ Built With
- **FastAPI** – high-performance async Python web framework.  
- **SQLAlchemy 2.0 (async)** – runtime reflection & database access.  
- **Pydantic** – data validation and schema generation.  
- **Microsoft SQL Server** – metadata source and persistence layer.


