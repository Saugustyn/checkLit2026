# checkLit

Platforma do analizy autentyczności i stylu tekstów literackich.  
Praca inżynierska — Politechnika / Akademia, 2026.

---

## O projekcie

checkLit analizuje teksty literackie pod kątem dwóch aspektów:

**Detekcja AI** — na podstawie perplexity modelu Polish GPT-2. Niższe perplexity oznacza bardziej przewidywalny tekst, charakterystyczny dla generatorów AI. Model skalibrowany na korpusie 80 tekstów (AUC = 0.90).

**Analiza stylometryczna** — MATTR (bogactwo leksykalne), gęstość leksykalna, entropia Shannona, bogactwo słownikowe, indeks czytelności LIX, najczęstsze bigramy, średnia długość zdania.

Platforma obsługuje tekst wklejony bezpośrednio lub wgrany jako plik (.txt, .pdf, .docx). Wyniki można eksportować jako JSON lub wydrukować jako PDF.

---

## Uruchamianie

### Wymagania

- Python 3.11
- Node.js 18+
- ~500MB wolnego miejsca (model Polish GPT-2 pobierany przy pierwszym uruchomieniu)

### Szybki start (Windows)

```powershell
.\start.ps1
```

Skrypt uruchamia backend i frontend w osobnych oknach terminala.

---

### Ręczne uruchamianie

**Backend:**

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend: http://localhost:8000  
Dokumentacja API (Swagger): http://localhost:8000/docs

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

---

## Testy

```bash
cd backend
venv\Scripts\activate
pytest tests/ -v
```

86 testów jednostkowych i integracyjnych (100% pass rate).  
Model GPT-2 jest mockowany — testy działają bez ładowania modelu (~1.5s).

---

## Ewaluacja modelu

```bash
cd backend/eval
python evaluate.py
```

Generuje: `roc_curve.png`, `evaluation_results.csv`, `evaluation_summary.json`.  
Wyznacza optymalny próg metodą Youdena na krzywej ROC.

---

## Endpointy API

| Metoda | URL | Opis |
|--------|-----|------|
| POST | /api/analyze | Analiza tekstu (JSON) |
| POST | /api/analyze-file | Analiza pliku (.txt, .pdf, .docx) |
| GET | /api/results/{id} | Pobierz wyniki po ID |
| GET | /api/history | Historia analiz |
| DELETE | /api/history/{id} | Usuń analizę |
| POST | /api/compare | Porównanie stylometryczne dwóch tekstów |
| GET | /api/results/{id}/text | Pobierz oryginalny tekst (.txt) |
| GET | /api/results/{id}/export | Eksport raportu (JSON) |

---


## Model detekcji AI

Model: [`sdadas/polish-gpt2-small`](https://huggingface.co/sdadas/polish-gpt2-small) (Hugging Face)  
Architektura: GPT-2, causal language model (autoregresywny)  
Metoda: perplexity — niższe perplexity = tekst bardziej przewidywalny = wyższe P(AI)

Mapowanie perplexity → prawdopodobieństwo: sigmoida z parametrami skalibrowanymi na rozkładzie korpusu v3 (midpoint = 250, k = 0.012).

Progi klasyfikacji (ROC/Youden, rekalibracja v3):

| Perplexity | Klasyfikacja |
|------------|--------------|
| < 32.03 | AI-generated |
| 32.03 – 41.06 | Strefa szara (Niepewny) |
| > 41.06 | Human-written |

Wyniki ewaluacji (n=80, corpus_full.csv):

| Metryka | Wartość |
|---------|---------|
| AUC-ROC | 0.9029 |
| Accuracy | 82.5% |
| Precision | 76.1% |
| Recall | 92.1% |
| F1 | 83.3% |

---

## Uwagi

- Przy pierwszym uruchomieniu model GPT-2 zostanie pobrany (~500MB)
- Baza danych SQLite tworzona automatycznie jako `literary_analyzer.db` (wykluczona z gita)
- Backend i frontend muszą działać jednocześnie
- System skalibrowany na polskich tekstach literackich — wyniki na innych gatunkach mogą być mniej wiarygodne