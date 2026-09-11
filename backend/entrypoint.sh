#!/bin/sh
set -eu
# Una única réplica de API en este Compose. Para escalar, migrar en un job separado.
alembic upgrade head
exec "$@"
