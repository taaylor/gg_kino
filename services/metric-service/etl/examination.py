import json
import random
import uuid
from copy import deepcopy

from config import kafka_config
from kafka import KafkaProducer

template_payload = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_session": "123e4567-e89b-12d3-a456-426614174000",
    "user_uuid": "987e6543-e21b-12d3-a456-426614174001",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "film_uuid": "456e7890-e21b-12d3-a456-426614174002",
    "event_type": "comment",
    "message_event": "User added a comment on the film",
    "event_params": {"count_words": "5", "language": "en"},
    "event_timestamp": "2025-06-03 15:24:00",
    "user_timestamp": "2025-06-03T15:24:00+00:00",
}

producer = KafkaProducer(bootstrap_servers=["localhost:9094"])

for i in range(10000):
    topic = random.choice(kafka_config.topics)
    message = deepcopy(template_payload)
    message["id"] = str(uuid.uuid4())
    message["user_session"] = str(uuid.uuid4())
    message["user_uuid"] = str(uuid.uuid4())
    message["event_type"] = random.choice(
        [
            "comment",
            "like",
            "subscribe",
        ]
    )
    try:
        producer.send(
            topic=topic,
            value=json.dumps(message).encode("utf-8"),
        )
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

producer.flush()
producer.close()
print("Все сообщения отправлены")
