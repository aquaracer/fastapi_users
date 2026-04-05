from fastapi import APIRouter

from src.users.controllers.auth_controller import router as auth_router
from src.users.controllers.users_controller import router as user_router


def get_apps_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1")
    router.include_router(user_router, prefix="/users", tags=["users"])
    router.include_router(auth_router, prefix="/auth", tags=["auth"])
    return router
