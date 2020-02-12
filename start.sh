printenv | sed 's/^\(.*\)$/export \1/g' > /app/project_env.sh

python manage.py makemigrations
python manage.py migrate
python manage.py load_data
python manage.py runserver 0.0.0.0:8000
#hello test
