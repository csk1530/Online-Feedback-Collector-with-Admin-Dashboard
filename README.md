# Online-Feedback-Collector-with-Admin-Dashboard

## Setup
1. Create a virtualenv and activate it:
   python -m venv venv
   source venv/bin/activate   # linux/mac
   venv\Scripts\activate      # windows

2. Install dependencies:
   pip install -r requirements.txt

3. (Optional) Edit `app.py` to change `app.secret_key` and admin password.
   To change admin password, replace the hash:
     from werkzeug.security import generate_password_hash
     print(generate_password_hash("your-password"))

4. Run:
   python app.py

5. Open:
   - User form: http://127.0.0.1:5000/
   - Admin login: http://127.0.0.1:5000/admin-login
     (default username: `admin`, password: `admin123`)

## Features
- Submit feedback (name, email, rating 1-5, comments)
- Admin dashboard with stats, Chart.js visualization, recent entries
- JSON API: /api/feedback
- Export CSV: /export-csv (requires admin login)

## Project structure
See your original project layout. Place templates into `templates/` and static files into `static/css` and `static/js`.
