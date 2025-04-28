# 🚴‍♂️ Leader's Jersey

**Leader's Jersey** is a web-based cycling prediction game where players select one rider per stage of a Grand Tour. The aim is to beat the GC (general classification) time using strategy, foresight, and a bit of luck.

---

## 🏁 How It Works

Each player:

- Selects one **stage rider** per stage (before the start of each stage).
- Selects one **backup rider** before the start of stage 1.
- Earns time equal to their selected rider’s stage result (minus bonus seconds).
- If their rider DNF'd, the **backup rider’s time** is used.
- If both the stage selected rider and backup DNF’d, the **last finisher’s time** is used as a fallback.
- Selections are **locked at the stage deadline** and results appear once the stage finishes.
- After the race, UCI points are awarded based on final GC position among players.

The player with the lowest total GC time at the end of the race wins! 🏆
Over the year, players can compete for the Overall UCI Points Leaderboard! 🌍✨

---

## 🔧 Features

- ✅ User registration and login
- ✅ ETL pipeline to fetch real-time stage data and results from ProCyclingStats
- ✅ Admin interface for managing races, stages, riders and results
- ✅ Dynamic countdown timer for each stage
- ✅ Auto-freezing selections after the deadline
- ✅ Total GC time calculation per user
- ✅ Stage-by-stage and final Leaderboard views
- ✅ DNF fallback logic with backup rider
- ✅ UCI Points system for completed races
- ✅ Overall yearly UCI Points Leaderboard
- ✅ Interactive modal pop-ups showing race-by-race UCI points breakdown
- ✅ Clean and customizable UI (Giro pink theme ready!)

---

## 📦 Tech Stack

- **Backend**: Django (Python)
- **Frontend**: Django Templates, HTML/CSS, JavaScript
- **Database**: SQLite (development)
- **Data Source**: [ProCyclingStats.com](https://www.procyclingstats.com/) via `procyclingstats` Python scraper
- **Admin Tools**: Django admin

---

## 🚀 Getting Started

1. Clone the repo  
   ```
   git clone https://github.com/yourusername/leaders-jersey.git
   cd leaders-jersey
   ```

2. Set up a virtual environment
    ```
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    ```

3. Install dependencies
    ```
    pip install -r requirements.txt
    ```
4. Run migrations & create superuser
    ```
    python manage.py migrate
    python manage.py createsuperuser
    ```
5. Start the development server
    ```
    python manage.py runserver
    ```
6. Visit http://127.0.0.1:8000 in your browser

🛠️ **Project Structure**
```
leaders_jersey/
├── etl/                   # ETL pipeline (extract, transform, load scripts)
├── game/                  # Main Django app
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/         # HTML templates (e.g. base.html, login.html, etc.)
│   └── static/            # Static files (JS, CSS, images)
├── leaders_jersey/        # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3             # SQLite database (development)
├── manage.py              # Django CLI entry point
venv/                      # Python virtual environment
.gitignore
README.md
requirements.txt
```

## 🔄 Running the ETL Process

You can trigger the ETL pipelines from the Django Admin panel:

- Go to Admin → ETL → ETL Runs → Add
- Select the race, stage, and ETL type (startlist, stage info, stage results)
- Click "Run ETL" to fetch and load the data automatically.


🗺️ Roadmap
🟢 Add form validation & improved UX
🟢 Add real GC comparison + highlight if user beats it
🟢 Add UCI points assignment and yearly leaderboard
🟢 Add race-by-race UCI points modal pop-up
🔜 Deploy to the web (Render, Railway, or similar)
🔜 Improve mobile layout and responsiveness
🔜 Add home page with upcoming races, game rules, and user profile links
🔜 Add player profile page with race history and UCI points overview
🔜 Add optional email notifications (e.g., stage reminder, results update)
🔜 Dark mode / theme switcher for better user experience

**Credits**

    Built with ❤️ by Jan Lodewijk Eshuis
    Data provided by ProCyclingStats.com

**Licence**

    © 2025 Jan Lodewijk Eshuis. All rights reserved.

    This project is intended for demonstration and private testing purposes only. 
    Unauthorized copying, modification, or distribution is prohibited without written permission.
