--node1
CREATE DATABASE IF NOT EXISTS replica;
CREATE DATABASE IF NOT EXISTS shard;

CREATE TABLE shard.views (event_time DEFAULT toDateTime(now()), film_id UUID,user_id UUID, timestamp String) Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/views', 'replica_1') PARTITION BY toYYYYMMDD(event_time) order by event_time;
CREATE TABLE IF NOT EXISTS replica.views (event_time DEFAULT toDateTime(now()), film_id UUID,user_id UUID, timestamp String) Engine=ReplicatedMergeTree('/clickhouse/tables/shard2/views', 'replica_2') PARTITION BY toYYYYMMDD(event_time) order by event_time;
CREATE TABLE IF NOT EXISTS default.views (event_time DEFAULT toDateTime(now()), film_id UUID,user_id UUID, timestamp String) ENGINE = Distributed('company_cluster', '', views, rand());

--node3
CREATE DATABASE IF NOT EXISTS replica;
CREATE DATABASE IF NOT EXISTS shard;

CREATE TABLE shard.views (event_time DEFAULT toDateTime(now()), film_id UUID,user_id UUID, timestamp String) Engine=ReplicatedMergeTree('/clickhouse/tables/shard2/views', 'replica_1') PARTITION BY toYYYYMMDD(event_time) order by event_time;
CREATE TABLE replica.views (event_time DEFAULT toDateTime(now()), film_id UUID,user_id UUID, timestamp String) Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/views', 'replica_2') PARTITION BY toYYYYMMDD(event_time) order by event_time;
CREATE TABLE default.views (event_time DEFAULT toDateTime(now()), film_id UUID,user_id UUID, timestamp String) ENGINE = Distributed('company_cluster', '', views, rand());

--node5
CREATE DATABASE IF NOT EXISTS replica;
CREATE DATABASE IF NOT EXISTS shard;

CREATE TABLE IF NOT EXISTS shard.views (event_time DEFAULT toDateTime(now()), film_id UUID,user_id UUID, timestamp String) Engine=ReplicatedMergeTree('/clickhouse/tables/shard3/views', 'replica_1') PARTITION BY toYYYYMMDD(event_time) order by event_time;
CREATE TABLE IF NOT EXISTS replica.views (event_time DEFAULT toDateTime(now()), film_id UUID,user_id UUID, timestamp String) Engine=ReplicatedMergeTree('/clickhouse/tables/shard3/views', 'replica_3') PARTITION BY toYYYYMMDD(event_time) order by event_time;
CREATE TABLE IF NOT EXISTS default.views (event_time DEFAULT toDateTime(now()), film_id UUID,user_id UUID, timestamp String) ENGINE = Distributed('company_cluster', '', views, rand());
