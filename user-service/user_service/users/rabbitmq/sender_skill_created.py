import pika, json
from django.conf import settings

def publish_skill_created_event(skill):
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()

    channel.exchange_declare(exchange=settings.SKILL_EVENTS_EXCHANGE, exchange_type='topic', durable=True)

    event_data = {
        "id": skill.id,
        "skill": skill.skill
    }

    channel.basic_publish(
        exchange=settings.SKILL_EVENTS_EXCHANGE,
        routing_key=settings.SKILL_CREATED_ROUTING_KEY,
        body=json.dumps(event_data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        )
    )
    connection.close()
