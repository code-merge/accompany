from fastapi import APIRouter


onboarding_router = APIRouter()

from .welcome_router import router as welcome_router
from .db_setup_router import router as db_setup_router
from .admin_user_router import router as admin_user_router
from .company_setup_route import router as company_setup_route





onboarding_router.include_router(welcome_router)
onboarding_router.include_router(db_setup_router)
onboarding_router.include_router(admin_user_router)
onboarding_router.include_router(company_setup_route)

