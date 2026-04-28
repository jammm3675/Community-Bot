from aiogram import Router
from .welcome import router as welcome_router
from .social import router as social_router
from .rpg import router as rpg_router
from .otc import router as otc_router
from .admin import router as admin_router

router = Router()

router.include_router(welcome_router)
router.include_router(social_router)
router.include_router(rpg_router)
router.include_router(otc_router)
router.include_router(admin_router)
