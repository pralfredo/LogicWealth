# Run the LogicWealth Website

The website is now a live FastAPI + vanilla JavaScript app. The dashboard calls the Python solver through `/api/solve`.

## 1. Start from the project root

```bash
cd LogicWealth
```

## 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Launch the website

```bash
uvicorn logicwealth.api.app:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

## 5. What works

- Live mandate editor
- Backend selector: `auto`, `z3`, `greedy`
- Solve button wired to the Python solver
- Portfolio holdings table
- Constraint certificate
- Sector exposure bars
- Why-not explanation, e.g. `NVDA`
- Asset universe search table
- API docs at `/docs`

## 6. API endpoints

```text
GET  /api/health
GET  /api/assets
POST /api/solve
```

## 7. CLI still works

```bash
python logicwealth_cli.py --backend greedy
python logicwealth_cli.py --backend z3 --why-not NVDA
```
