# Gravity Teaching Platform

Professional web-based platform like Classplus for coaching institutes.

## Setup
1. Install MySQL (https://dev.mysql.com/downloads/installer/), set root password, create DB: `CREATE DATABASE gravity_db;`
2. `pip install -r requirements.txt`
3. Copy .env.example to .env, update secrets/DB creds.
4. Run DB schema: `mysql -u root -p gravity_db < database/schema.sql`
5. `python run.py`
6. Open http://localhost:5000

## Features
- Teacher/Student/Admin panels
- Courses, materials upload (PDF/video/image/notes)
- Simulated payments (UPI + bank, manual verification)
- JWT auth, responsive UI

Bank details: Zakir Husain, SBI 30392342115
UPI: PhonePe/GPay 7229985050
