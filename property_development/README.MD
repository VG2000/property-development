# To run in dev:
docker compose -f docker-compose.dev.yml up --build -d

# To make migrations
python manage.py makemigrations --settings=property_development.settings.dev

# To run in prod:
docker compose -f docker-compose.prod.yml up --build -d

### To seed data
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
