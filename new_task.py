import pika


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    message =  "AAAA"
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        ))
    print(" Sent %r" % message)
    connection.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()