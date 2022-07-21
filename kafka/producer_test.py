from kafka import KafkaProducer
from time import sleep

producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

n = 0
while n < 105:
    value = f'01:23:55.00{n}'
    key = f'025c58cd-1b7e-43be-9ffb-8571a613579b_025c58cd-1b7e-43be-9ffb-8571a613579b'

    producer.send(

        topic='auth_views_labels',
        value=bytes(value, "utf-8"),
        key=bytes(key, "utf-8"),
    )
    n += 1

sleep(1)
