from aiogram import Router
from . import welcome, social, otc, rpg

router = Router()

router.include_router(welcome.router)
router.include_router(social.router)
router.include_router(otc.router)
router.include_router(rpg.router)
