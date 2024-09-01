# rabbitmq.py
import pika
from django.conf import settings

def get_connection():
    try:
        credentials = pika.PlainCredentials('creato_admin', '629648767bee46535b7f829ee2f8ecd0')
        parameters = pika.ConnectionParameters('host.docker.internal', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        return connection
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Publish messages
def publish_message(queue, exchange, routing_key, message):
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    connection.close()


def publish_email_verification(message):
    publish_message(
        queue=settings.RABBITMQ_EMAIL_VERIFICATION_QUEUE,
        exchange=settings.RABBITMQ_EXCHANGE,
        routing_key=settings.RABBITMQ_EMAIL_VERIFICATION_ROUTING_KEY,
        message=message
    )

def publish_workspace_invite(message):
    publish_message(
        queue=settings.RABBITMQ_WORKSPACE_INVITE_QUEUE,
        exchange=settings.RABBITMQ_EXCHANGE,
        routing_key=settings.RABBITMQ_WORKSPACE_INVITE_ROUTING_KEY,
        message=message
    )

# Consume messages
def consume_messages(callback):
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)

    def wrapped_callback(ch, method, properties, body):
        callback(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=settings.RABBITMQ_QUEUE, on_message_callback=wrapped_callback)
    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

def consume_message(queue, callback):
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)

    def wrapped_callback(ch, method, properties, body):
        callback(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue, on_message_callback=wrapped_callback)
    print(f"Waiting for messages in {queue}. To exit press CTRL+C")
    channel.start_consuming()

def consume_email_verification(callback):
    consume_message(
        queue=settings.RABBITMQ_EMAIL_VERIFICATION_QUEUE,
        callback=callback
    )

def consume_workspace_invite(callback):
    consume_message(
        queue=settings.RABBITMQ_WORKSPACE_INVITE_QUEUE,
        callback=callback
    )