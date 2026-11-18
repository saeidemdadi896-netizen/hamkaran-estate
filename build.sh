set -o errexit

pip install --upgrade pip
pip install --user -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate