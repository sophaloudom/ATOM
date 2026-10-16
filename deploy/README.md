# ATOM test hosting

Requires Docker Engine and Docker Compose v2. This stack runs PostgreSQL 17, a migration/seed job, Gunicorn, and one periodic alert worker. Do not scale the worker: it is a simple single-process dispatcher, without distributed locking. Services restart after a host reboot if Docker starts automatically. The setup job runs on stack startup before web and worker.

## Private HTTP test environment

Run from the repository root:

```sh
cp deploy/test.env.example deploy/test.env
chmod 600 deploy/test.env
# Edit both secret placeholders in deploy/test.env using different random values.
# Generate each with: python -c "import secrets; print(secrets.token_hex(32))"
docker compose --env-file deploy/test.env -f compose.yaml -f compose.test.yaml up --build -d --wait
```

Open port 8080 on the Docker host locally. For a remote server, use `ssh -L 8080:127.0.0.1:8080 user@server` and access it through the tunnel. HTTP mode deliberately disables secure-only cookies so sign-in works; its default port binding is loopback only. Keep this mode private. `TEST_PORT` changes the port; `TEST_BIND` changes the bind address. Add the hostname to `DJANGO_ALLOWED_HOSTS` if accessing by another hostname. The sample environment seeds demo data; set SEED_DEMO=0 for an empty inventory. No default admin account is created.

The .env file is loaded explicitly by Compose; Django does not auto-read it. Use URL-safe hex characters for POSTGRES_PASSWORD because it is interpolated into DATABASE_URL. Keep deploy/test.env out of source control. In restricted cloud shells where Docker cannot write its default config, prefix Docker commands with `DOCKER_CONFIG=/tmp/atom-docker`.

## Public test environment with HTTPS

Point a real DNS domain to your server, allow inbound TCP 80 and 443, and add `SITE_DOMAIN=your-test-domain.example` to deploy/test.env. Start using the HTTPS override **instead of** the HTTP override:

```sh
docker compose --env-file deploy/test.env -f compose.yaml -f compose.host.yaml up --build -d --wait
```

Caddy obtains and renews certificates automatically. This requires outbound access to certificate authorities. Only Caddy publishes ports; Django and PostgreSQL remain on the private Compose network. Secure cookies stay enabled, and Django trusts forwarded HTTPS headers only behind this proxy. Do not combine the test and host override files. If switching modes on the same machine, run `down` with the old file combination first (without `-v`). DNS, certificate issuance and remote reachability must be checked on your actual host; local Compose validation does not prove them.

## Manage and validate

Use the same `--env-file` and `-f` flags for every command; replace compose.test.yaml with compose.host.yaml for HTTPS:

```sh
docker compose --env-file deploy/test.env -f compose.yaml -f compose.test.yaml ps -a
docker compose --env-file deploy/test.env -f compose.yaml -f compose.test.yaml logs --tail=100 web worker setup
docker compose --env-file deploy/test.env -f compose.yaml -f compose.test.yaml exec web python manage.py createsuperuser
docker compose --env-file deploy/test.env -f compose.yaml -f compose.test.yaml exec web python manage.py test
curl --fail http://127.0.0.1:8080/healthz/
docker compose --env-file deploy/test.env -f compose.yaml -f compose.test.yaml down
```

Health should return `{"status": "ok"}`; it checks PostgreSQL connectivity. The web healthcheck does not contact weather services. Check the dashboard, sign-up, sign-in, watchlist and Notifications preferences too. The worker checks weather and email every 10 minutes. SMTP defaults to console mail: configure the EMAIL_* values for real delivery. Retailer and transport data remain samples. Live weather requires outbound HTTPS to api.open-meteo.com.

## Update, backup and restore

Before an update, back up the database, then run the same `up --build -d --wait` command. Inspect the setup service logs for migrations. Migration failure prevents the new web and worker from starting. Compose does not guarantee zero-downtime releases or automatically roll back schema changes.

```sh
mkdir -p backups
chmod 700 backups
docker compose --env-file deploy/test.env -f compose.yaml -f compose.test.yaml exec -T db pg_dump -U atom -d atom -Fc > backups/atom.dump
# Restore only into a separate test database, or after stopping web and worker:
# docker compose ... exec -T db pg_restore -U atom -d atom --clean --if-exists < backups/atom.dump
```

`down` preserves named database and certificate volumes. `down -v` destroys them. Changing POSTGRES_PASSWORD in the environment file does not change an existing PostgreSQL user's password; coordinate database password rotation rather than deleting data. This stack is intended for testing; backups, monitoring, delivery guarantees and capacity testing need further work for production.

## Cloud build without Docker DNS access

The onboarding sandbox can download packages on its host while Docker build containers lack DNS/proxy access. An optional offline build uses wheels fetched through the host's normal verified HTTPS package installer:

```sh
# Run on the same architecture and Python 3.12 as the target image.
.venv/bin/pip download --only-binary=:all: -r requirements.txt -d deploy/wheels
DOCKER_CONFIG=/tmp/atom-docker docker compose --env-file deploy/test.env -f compose.yaml -f compose.test.yaml build --build-arg OFFLINE_WHEELS=1
DOCKER_CONFIG=/tmp/atom-docker docker compose --env-file deploy/test.env -f compose.yaml -f compose.test.yaml up --no-build -d --wait
```

Wheels are ignored by Git. The normal build downloads from the package registry; OFFLINE_WHEELS=1 strictly installs from the wheel directory and fails if required wheels are missing. Do not disable TLS verification to work around a proxy problem. Use wheels for the target platform if building elsewhere.
