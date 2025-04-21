from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def example_root():
    a = 1  # noqa: F841
    return {"message": "example root"}
