from fastapi import FastAPI

from app.schema import JavaOutlet, JavaOutletCreate, JavaOutletList



app = FastAPI(
    title="JavaHouse Coffee Kenya Outlets API",
    description=(
        "APIs for managing JavaHouse Coffee Kenya outlets, catalog items, and orders."
    ),
    version="0.2.0",
)


@app.get("/", response_model=dict)
def service_overview() -> dict:
    return {
        "service": "JavaHouse Coffee Kenya Outlets",
        "version": "0.2.0",
        "status": "ok",
    }
