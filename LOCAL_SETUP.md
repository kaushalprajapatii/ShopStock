# ShopStock Local Setup

## 1. Open terminal in this folder

## 2. Create virtual environment

### Windows
python -m venv venv
venv\Scripts\activate

### Mac/Linux
python3 -m venv venv
source venv/bin/activate

## 3. Install dependencies

pip install -r backend/requirements.txt

## 4. Run project

python run_local.py

## 5. Open browser

http://127.0.0.1:8000

## Default Login

Email: admin@shop.com
Password: admin123

## Notes

- Uses SQLite locally
- No PostgreSQL required
- No deployment configuration required