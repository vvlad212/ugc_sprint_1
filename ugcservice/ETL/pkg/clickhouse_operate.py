import logging
import backoff

from clickhouse_driver import Client
from clickhouse_driver.errors import NetworkError, CannotParseUuidError, Error
from ugcservice.ETL.pkg.req_handler import create_backoff_hdlr

logger = logging.getLogger(__name__)

BACKOFF_MAX_TIME = 60  # sec
back_off_hdlr = create_backoff_hdlr(logger)


class ClickHouse:
    @backoff.on_exception(
        backoff.fibo,
        exception=(ConnectionRefusedError, NetworkError,Error, ConnectionError,BaseException),
        max_time=BACKOFF_MAX_TIME,
        on_backoff=back_off_hdlr,
    )
    def connection(self):

        client = Client(host='127.0.0.1')
        try:
            client.connection.connect()
            logger.info('Connected to CLICKHOUSE')
            return client
        except Exception as ex:
            logger.error(f'Connection refused error CLICKHOUSE {ex}')
            raise ConnectionRefusedError


    @backoff.on_exception(
        backoff.fibo,
        exception=(NetworkError, CannotParseUuidError),
        max_time=BACKOFF_MAX_TIME,
        on_backoff=back_off_hdlr,
    )
    def ch_insert(self, insert_values: list):
        try:
            client = self.connection()
            client.execute(f"INSERT INTO default.views (film_id, user_id, timestamp) VALUES ",
                           (tuple(row) for row in insert_values))
            logger.info(f'{len(insert_values)} added in CLICKHOUSE.')
        except Exception as ex:
            logger.error(f'Query error CLICKHOUSE {ex}')
            raise Error
