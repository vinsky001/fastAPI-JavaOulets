from fastapi import FastAPI
from app.database import init_db, run_db_operation
import json
from datetime import datetime, timezone
from app.schema import (
    JavaOutlet,
    JavaOutletCreate,
    JavaOutletList,
    JavaOutletMenuItem,
    JavaOutletMenuItemCreate,
    JavaOutletOrder,
    JavaOutletOrderCreate,
    JavaOutletOrderSummary,
    JavaOutletWithMenu,
)




app = FastAPI(
    title="JavaHouse Coffee Kenya Outlets API",
    description=(
        "APIs for managing JavaHouse Coffee Kenya outlets, catalog items, and orders."
    ),
    version="0.2.0",
)

@app.on_event("startup")
async def startup_event() -> None:
    await init_db()

@app.get("/", response_model=dict)
def service_overview() -> dict:
    return {
        "service": "JavaHouse Coffee Kenya Outlets",
        "version": "0.2.0",
        "status": "ok",
    }
    
@app.get("/outlets/", response_model=JavaOutletList)
async def list_java_outlets() -> JavaOutletList:
    """Lists all Javahouse Coffee Kenya Outlets"""
    rows = await run_db_operation(
        lambda connection: connection.execute("SELECT * FROM java_outlets ORDER BY name").mappings().all()
    ) 
    
    outlets = [dict(row) for row in rows]
    return JavaOutletList(outlets=outlets)
    
