import os

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query

load_dotenv()


TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = os.getenv("TMDB_BASE_URL")


router = APIRouter(prefix="/movies", tags=["Movies"])

# 1. ?api_key=[] (Query Paramter)
# 2. Authorization: Bearer


_USE_BEARER = TMDB_API_KEY.startswith("eyJ")
print("TMDB_API_KEY:", repr(TMDB_API_KEY))
print("USE_BEARER:", _USE_BEARER)


async def tmdb_get(path: str, params: dict | None = None) -> dict:
    if not TMDB_API_KEY:
        raise HTTPException(status_code=500, detail="TMDB_API_KEY is not set in .env")

    base_params: dict = {"language": "en-US"}
    headers: dict = {}

    if _USE_BEARER:
        headers["Authorization"] = f"Bearer {TMDB_API_KEY}"
    else:
        base_params["api_key"] = TMDB_API_KEY

    if params:
        base_params.update(params)

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{TMDB_BASE_URL}{path}", params=base_params, headers=headers, timeout=10
        )
    if resp.status_code == 401:
        print(resp.text)
        raise HTTPException(
            status_code=500,
            detail="TMDB rejected the api key. Please chnage your api key",
        )
    if resp.status_code != 200:
        print(resp.text)
        raise HTTPException(status_code=resp.status_code, detail="TMDB request failed")
    return resp.json()


@router.get("/popular")
async def get_popular_movies(
    page: int = Query(default=1, ge=1, le=500, description="Page number"),
):
    """ "GET /movie/popular?page=1 - paginated page"""
    return await tmdb_get("/movie/popular", {"page": page})


@router.get("/trending")
async def get_trending_movies(
    time_window: str=Query(default="week" , description="day or week"),
):
    """ "GET /movie/popular?page=1 - paginated page"""
    if time_window not in ("day", "week"):
        raise HTTPException(status_code=400, detail="Time Window must be day or week")
    return await tmdb_get(f"/trending/movie/{time_window}")


@router.get("/genres")
async def get_genres():
    return await tmdb_get("/genres/movie/list")


@router.get("/search")
async def search_movies(
    query: str = Query(description="Movies title to search for"),
    page: int = Query(default=1, ge=1, description="Page number"),
):
    return await tmdb_get("/search/movie", {"query":query, "page":page})

@router.get("/{movie_id}")
async def get_movie_detail(movie_id: int):
    return await tmdb_get(f"/movie/{movie_id}", {"append_to_response": "credits, videos"})
