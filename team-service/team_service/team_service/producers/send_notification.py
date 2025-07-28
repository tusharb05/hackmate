import pika
import json
import os
from django.conf import settings


def publish_notification_event(message: dict):
    # Connect using the RabbitMQ URL from settings
    params = pika.URLParameters(settings.RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Declare exchange and queue from settings
    channel.exchange_declare(
        exchange=settings.NOTIFICATION_EXCHANGE,
        exchange_type='direct',
        durable=True
    )

    channel.queue_declare(queue=settings.NOTIFICATION_QUEUE, durable=True)

    channel.queue_bind(
        exchange=settings.NOTIFICATION_EXCHANGE,
        queue=settings.NOTIFICATION_QUEUE,
        routing_key=settings.NOTIFICATION_ROUTING_KEY
    )

    channel.basic_publish(
        exchange=settings.NOTIFICATION_EXCHANGE,
        routing_key=settings.NOTIFICATION_ROUTING_KEY,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2  # Make message persistent
        )
    )

    connection.close()
