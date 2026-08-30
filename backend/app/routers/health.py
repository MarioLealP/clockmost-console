from fastapi import APIRouter

router = APIRouter(tags=["meta"])


@router.get("/api/health")
async def health() -> dict[str, bool]:
    return {"ok": True}
