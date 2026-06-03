from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_analytics():
    return {
        "total_reviews": 0,
        "security_score_avg": 0,
        "issues_found": 0
    }
