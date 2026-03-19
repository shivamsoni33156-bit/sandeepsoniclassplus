# Implementation TODO

## Setup (User Actions)
- [ ] Install MySQL, create `gravity_db` user root/your_pass
- [ ] `pip install -r requirements.txt`
- [ ] Copy `.env.example` to `.env`, set `MYSQL_PASSWORD`, generate `SECRET_KEY`
- [ ] `mysql -u root -p gravity_db < database/schema.sql`

## Development Steps (AI Tracked)
- [x] Create project structure (requirements.txt, README.md, TODO.md, .env.example)
- [x] Create database/schema.sql
- [x] Create backend/app.py, models.py
- [x] Implement auth routes (register/login)
- [x] Create frontend/index.html, css/, js/
- [ ] Add course/materials routes/UI (enhanced)
- [ ] Implement payments (UPI page)
- [ ] Add tests feature (basic)
- [ ] Admin panel
- [ ] Test full flow, fix issues
- [ ] Complete!

Run `python run.py` to start.
