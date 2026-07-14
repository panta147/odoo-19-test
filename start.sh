#!/bin/sh
set -e

if [ -d ./odoo ]; then
  ODOO_ROOT=./odoo
elif [ -d ./odoo/odoo ]; then
  ODOO_ROOT=./odoo/odoo
else
  echo "Odoo source directory not found" >&2
  exit 1
fi

if [ -f "$ODOO_ROOT/odoo-bin" ]; then
  ODOO_BIN="$ODOO_ROOT/odoo-bin"
else
  echo "Odoo startup script not found in $ODOO_ROOT" >&2
  exit 1
fi

cat > /tmp/odoo.conf <<EOF
[options]
addons_path = ./myaddons,$ODOO_ROOT/addons
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

python "$ODOO_BIN" -c /tmp/odoo.conf --http-port=${PORT:-8069}
