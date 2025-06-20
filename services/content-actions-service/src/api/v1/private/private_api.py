from fastapi import APIRouter

router = APIRouter()


@router.get(path="/glitchtip-test", summary="Endpoint для тестирования логов в GlitchTip")
async def test_glitch():
    return 1 / 0  # noqa: WPS344
