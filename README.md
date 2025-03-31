🚴‍♂️ Leader's Jersey
Leader's Jersey is a web-based cycling prediction game where players select one rider per stage of a Grand Tour. The aim is to beat the GC (general classification) time using strategy, foresight, and a bit of luck.

🏁 How It Works
Each player:

Selects one stage rider per stage (before the 12:00 deadline).

Selects one backup rider before the start of stage 1.

Earns time equal to their selected rider’s stage result (minus bonus seconds).

If their rider DNF'd, the backup rider’s time is used.

If both DNF’d, the last finisher’s time is used as a fallback.

Selections are locked at the stage deadline and results appear once the stage finishes.

The player with the lowest total GC time at the end of the race wins! 🏆

🔧 Features
✅ User registration and login

✅ ETL pipeline to fetch real-time stage data and results from ProCyclingStats

✅ Admin interface for managing races, stages, riders and results

✅ Dynamic countdown timer for each stage

✅ Auto-freezing selections after the deadline

✅ Total GC time calculation per user

✅ Leaderboard view

✅ DNF fallback logic with backup rider

✅ Clean and customizable UI (Giro pink theme ready!)

📦 Tech Stack
Backend: Django (Python)

Frontend: Django Templates, HTML/CSS, JavaScript

Database: SQLite (development)

Data Source: ProCyclingStats.com via procyclingstats Python scraper

Admin Tools: Django admin

🚀 Getting Started
Clone the repo

bash
Kopiëren
Bewerken
git clone https://github.com/yourusername/leaders-jersey.git
cd leaders-jersey
Set up a virtual environment

bash
Kopiëren
Bewerken
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
Install dependencies

bash
Kopiëren
Bewerken
pip install -r requirements.txt
Run migrations & create superuser

bash
Kopiëren
Bewerken
python manage.py migrate
python manage.py createsuperuser
Start the development server

bash
Kopiëren
Bewerken
python manage.py runserver
Visit http://127.0.0.1:8000 in your browser

🛠️ Project Structure
csharp
Kopiëren
Bewerken
leaders_jersey/
├── game/                  # Django app (models, views, templates)
├── etl/                   # Custom ETL pipeline
├── templates/             # HTML templates
├── static/                # Static JS/CSS
├── db.sqlite3             # Dev database
└── manage.py
🗺️ Roadmap
🟢 Add form validation & improved UX

🟢 Add real GC comparison + highlight if user beats it

🔜 Deploy to the web (Render or Railway)

🔜 Mobile layout improvements

🔜 Email notifications (optional)

🙌 Credits
Built with ❤️ by Jan Lodewijk Eshuis.
Data provided by ProCyclingStats.