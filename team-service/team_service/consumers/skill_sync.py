import pika, json, os, django, time

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "team_service.settings")
django.setup()

from teams.models import Skill
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
    print(f"\n[✓] Received skill.created event:\n{json.dumps(data, indent=2)}\n")

    Skill.objects.update_or_create(
        id=data["id"],
        defaults={"skill": data["skill"]}
    )

    ch.basic_ack(delivery_tag=method.delivery_tag)


def run_skill_consumer():
    params = pika.URLParameters(settings.RABBITMQ_URL)
    conn = connect_to_rabbitmq(params)
    ch = conn.channel()

    ch.exchange_declare(exchange=settings.SKILL_EVENTS_EXCHANGE, exchange_type='topic', durable=True)
    ch.queue_declare(queue=settings.TEAM_SKILL_QUEUE, durable=True)
    ch.queue_bind(queue=settings.TEAM_SKILL_QUEUE, exchange=settings.SKILL_EVENTS_EXCHANGE, routing_key=settings.SKILL_CREATED_ROUTING_KEY)

    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue=settings.TEAM_SKILL_QUEUE, on_message_callback=callback)

    print(" [*] Waiting for skill.created events. To exit press CTRL+C")
    ch.start_consuming()

if __name__ == "__main__":
    run_skill_consumer()
