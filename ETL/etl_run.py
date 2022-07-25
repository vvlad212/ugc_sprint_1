import logging

from core import config
from pkg.clickhouse_operate import ClickHouse
from pkg.kafka_consumer import KafkaConsumerClient
from core.req_handler import create_backoff_hdlr

logger = logging.getLogger(__name__)
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
                if len(insert_list) == config.KAFKA_BATCH_SIZE:
                    consumer.paused()
                    logger.info("Kafka consumer paused")
                    clickhouse_operate.ch_insert(insert_values=insert_list)
                    insert_list.clear()
                    consumer.resume()
                    logger.info("Kafka consumer resumed")
                insert_list.append([*msg.key.decode("utf-8").split('_'), msg.value.decode("utf-8")])


if __name__ == '__main__':
    ETLProcessRunner.start_etl()
