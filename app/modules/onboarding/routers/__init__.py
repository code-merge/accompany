from fastapi import APIRouter

from .welcome_router import router as welcome_router
from .db_setup_router import router as db_setup_router
from .admin_user_router import router as admin_user_router
from .company_setup_route import router as company_setup_route
from .system_setup_router import router as system_setup_router
from .finish_setup_router import router as finish_setup_router


onboarding_router = APIRouter()

"""
This module initializes and aggregates all onboarding-related API routers for the application.

Routers included:
- welcome_router: Handles welcome and initial onboarding endpoints.
- db_setup_router: Manages database setup endpoints during onboarding.
- admin_user_router: Handles creation and setup of the initial admin user.
- company_setup_route: Manages company information setup endpoints.
- system_setup_router: Handles system configuration endpoints during onboarding.
- finish_setup_router: Finalizes the onboarding process.

The `onboarding_router` is an APIRouter instance that includes all the above routers, providing a unified entry point for onboarding-related API routes.
"""

onboarding_router.include_router(welcome_router)
onboarding_router.include_router(db_setup_router)
onboarding_router.include_router(admin_user_router)
onboarding_router.include_router(company_setup_route)
onboarding_router.include_router(system_setup_router)
onboarding_router.include_router(finish_setup_router)