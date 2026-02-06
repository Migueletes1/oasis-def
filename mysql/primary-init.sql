CREATE USER IF NOT EXISTS 'repl'@'%' IDENTIFIED BY 'repl_pass';
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'repl'@'%';

CREATE USER IF NOT EXISTS 'proxysql_monitor'@'%' IDENTIFIED BY 'proxysql_monitor_pass';
GRANT REPLICATION CLIENT, PROCESS, SUPER, SELECT ON *.* TO 'proxysql_monitor'@'%';

CREATE USER IF NOT EXISTS 'orchestrator'@'%' IDENTIFIED BY 'orchestrator_pass';
GRANT SUPER, PROCESS, REPLICATION SLAVE, REPLICATION CLIENT, RELOAD, SHOW DATABASES ON *.* TO 'orchestrator'@'%';
GRANT SELECT ON mysql.slave_master_info TO 'orchestrator'@'%';
GRANT SELECT ON mysql.slave_relay_log_info TO 'orchestrator'@'%';
GRANT SELECT ON mysql.slave_worker_info TO 'orchestrator'@'%';
FLUSH PRIVILEGES;
