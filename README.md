# ATOM — Your day, connected

Mobile-friendly Django / Bootstrap dashboard for supermarket discounts, weather and transport in Auckland and Wellington.

## Run locally

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

Development uses SQLite when DATABASE_URL is absent. For PostgreSQL set DATABASE_URL (see .env.example) before migrating. Environment files are examples; export variables yourself. No default user or password is created. Register through /signup/; create an administrator with `python manage.py createsuperuser`.

## Included

- Search and category filters, responsive deal cards, persisted watchlists and user accounts.
- In-app notifications when a watched product's price falls below its previous price and regular price. Update products through Django admin using save(); bulk SQL updates bypass signals.
- Email price notifications: `python manage.py send_alerts`. Console mail by default. Configure SMTP and schedule this command periodically. Delivery retries may duplicate email after a worker crash; use a transactional delivery queue for production.
- City-specific weather from Open-Meteo (10 minute cache). Unavailable requests show explicitly labelled sample conditions. Strong wind advisory appears at 50 km/h. These are weather conditions, not official emergency warnings.
- Auckland and Wellington sample timetables and service notices; manage notices through admin.

## Data integration boundaries

Retailer inventory, prices, transport departures and notices are **demo data**, not live feeds. There is no universal supermarket API: connect licensed retailer feeds, then normalize products and call model save() for price changes. Connect Auckland Transport and Metlink licensed APIs or GTFS/GTFS-RT feeds for real timetables and disruptions. Provider credentials and permitted usage must be configured before those integrations. Weather is live when Open-Meteo is reachable; consult its terms and attribution before production use. Registering creates local weather/transport alert preferences, adjustable under Notifications. New service notices notify subscribers for that city. Schedule `python manage.py check_weather` every 10 minutes to create high-wind advisories (one per city per day), and `python manage.py send_alerts` to deliver queued emails. Run `python manage.py run_alert_worker` as a separate development process to check weather and dispatch queued emails every 10 minutes. For production, use a supervised scheduler and reliable delivery queue. Official warning ingestion and browser push are not implemented. Notification delivery currently covers product prices in-app and via configured email; browser push is future work.

## Validate

```sh
.venv/bin/python manage.py check
.venv/bin/python manage.py test
```

## PostgreSQL deployment

Docker Compose files are organized into a shared stack (`compose.yaml`), private HTTP testing (`compose.test.yaml`), and public HTTPS test hosting (`compose.host.yaml`). See [test hosting instructions](deploy/README.md) for environment variables, startup, administration, backups and validation.

For higher traffic, use PostgreSQL pooling, shared Redis caching, Celery workers/beat for feed ingestion and notifications, and multiple stateless Gunicorn instances behind a load balancer. This starter has not been load-tested; its cache is per-process and its email command should have one scheduled worker. Bootstrap is loaded from jsDelivr and fonts from Google Fonts; application styling works without Bootstrap, with system font fallbacks.

## Cloud development helper

With Docker available, `./scripts/dev.sh setup` starts a local PostgreSQL 17 container, migrates and seeds the demo. `./scripts/dev.sh` also starts Django on port 8000. Database credentials are randomly generated locally in an ignored permission-restricted `.local-db.env`; never commit it. Source this file before running management commands against that PostgreSQL database. The named Docker volume retains data on this machine; back it up separately, and recreate processes in future cloud tasks.
