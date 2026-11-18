set -o errexit

# ساخت محیط مجازی
python3 -m venv venv
source venv/bin/activate

# نصب وابستگی‌ها در محیط مجازی
pip install --upgrade pip
pip install -r requirements.txt

# اجرای دستورات جنگو
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py makemigrations
