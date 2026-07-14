#!/bin/sh
set -e

cat > /tmp/odoo.conf <<EOF
[options]
addons_path = ./myaddons,./odoo/addons
db_host = ${DB_HOST}
db_port = ${DB_PORT}
db_user = ${DB_USER}
db_password = ${DB_PASSWORD}
db_name = ${DB_NAME}
dbfilter = ^${DB_NAME}$
admin_passwd = ${ADMIN_PASSWD}
list_db = False
workers = 1
max_cron_threads = 1
EOF

python ./odoo/odoo-bin -c /tmp/odoo.conf --http-port=${PORT:-8069}
