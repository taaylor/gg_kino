import base64
import json


def decode_jwt_payload(jwt_token: str) -> dict:
    try:
        parts = jwt_token.split(".")
        if len(parts) != 3:
            raise ValueError("Невалидный JWT токен")
        payload_b64 = parts[1]
        # добавляем padding (заглушку) если payload не кратен 4
        padding = "=" * (-len(payload_b64) % 4)
        payload_b64 += padding
        payload_decoded_bytes = base64.urlsafe_b64decode(payload_b64)
        return json.loads(payload_decoded_bytes.decode("utf-8"))
    except Exception as e:
        print("Ошибка декодирования JWT:", e)
        return {}
