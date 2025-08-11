import pika, json, os, django

import pika, json, os, django, time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "team_service.settings")
django.setup()

from teams.models import CustomUser
from django.conf import settings


def connect_to_rabbitmq(params, retries=5, delay=5):
    for attempt in range(1, retries + 1):
        try:
            return pika.BlockingConnection(params)
        except pika.exceptions.AMQPConnectionError as e:
            print(f"[!] RabbitMQ connection failed (attempt {attempt}/{retries}). Retrying in {delay}s...")
            time.sleep(delay)
    raise Exception("[x] Could not connect to RabbitMQ after multiple retries.")


def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"\n[✓] Received user.created event:\n{json.dumps(data, indent=2)}\n")
    print(data)
    print("\n\n\n\n\n\n\n")
    # Upsert user by primary key
    CustomUser.objects.update_or_create(
        id=data["id"],
        defaults={
            "email": data["email"],
            "full_name": data["full_name"],
            "profile_image": data.get("profile_image")
        }
    )

    ch.basic_ack(delivery_tag=method.delivery_tag)


def run_consumer():
    params = pika.URLParameters(settings.RABBITMQ_URL)
    connection = connect_to_rabbitmq(params)
    channel = connection.channel()

    channel.exchange_declare(settings.USER_EVENTS_EXCHANGE, exchange_type='topic', durable=True)
    channel.queue_declare(settings.TEAM_SERVICE_QUEUE, durable=True)
    channel.queue_bind(
        queue=settings.TEAM_SERVICE_QUEUE,
        exchange=settings.USER_EVENTS_EXCHANGE,
        routing_key=settings.USER_CREATED_ROUTING_KEY
    )

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.TEAM_SERVICE_QUEUE, on_message_callback=callback)

    print(" [*] Waiting for user.created events. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    run_consumer()
