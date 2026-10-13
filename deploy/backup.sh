#!/bin/sh
# Backup diário do banco e dos anexos. Agende no cron da VM, por exemplo:
#   30 1 * * * /opt/erpworksys/deploy/backup.sh /backup/erp
# Copie a pasta de destino para fora da VM (NAS, outro servidor ou nuvem).
set -eu
DESTINO="${1:-/backup/erp}"
DIAS="${RETENCAO_DIAS:-30}"
DATA="$(date +%Y%m%d-%H%M)"
cd "$(dirname "$0")/.."
mkdir -p "$DESTINO"

docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$DESTINO/erp-$DATA.dump"
docker compose exec -T web tar -C /app -czf - media > "$DESTINO/media-$DATA.tar.gz"

find "$DESTINO" -name 'erp-*.dump' -mtime +"$DIAS" -delete
find "$DESTINO" -name 'media-*.tar.gz' -mtime +"$DIAS" -delete
echo "Backup concluído em $DESTINO ($DATA)"
