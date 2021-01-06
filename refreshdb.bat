python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > dbdata.json
del db.sqlite3
python manage.py makemigrations
python manage.py migrate
manage.py migrate --run-syncdb
python manage.py loaddata dbdata.json
del dbdata.json