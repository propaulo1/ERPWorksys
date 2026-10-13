# Implantação no servidor Worksys

Ambiente-alvo: HP DL380 G7 com VMware ESXi 6.x, processador Xeon X5690 (sem AVX).

## 1. Criar a VM

- Sistema: **Ubuntu Server 24.04 LTS** (tipo de convidado no ESXi: "Ubuntu Linux (64-bit)").
  Não usar RHEL/AlmaLinux/Rocky 10: exigem AVX2 e não instalam nesse processador.
- Recursos iniciais: 4 vCPU, 8 GB de RAM, 100 GB de disco (thin provisioning).
- Rede com IP fixo e um nome DNS interno (ex.: `erp.worksys.local`).

## 2. Instalar Docker

```sh
sudo apt update && sudo apt install -y docker.io docker-compose-v2 git
sudo usermod -aG docker $USER   # sair e entrar de novo
```

## 3. Baixar e configurar

```sh
sudo mkdir -p /opt/erpworksys && sudo chown $USER /opt/erpworksys
git clone https://github.com/propaulo1/ERPWorksys.git /opt/erpworksys
cd /opt/erpworksys
cp .env.example .env
# edite o .env: DJANGO_SECRET_KEY (gere com: python3 -c "import secrets;print(secrets.token_urlsafe(50))"),
# DJANGO_ALLOWED_HOSTS, DJANGO_CSRF_TRUSTED_ORIGINS e POSTGRES_PASSWORD
```

Certificado HTTPS em `deploy/certs/erp.crt` e `deploy/certs/erp.key`
(certificado interno, ou Let's Encrypt se o ERP for publicado na internet).
Para um teste rápido, um autoassinado:

```sh
openssl req -x509 -newkey rsa:2048 -nodes -days 825 -subj "/CN=erp.worksys.local" \
  -keyout deploy/certs/erp.key -out deploy/certs/erp.crt
```

## 4. Subir

```sh
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

Acesse `https://erp.worksys.local`. Em **Administração > Empresas**, preencha os dados
reais das duas empresas (criadas com nomes provisórios "SN" e "LP"). Em
**Administração > Usuários**, cadastre os usuários, o perfil e as empresas de cada um.

## 5. Backup

```sh
sudo crontab -e
# 30 1 * * * /opt/erpworksys/deploy/backup.sh /backup/erp
```

Copie `/backup/erp` para fora da VM (NAS, outro servidor ou nuvem) e teste a
restauração periodicamente:

```sh
docker compose exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean' < /backup/erp/erp-AAAAMMDD-HHMM.dump
```

## 6. Atualizar

Tire um snapshot da VM no ESXi e depois:

```sh
cd /opt/erpworksys && git pull && docker compose up -d --build
```

As migrações do banco rodam automaticamente na inicialização do container `web`.
