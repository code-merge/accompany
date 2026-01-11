from passlib.hash import bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.onboarding.data.constants import LANGUAGES
from app.core.db.models import User, Company, Language, Module

async def create_system_admin_user(db: AsyncSession, email: str, password: str) -> tuple[bool, str]:
    try:
        user = User(email=email, hashed_password=bcrypt.hash(password), role="system_admin")
        db.add(user)
        await db.commit()
        return True, "✅ System admin user created"
    except IntegrityError:
        return False, f"❌ Email '{email}' already exists"
    except Exception as e:
        return False, f"❌ Failed to create admin: {e}"

async def create_company_record(db: AsyncSession, name: str, industry: str) -> tuple[bool, str]:
    try:
        db.add(Company(name=name, industry=industry))
        await db.commit()
        return True, "✅ Company record created"
    except Exception as e:
        return False, f"❌ Failed to create company: {e}"

async def seed_languages(db: AsyncSession) -> str:
    try:
        for code in LANGUAGES:
            lang = Language(code=code, label=code.upper())
            await db.merge(lang)
        await db.commit()
        return "✔️ Languages seeded"
    except Exception as e:
        return f"❌ Failed to seed languages: {e}"


async def seed_modules(db: AsyncSession, modules: list[str]) -> str:
    try:
        for name in modules:
            module = Module(name=name)
            await db.merge(module)
        await db.commit()
        return "✔️ Modules seeded"
    except Exception as e:
        return f"❌ Failed to seed modules: {e}"
