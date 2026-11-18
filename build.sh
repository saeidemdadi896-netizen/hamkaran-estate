set -o errexit

# ساخت محیط مجازی
python3 -m venv venv
source venv/bin/activate

# نصب وابستگی‌ها
pip install --upgrade pip
pip install -r requirements.txt

# دستورات دیتابیس و استاتیک
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
