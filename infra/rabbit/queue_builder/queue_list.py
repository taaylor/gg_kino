import os

queues: set[str] = set()

queues.add(os.getenv("RABBITMQ_REVIEW_LIKE_QUEUE", ""))
queues.add(os.getenv("RABBITMQ_REGISTERED_QUEUE", ""))
queues.add(os.getenv("RABBITMQ_MANAGER_MAILING_QUEUE", ""))
queues.add(os.getenv("RABBITMQ_AUTO_MAILING_QUEUE", ""))
