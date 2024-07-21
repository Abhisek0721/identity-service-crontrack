# rabbitmq.py
import pika
from django.conf import settings

def get_connection():
    try:
        credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(settings.RABBITMQ_HOST, settings.RABBITMQ_PORT, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        return connection
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def publish_message(message):
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE,  durable=True)
    channel.basic_publish(
        exchange=settings.RABBITMQ_EXCHANGE,
        routing_key=settings.RABBITMQ_ROUTING_KEY,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    connection.close()

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
