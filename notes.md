rm db.sqlite3
echo "migrate"
python manage.py migrate

echo "load db data"
python manage.py load_base_db_data





python manage.py import_report ~/test-data/report/lux-gastro-report.pdf

python manage.py import_report ~/test-data/report/lux-histo-0.pdf

python manage.py import_report ~/test-data/report/lux-histo-1.pdf
python manage.py import_report ~/test-data/report/AW_PAtho.pdf
python manage.py import_report ~/test-data/report/AW_ÖGD.pdf