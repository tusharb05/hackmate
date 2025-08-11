import pika, json
from django.conf import settings
from django.core.files.storage import default_storage


def publish_user_created(user):
    params = pika.URLParameters(settings.RABBITMQ_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    ch.exchange_declare(settings.USER_EVENTS_EXCHANGE, exchange_type='topic', durable=True)
    print(user.profile_image.name)
    payload = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "profile_image": user.profile_image.name if user.profile_image else None
    }
    ch.basic_publish(
        exchange=settings.USER_EVENTS_EXCHANGE,
        routing_key=settings.USER_CREATED_ROUTING_KEY,
        body=json.dumps(payload),
        properties=pika.BasicProperties(content_type='application/json', delivery_mode=2)
    )
    conn.close()
