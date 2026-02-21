# Literary Analyzer

Platforma do analizy autentyczności i stylu tekstów literackich.  
Praca inżynierska.

---

## 🚀 Uruchamianie projektu

### 1. Backend (FastAPI)

```bash
cd backend

# Utwórz wirtualne środowisko
python -m venv venv

# Aktywuj (Windows)
venv\Scripts\activate

# Aktywuj (Linux/Mac)
source venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom serwer deweloperski
uvicorn app.main:app --reload --port 8000
```

Backend dostępny pod: http://localhost:8000  
Dokumentacja API (Swagger): http://localhost:8000/docs

### 2. Frontend (React + Vite)

```bash
cd frontend

# Zainstaluj zależności
npm install

# Uruchom deweloperski serwer
npm run dev
```

Frontend dostępny pod: http://localhost:5173

---

## 🧪 Testy

```bash
cd backend
pytest tests/ -v
```

---

## 📁 Struktura projektu

```
literary-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py          # Punkt wejścia FastAPI
│   │   ├── database.py      # Konfiguracja SQLite
│   │   ├── models.py        # Modele SQLAlchemy
│   │   ├── schemas.py       # Schematy Pydantic
│   │   ├── routers/
│   │   │   └── analysis.py  # Endpointy API
│   │   └── services/
│   │       ├── stylometry.py  # Analiza stylometryczna
│   │       ├── nlp_service.py # Jakość językowa (Flesch)
│   │       └── ai_detector.py # Detekcja AI (HuggingFace)
│   ├── tests/
│   │   └── test_analysis.py   # Testy pytest
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api/axios.js       # Klient HTTP
│   │   ├── components/
│   │   │   └── Navbar.jsx
│   │   └── pages/
│   │       ├── Home.jsx
│   │       ├── Analyze.jsx
│   │       ├── Results.jsx
│   │       ├── History.jsx
│   │       ├── Compare.jsx
│   │       └── About.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## 🔌 Endpointy API

| Metoda | URL | Opis |
|--------|-----|------|
| POST | /api/analyze | Analiza tekstu |
| GET | /api/results/{id} | Pobierz wyniki |
| GET | /api/history | Historia analiz |
| POST | /api/compare | Porównaj dwa teksty |
| DELETE | /api/history/{id} | Usuń analizę |

---

## ⚠️ Uwagi

- Przy pierwszym uruchomieniu model AI zostanie pobrany (~500MB)
- Baza danych SQLite tworzona automatycznie jako `literary_analyzer.db`
- Backend i frontend muszą działać jednocześnie
