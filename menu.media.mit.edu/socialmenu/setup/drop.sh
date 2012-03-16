#!/bin/sh

db=SocialMenu

psql -t -d $db -U otnpostgres -c "SELECT 'DROP TABLE ' || n.nspname || '.' || c.relname || ' CASCADE;' FROM pg_catalog.pg_class AS c LEFT JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace WHERE relkind = 'r' AND n.nspname NOT IN ('pg_catalog', 'pg_toast') AND pg_catalog.pg_table_is_visible(c.oid)" >/tmp/droptables

psql -d $db -U otnpostgres -f /tmp/droptables 


