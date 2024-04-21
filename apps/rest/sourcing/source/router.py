from fastapi import APIRouter, Depends

from sourcing.source.aspsp.router import router as aspsp_router
from sourcing.source.crypto_wallet.router import router as crypto_wallet_router
from sourcing.user.auth import get_current_active_user

router = APIRouter(prefix="/sources", dependencies=[Depends(get_current_active_user)])
router.include_router(aspsp_router)
router.include_router(crypto_wallet_router)
