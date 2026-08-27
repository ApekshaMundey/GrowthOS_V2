from fastapi import APIRouter
# Import v1 routers once created in subsequent phases

api_router = APIRouter(prefix="/api/v1")

# Placeholder router registrations:
# api_router.include_router(auth.router, tags=["Auth"])
# api_router.include_router(users.router, tags=["Users"])
