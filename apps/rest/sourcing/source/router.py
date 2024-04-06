from fastapi import APIRouter

from sourcing.source.aspsp.router import router as aspsp_router

router = APIRouter(prefix="/sources")
router.include_router(aspsp_router)
