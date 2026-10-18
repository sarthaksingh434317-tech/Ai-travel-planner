# 🌍 TravelGenius AI – Smart Travel Planner

> **"Your Next Adventure, Planned by AI."**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask 3.0+](https://img.shields.io/badge/Framework-Flask%203.0%2B-black.svg)](https://flask.palletsprojects.com/)
[![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini%202.5-4285F4.svg)](https://aistudio.google.com/)
[![Database](https://img.shields.io/badge/Database-SQLite3-003B57.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📖 1. Project Overview

**TravelGenius AI** is an AI-powered travel planning web application that synthesizes comprehensive, day-by-day travel itineraries based on traveler preferences, departure city, destination, travel dates, traveler composition, budget in INR, travel styles, and dietary needs.

Built with a luxury travel aesthetic, responsive design, glassmorphism UI components, and real-time generative capabilities powered by **Google Gemini AI**.

---

## ✨ 2. Key Features

- **Personalized Day-by-Day Schedules**: Morning, afternoon, and evening time-blocked schedules with practical tips.
- **Estimated INR Budget Breakdown**: Detailed expense transparency categorized into Stay, Dining, Sightseeing, Local Transport, and Contingency.
- **Dual Mode Operation**:
  - **Live Gemini AI Mode**: Real-time generative itineraries using Google's Gemini models.
  - **High-Fidelity Demo Mode**: If no Gemini API key is configured or the API is unreachable, the system automatically provides high-fidelity, customized sample plans with explicit UI labeling.
- **Destination Explorer**: Interactive catalog featuring 10 curated global & domestic hotspots (Goa, Manali, Jaipur, Kerala, Kashmir, Bali, Dubai, Paris, Tokyo, Switzerland) with multi-criteria filtering and 1-click trip planning.
- **Persistent Storage (SQLite)**: Save favorite itineraries, browse saved trips, view rich modal breakdowns, and delete trips.
- **Interactive Budget Estimator**: Dynamic slider widget that computes estimated travel costs in INR by duration, travelers, comfort tier, and domestic vs. international scope.
- **Interactive Packing Checklist**: Category-sorted packing items with interactive checkboxes.
- **Weather-Proof Alternatives**: Tailored indoor backup plans for bad-weather days.
- **Export & Share Options**:
  - Clean print stylesheet formatted for PDF generation and physical vouchers (`window.print()`).
  - Markdown itinerary summary clipboard copy with toast feedback.
  - Web Share API integration (`navigator.share`).
- **Robust Validation**: Dual-layer input validation (frontend + backend) ensuring valid dates, traveler counts, and realistic budgets.

---

## 🛠️ 3. Technology Stack

- **Backend**: Python 3.10+, Flask, `google-genai`, `requests`, `python-dotenv`, `gunicorn`
- **Database**: SQLite 3 with atomic transaction management
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Font Awesome 6.5
- **Typography**: Google Fonts (*Plus Jakarta Sans* & *Outfit*)
- **Deployment**: Ready for Render (`render.yaml`, `Procfile`) and GitHub

---

## 📂 4. Project Directory Structure

```
ai-travel-planner/
│
├── app.py                      # Flask server, routes, and REST API endpoints
├── config.py                   # Application configuration & env loader
├── database.py                 # SQLite persistence layer and query methods
├── destinations_data.py        # Curated catalog for 10 top destinations
├── gemini_service.py           # Gemini AI prompt engine, parser & sample fallback
│
├── static/
│   ├── css/
│   │   ├── style.css           # Custom luxury design system & animations
│   │   └── print.css           # Clean print & PDF export stylesheet
│   ├── js/
│   │   ├── main.js             # Toast alerts, clipboard, and API key management
│   │   ├── planner.js          # Trip planner form, loading stepper & itinerary renderer
│   │   ├── explorer.js         # Destination filtering and modal preview
│   │   ├── my_trips.js         # Saved trips view, delete & export handlers
│   │   └── budget_calculator.js# Interactive travel budget estimator tool
│   └── images/
│       ├── logo.svg            # Custom SVG vector brand logo
│       └── hero-bg.svg         # High-resolution vector fallback hero background
│
├── templates/
│   ├── base.html               # Master layout with navigation, modal, and footer
│   ├── index.html              # Landing page (hero, popular destinations, how it works, testimonials)
│   ├── plan.html               # Smart AI Trip Planner form & loading state
│   ├── explore.html            # Destination Explorer with filters & quick modal
│   ├── my_trips.html           # Saved trips grid and detail modal
│   ├── about.html              # Technical overview, AI ethics & architecture
│   ├── 404.html                # Friendly 404 error page
│   └── 500.html                # Friendly 500 error page
│
├── tests/
│   └── test_app.py             # 12 comprehensive unit and integration tests
│
├── data/
│   └── trips.db                # SQLite database (auto-created on startup)
│
├── .env.example                # Sample environment variables file
├── .gitignore                  # Git ignore rules for Python, SQLite & IDE files
├── Procfile                    # Render / Heroku process file
├── render.yaml                 # Render web service blueprint
├── requirements.txt            # Python dependencies
└── README.md                   # Complete documentation
```

---

## 🚀 5. Getting Started Locally

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- `pip` package manager

### 1. Clone or Open Workspace
```bash
cd ai-travel-planner
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and set your configuration:
```env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here

# Get a free Gemini API key from https://aistudio.google.com/
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```
*(Note: If you leave `GEMINI_API_KEY` blank, TravelGenius AI automatically runs in Demo Mode with realistic sample plans!)*

### 4. Run the Application
```bash
python app.py
```
Or via the Python launcher:
```bash
py app.py
```

Open your browser at:
```
http://127.0.0.1:5000/
```

---

## 🧪 6. Running Automated Tests

Run the full suite of unit and integration tests:

```bash
python -m unittest tests/test_app.py
```
or
```bash
py -m unittest tests/test_app.py
```

The test suite validates:
1. Health check `/api/health`
2. Landing homepage rendering
3. Trip planner form rendering & query parameter prefill
4. Destination explorer and region/budget/style filters
5. SQLite database persistence (saving, retrieving, and deleting trips)
6. Frontend & backend date and budget validation errors
7. AI service fallback and comprehensive sample generation
8. Interactive travel budget calculator API

---

## 🌐 7. REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `GET /api/health` | GET | Health check and uptime status |
| `POST /api/generate-itinerary` | POST | Validates input and generates structured AI itinerary |
| `POST /api/save-trip` | POST | Saves itinerary to SQLite database |
| `GET /api/trips` | GET | Lists all saved itineraries |
| `GET /api/trips/<trip_id>` | GET | Retrieves full itinerary details for a specific trip |
| `DELETE /api/trips/<trip_id>` | DELETE | Deletes a saved trip from SQLite |
| `GET /api/destinations` | GET | Returns curated destination catalog with query filtering |
| `GET /api/destinations/<dest_id>`| GET | Returns destination details by ID |
| `POST /api/calculate-budget` | POST | Calculates estimated budget breakdown in INR |

---

## ☁️ 8. Deployment Guide

### Deploying to GitHub
```bash
git init
git add .
git commit -m "Initial commit: TravelGenius AI - Smart Travel Planner"
git branch -M main
git remote add origin https://github.com/<your-username>/travelgenius-ai.git
git push -u origin main
```

### Deploying to Render
1. Log in to [Render](https://render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Render will automatically detect `render.yaml` or you can manually configure:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. In **Environment Variables**, add:
   - `GEMINI_API_KEY`: *(Your Google AI Studio API key)*
   - `SECRET_KEY`: *(A strong random secret string)*
   - `FLASK_ENV`: `production`
6. Click **Deploy Web Service**.

---

## 🛡️ 9. Ethics, Safety & Disclaimers

1. **Estimates Only**: All flight costs, hotel tariffs, entry tickets, and transit fares are realistic estimates in Indian Rupees (INR). Users are advised to confirm live bookings and operating hours before traveling.
2. **Transparent AI**: Live Gemini generation is clearly marked with a badge. When running in sample mode, the application explicitly notifies the traveler that demo data is displayed.
3. **Privacy First**: Travel plans are saved locally on your server/browser using SQLite. No user data is tracked or sold.

---

## 📄 License
This project is licensed under the MIT License.
