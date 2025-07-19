from fastapi import APIRouter


onboarding_router = APIRouter()

from .welcome_router import router as welcome_router


onboarding_router.include_router(welcome_router)
