import json
from typing import Any

import semver
from fastapi import APIRouter, Header

from app import cache, schemas
from app.services import rankings

router = APIRouter()


@router.get("/", response_model=list[schemas.Ranking])
async def get_rankings(app_version: str | None = Header(None)) -> Any:
    try:
        response = [schemas.Ranking.parse_obj(ranking) for ranking in json.loads(await cache.get("rankings"))]
    except cache.CacheMiss:
        response = await rankings.ranking_list()

    # TODO: revert after a month or so
    if app_version and semver.compare("0.2.12", app_version[1:]) > -1:
        ranking_replace = {
            "Asia-Pacific": "Asia Pacific",
            "Latin America South": "Latin America - South",
            "Latin America North": "Latin America - North",
        }
        for ranking in response:
            if region := ranking_replace.get(ranking.region):
                ranking.region = region

    return response
