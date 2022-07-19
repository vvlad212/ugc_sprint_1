from kafka import KafkaProducer
from time import sleep


producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

producer.send(
    topic='auth_views_labels',
    value=b'16110399314',
    key=b'500271+tt0120338',
)

sleep(1)