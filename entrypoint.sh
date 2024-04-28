#!/bin/bash

set -e

# Definir valores fijos para la conexión a la base de datos
HOST="172.31.17.230"  # Reemplazar con el nombre del host de la base de datos PostgreSQL
PORT="5432"             # Puerto de la base de datos PostgreSQL
USER="odoo"             # Usuario de la base de datos PostgreSQL
PASSWORD="odoo"         # Contraseña de la base de datos PostgreSQL

# Agregar los valores al array de argumentos de la base de datos
DB_ARGS=("--db_host" "$HOST" "--db_port" "$PORT" "--db_user" "$USER" "--db_password" "$PASSWORD")


case "$1" in
    -- | odoo)
        shift
        if [[ "$1" == "scaffold" ]] ; then
            exec odoo "$@"
        else
            exec odoo "$@" "${DB_ARGS[@]}"
        fi
        ;;
    -*)
        exec odoo "$@" "${DB_ARGS[@]}"
        ;;
    *)
        exec "$@"
esac

exit 1