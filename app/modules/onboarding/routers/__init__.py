from fastapi import APIRouter


onboarding_router = APIRouter()

from .welcome_router import router as welcome_router
from .db_setup_router import router as db_setup_router



onboarding_router.include_router(welcome_router)
onboarding_router.include_router(db_setup_router)

