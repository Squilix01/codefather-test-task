from taskiq_aio_pika import AioPikaBroker
from app.core.config import Config

config = Config()


broker = AioPikaBroker(config.rabbitmq.rabbitmq)
