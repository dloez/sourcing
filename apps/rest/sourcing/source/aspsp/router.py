from typing import List

from fastapi import APIRouter, Depends

from sourcing.source.aspsp.db import aspsps_collection
from sourcing.source.aspsp.models import ASPSP
from sourcing.user.auth import get_current_active_user

router = APIRouter(
    prefix="/aspsps",
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/", response_model=List[ASPSP])
async def list():
    return await aspsps_collection.find().to_list(None)
