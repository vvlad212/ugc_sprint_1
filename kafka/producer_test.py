from kafka import KafkaProducer
from time import sleep

producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

n = 0
while n < 1000:
    value = f'01:23:55.00000{n}'
    key = f'025c58cd-1b7e-43be-9ffb-8571a613579b_00000000-0000-0000-0000-000000000000'

    producer.send(

        topic='auth_views_labels',
        value=bytes(value, "utf-8"),
        key=bytes(key, "utf-8"),
    )
    n += 1

sleep(1)
