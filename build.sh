set -o errexit

# نصب وابستگی‌ها در محیطی که رندر ارائه داده است
pip install --upgrade pip
pip install -r requirements.txt

# اجرای دستورات جنگو
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
