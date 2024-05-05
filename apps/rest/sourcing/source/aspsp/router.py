from typing import List

from fastapi import APIRouter, Depends, HTTPException

from sourcing.source.aspsp.db import aspsps_collection
from sourcing.source.aspsp.enable_banking import client as eb
from sourcing.source.aspsp.models import (
    ASPSP,
    ASPSPAuthRequest,
    ASPSPAuthResponse,
    ASPSPResponse,
    ASPSPSessionRequest,
    ASPSPSourceDetails,
)
from sourcing.source.models import Source, SourceKind
from sourcing.user.auth import get_current_active_user
from sourcing.user.db import users_collection
from sourcing.user.models import User

router = APIRouter(
    prefix="/aspsps",
)


@router.get("/", response_model=List[ASPSPResponse], response_model_by_alias=False)
async def list():
    aspsps_collection.find()
    aspsps = [ASPSP(**aspsp) async for aspsp in aspsps_collection.find()]
    return aspsps


@router.post("/auth", response_model=ASPSPAuthResponse)
async def auth_to_aspsp(auth_to_aspsp: ASPSPAuthRequest):
    aspsp = await aspsps_collection.find_one({"_id": auth_to_aspsp.aspsp_id})
    if not aspsp:
        raise HTTPException(status_code=404, detail="ASPSP not found")
    aspsp = ASPSP(**aspsp)
    return await eb.init_auth_session(
        name=aspsp.name,
        country=aspsp.country,
        redirect_url=auth_to_aspsp.redirect_url,
    )


@router.post("/session")
async def create_session(
    session_request: ASPSPSessionRequest,
    current_user: User = Depends(get_current_active_user),
):
    session = await eb.create_session(session_request.code)
    for account in session["accounts"]:
        iban = None
        if account["account_id"]:
            iban = account["account_id"].get("iban", None)
        source = Source(
            kind=SourceKind.ASPSP,
            details=ASPSPSourceDetails(
                iban=iban,
                currency=account["currency"],
                name=account["name"],
                eb_session=session["session_id"],
                eb_uid=account["uid"],
                eb_id_hash=account["identification_hash"],
            ),
        )

        found = False
        for s in current_user.sources:
            if s.kind != SourceKind.ASPSP:
                continue

            if s.details.eb_id_hash != source.details.eb_id_hash:
                continue

            found = True
            await users_collection.update_one(
                {
                    "_id": current_user.id,
                    "sources.details.eb_id_hash": source.details.eb_id_hash,
                },
                {"$set": {"sources.$": source.model_dump()}},
            )

        if not found:
            await users_collection.update_one(
                {"_id": current_user.id},
                {"$push": {"sources": source.model_dump()}},
            )
    return {"status": "ok"}
