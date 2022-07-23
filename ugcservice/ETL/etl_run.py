import logging
# from logging import config as logging_config
from pkg.clickhouse_operate import ClickHouse
from pkg.kafka_consumer import KafkaConsumerClient
# from pkg.logger import LOGGING
from pkg.req_handler import create_backoff_hdlr

logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

BACKOFF_MAX_TIME = 60  # sec
batch_size = 10
back_off_hdlr = create_backoff_hdlr(logger)


class ETLProcessRunner:

    @classmethod
    def start_etl(cls):
        logger.info('ETL process has been started.')
        insert_list = []
        clickhouse_operate = ClickHouse()
        kafka_consumer = KafkaConsumerClient()
        consumer = kafka_consumer.create_consumer()
        while True:
            for msg in consumer:
                try:
                    consumer.commit()
                except Exception as ex:
                    logger.error(f'Error kafka consumer {ex}')
                    if insert_list:
                        clickhouse_operate.ch_insert(insert_values=insert_list)
                        insert_list.clear()
                    consumer.close()
                    consumer = kafka_consumer.create_consumer()
                    continue
                if len(insert_list) == batch_size:
                    consumer.paused()
                    clickhouse_operate.ch_insert(insert_values=insert_list)
                    insert_list.clear()
                    consumer.resume()
                insert_list.append([*msg.key.decode("utf-8").split('_'), msg.value.decode("utf-8")])


if __name__ == '__main__':
    ETLProcessRunner.start_etl()
