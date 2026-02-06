#!/bin/bash
set -e

until mysqladmin ping -h mysql-primary --silent; do
  sleep 1
done

mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "STOP REPLICA;" || true
mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "RESET REPLICA ALL;" || true
mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "CHANGE REPLICATION SOURCE TO SOURCE_HOST='mysql-primary', SOURCE_USER='repl', SOURCE_PASSWORD='repl_pass', SOURCE_AUTO_POSITION=1;"
mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "START REPLICA;"
