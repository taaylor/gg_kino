from core.config import app_config
from sentence_transformers import SentenceTransformer

ai_model: SentenceTransformer | None = None


def get_ai_model() -> SentenceTransformer:
    global ai_model  # noqa: WPS420
    if ai_model is None:
        ai_model = SentenceTransformer(
            model_name_or_path=app_config.ai_model.name,
            truncate_dim=app_config.ai_model.truncate_dim,
        )
    return ai_model
