import logging
import backoff

from clickhouse_driver import Client
from clickhouse_driver.errors import NetworkError, CannotParseUuidError, Error
from pkg.req_handler import create_backoff_hdlr

logger = logging.getLogger(__name__)

BACKOFF_MAX_TIME = 60  # sec
back_off_hdlr = create_backoff_hdlr(logger)
CLICKHOUSE_HOST = 'clickhouse-node1'
CLICKHOUSE_DATABASE = 'default'
CLICKHOUSE_TABLE = 'views'
query_auth_insert = f"INSERT INTO {CLICKHOUSE_DATABASE}.{CLICKHOUSE_TABLE} (film_id, user_id, timestamp) VALUES"


class ClickHouse:
    @backoff.on_exception(
        backoff.fibo,
        exception=(ConnectionRefusedError, Error),
        max_time=BACKOFF_MAX_TIME,
        on_backoff=back_off_hdlr,
    )
    def connection(self):

        client = Client(host=CLICKHOUSE_HOST)
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
            logger.info(f'Start insert in CLICKHOUSE.')
            client.execute(query_auth_insert, (tuple(row) for row in insert_values))
            logger.info(f'{len(insert_values)} row(s) added in CLICKHOUSE.')
        except Exception as ex:
            logger.error(f'Query error CLICKHOUSE {ex}')
            raise Error
