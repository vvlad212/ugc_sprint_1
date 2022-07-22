from kafka import KafkaConsumer
from clickhouse.ETL.clickhouse_operate import ClickHouse


class MsgConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'auth_views_labels',
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            bootstrap_servers=['localhost:9092'],
            group_id='echo-messages-to-stdout',
            consumer_timeout_ms=5000,
        )
        self.insert_list = []
        self.clickhouse_operate = ClickHouse()

    def start_etl(self):
        while True:
            for msg in self.consumer:
                try:
                    self.consumer.commit()
                except :
                    pass
                    # TODO сделать логгер и какой-то обработчик
                    # self.consumer.close()  # Останавливаем клиента Kafka
                    # self.pool.close()
                    return
                if len(self.insert_list) == 100:
                    self.consumer.paused()
                    self.clickhouse_operate.ch_insert(insert_values=self.insert_list)
                    self.insert_list.clear()
                    self.consumer.resume()
                self.insert_list.append([*msg.key.decode("utf-8").split('_'), msg.value.decode("utf-8")])
                print(msg.value)


if __name__ == '__main__':
    cons = MsgConsumer()
    cons.start_etl()
