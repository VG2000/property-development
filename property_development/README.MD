# To run in dev:
docker compose -f docker-compose.dev.yml up --build -d

# To make migrations
python manage.py makemigrations --settings=property_development.settings.dev

# To run in prod:
docker compose -f docker-compose.prod.yml up --build -d

# To check the logs on Lightsail
docker compose -f docker-compose.prod.yml logs --tail=100

# To seed data in prod SSH into container
docker compose -f docker-compose.prod.yml exec web bash
# Then run one by one eg...
# Land registry
python manage.py import_lr_data /data/ppd_data_conwy.csv

# scp command to copy files from local into Lightsail
# CSV data files
scp -C -i ~/.ssh/LightsailDefaultKey-eu-west-2.pem \
  ~/Projects/Property-Development/data/*.csv \
  ubuntu@3.10.241.170:/home/ubuntu/property-development/property-development/data/
# Media pdfs
scp -C -i ~/.ssh/LightsailDefaultKey-eu-west-2.pem \
  ~/Projects/Property-Development/property_development/*.csv \
  ubuntu@3.10.241.170:/home/ubuntu/property-development/property-development/data/

### To seed data in development
# Land registry data
docker compose -f docker-compose.dev.yml exec web python manage.py import_lr_data /data/ppd_data_conwy.csv
docker compose -f docker-compose.dev.yml exec web python manage.py import_lr_data /data/ppd_data_gwynedd.csv
docker compose -f docker-compose.dev.yml exec web python manage.py import_lr_data /data/ppd_data_denbighshire.csv
docker compose -f docker-compose.dev.yml exec web python manage.py import_lr_data /data/ppd_data_flintshire.csv
# EPC data
docker compose -f docker-compose.dev.yml exec web python manage.py import_epc_data /data/certificates_conwy.csv
docker compose -f docker-compose.dev.yml exec web python manage.py import_epc_data /data/certificates_gwynedd.csv
docker compose -f docker-compose.dev.yml exec web python manage.py import_epc_data /data/certificates_denbighshire.csv
docker compose -f docker-compose.dev.yml exec web python manage.py import_epc_data /data/certificates_flintshire.csv
# Populate PropertyProfiles table
docker compose -f docker-compose.dev.yml exec web python manage.py populate_property_profiles

# Running Tailwind
npx @tailwindcss/cli -i ./src/input.css -o ./static/css/output.css --watch

# Running linter
ruff check
ruff check --watch
ruff check --fix

# Running Coverage
coverage run manage.py test
coverage report ### Aim for 80% ###


## About the Platform

A data-rich property development workspace for North Wales, combining land registry transactions, EPC intelligence, and curated investor collateral into a single, secure interface.
Key Features

Private Project Rooms: Role-based access gating with activity logging, brochure hosting, and instant CSV previews for investor diligence.
Spatial Intelligence: Leaflet-powered sale map with HTMX-driven filters for price bands, £/sqft benchmarks, and deed dates across Conwy, Denbighshire, Gwynedd, and Flintshire.
Market Insights: Editorial briefings and regional dossiers surfaced through tailored insights pages and embedded reference material.
Data Pipelines: Management commands that ingest HM Land Registry and EPC datasets, fuse them into geocoded PropertyProfiles, and surface pricing metrics down to the parcel.
Technical Stack

Django 5 with PostGIS-backed PostgreSQL, HTMX for partial updates, Leaflet.js with marker clustering, and Tailwind CSS for responsive UI.
Dockerised dev/prod environments with Gunicorn, Whitenoise, and Ruff/Coverage tooling baked in for linting and tests.
What’s Next?

Automated Alerts: Wire project access-denied signals into email notifications for faster investor onboarding.
UI Polish: Deliver the planned sticky navigation and additional map overlays for planning constraints.
Data Growth: Extend ingestion to commercial lettings, ONS socio-economic layers, and clean energy assets to deepen site selection analytics.
Analytics Roadmap: Layer time-series sale trends, bedroom/£ per sqft benchmarking panels, and exportable investor decks.