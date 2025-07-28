import json
import os
import time
import pika
import django

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notification_service.settings")
django.setup()

from django.conf import settings
from notify.models import Notification  



def connect_to_rabbitmq(params, retries=5, delay=5):
    for attempt in range(1, retries + 1):
        try:
            return pika.BlockingConnection(params)
        except pika.exceptions.AMQPConnectionError as e:
            print(f"[!] RabbitMQ connection failed (attempt {attempt}/{retries}). Retrying in {delay}s...")
            time.sleep(delay)
    raise Exception("[x] Could not connect to RabbitMQ after multiple retries.")


def save_notification(data):
    notification = Notification.objects.create(
        user_id=data["user_id"],
        team_application_id=data["team_application_id"],
        message=data["message"],
        type=data["type"]
    )
    print(f"[✓] Notification saved for user {notification.user_id}")
    return notification


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f"[→] Received event: {data}")

        save_notification(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[x] Error handling notification event: {e}")


def run_notification_consumer():
    params = pika.URLParameters(settings.RABBITMQ_URL)
    conn = connect_to_rabbitmq(params)
    ch = conn.channel()

    ch.exchange_declare(exchange=settings.NOTIFICATION_EXCHANGE, exchange_type='direct', durable=True)
    ch.queue_declare(queue=settings.NOTIFICATION_QUEUE, durable=True)
    ch.queue_bind(exchange=settings.NOTIFICATION_EXCHANGE, queue=settings.NOTIFICATION_QUEUE, routing_key=settings.NOTIFICATION_ROUTING_KEY)

    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue=settings.NOTIFICATION_QUEUE, on_message_callback=callback)

    print(" [*] Waiting for notification events. To exit press CTRL+C")
    ch.start_consuming()


if __name__ == "__main__":
    run_notification_consumer()
