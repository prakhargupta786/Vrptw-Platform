from fastapi import APIRouter

from app.api.v1.endpoints import (auth, demand, exports, health, master_data, metrics, outcomes, planning, quality,
                                  runs, users)

api_router = APIRouter()
for module in (health, auth, users, runs, master_data, demand, planning, outcomes, quality, metrics, exports):
    api_router.include_router(module.router)
