import time
import multiprocessing.pool as mp_pool
from kafka import KafkaConsumer
from clickhouse.ETL.clickhouse_operate import ClickHouse
import datetime


class LimitedMultiprocessingPool(mp_pool.Pool):
    def get_pool_cache_size(self):
        return len(self._cache)


class MsgConsumer:
    def __init__(self):
        # Функция для обработки сообщения в дочернем процессе
        # self.proc_fun = proc_fun
        # Клиент для чтения сообщений из Kafka
        self.consumer = KafkaConsumer(
            'auth_views_labels',
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            bootstrap_servers=['localhost:9092'],
            group_id='echo-messages-to-stdout',
            consumer_timeout_ms=5000,
        )
        # Лимит на количество сообщений, единовременно находящихся в пуле
        self.pool_cache_limit = 2
        # Флаг управляемой остановки приложения
        self.stop_processing = False
        # Пул обработчиков сообщений
        self.pool = LimitedMultiprocessingPool(processes=2)
        self.insert_list = []
        self.clickhouse_operate = ClickHouse()

    def set_stop_processing(self):
        self.stop_processing = True

    def handle_pool_cache_excess(self):
        while self.pool.get_pool_cache_size() >= self.pool_cache_limit:
            time.sleep(5)

    def stop(self):
        self.consumer.close()  # Останавливаем клиента Kafka
        self.pool.close()

    def main_loop(self):
        while not self.stop_processing:
            for msg in self.consumer:
                if self.stop_processing:
                    self.stop()
                    return
                try:
                    self.handle_pool_cache_excess()
                    self.consumer.commit()
                except:
                    self.stop()
                    return
                if len(self.insert_list) == 100:
                    pass
                    self.clickhouse_operate.ch_insert(insert_values=self.insert_list)
                    self.insert_list.clear()
                self.insert_list.append([*msg.key.decode("utf-8").split('_'), 12657128])#msg.value.decode("utf-8")])
                print(msg.value)


if __name__ == '__main__':
    cons = MsgConsumer()
    cons.main_loop()
