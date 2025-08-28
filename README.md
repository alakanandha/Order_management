Setup Instructions


git clone <your-repo-url>
cd order_management
python -m venv .venv
.venv\Scripts\activate   
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


Test User Credentials
Admin Side
Login URL: /accounts/admin-login/
Username: admin
Password: admin123

Customer Side
Login URL: /shop/
Username: alakan
Password: Alakaps@123
