from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def example_root():
    a = 1
    return {"message": "example root"}
