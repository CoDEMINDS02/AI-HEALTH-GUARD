# AI HealthGuard

**AI-Powered Medical Health Analysis Assistant — local prototype**

> ⚠️ **Medical disclaimer:** AI HealthGuard provides preliminary health information and does not
> provide a medical diagnosis or replace a qualified healthcare professional. This is a
> **DEMO / EDUCATIONAL PROTOTYPE**, not a medical device.

---

## Project overview

### Problem statement

People often struggle to organize their symptoms, medical context, and lab reports into something
useful before (or instead of) seeing a doctor. Generic internet searches are unreliable and often
either alarmist or falsely reassuring. Serious "red flag" symptoms can be buried in noise.

### Solution

AI HealthGuard is a preliminary health analysis assistant that:

- collects a minimal health profile and structured symptom input,
- asks a small number of **relevant AI-generated follow-up questions**,
- optionally reads an uploaded medical report (PDF) while preserving units and reference ranges,
- combines everything into a **structured, validated assessment** (never free-form model output),
- runs every result through a **deterministic safety layer** that detects urgent warning signs and
  escalates risk regardless of what the AI claims.

It explicitly does **not**: diagnose disease, prescribe medication or dosages, state certainty
about any condition, or discourage seeking care. All output uses cautious wording such as
"possible concern", "may be associated with", "could warrant further evaluation".

### Key features

| Feature | Notes |
|---|---|
| Health profile | Age, sex, conditions, allergies, medications, brief history only |
| Symptom intake | Primary/additional symptoms, description, duration, severity 1–10, onset |
| Follow-up questions | Provider-generated, capped count, stored with answers |
| Medical report upload | PDF text extraction → normalized lab values; images accepted without fake OCR |
| Structured analysis | Strict JSON contract validated by Pydantic; malformed AI output never reaches the UI |
| Deterministic safety engine | Regex red-flag rules override AI risk level upward, never downward |
| Results dashboard | Risk level, summary, concerns, red flags, next steps, questions for your doctor |
| History | Past analyses stored in SQLite |

---

## Architecture

```
USER
 ↓
Health Profile ──────────────┐
Symptoms ────────────────────┤
AI Follow-up Questions ──────┤     FastAPI backend (SQLite via SQLAlchemy)
Optional Medical Report ─────┤        ├── PDF parser + lab normalizer
                             ▼        │
                  Combined Analysis Request    │
                             ▼                 │
                    AIProvider abstraction ────┤── DemoAIProvider (offline)
                       (swap vendors freely)   └── OpenAICompatibleProvider
                             ▼                        (Qwen later)
                  Safety / Risk Layer  ← deterministic red-flag rules
                             ▼
                Structured Health Assessment  (Pydantic-validated JSON)
                             ▼
                      User Dashboard (React + Vite)
```

Key design rule: **the language model never has the final say on emergency risk.**
`app/services/risk/engine.py` merges the AI's `risk_level` with deterministic red-flag detection
(`app/services/risk/red_flags.py`) using *max escalation* — safety can raise LOW/MODERATE to HIGH
and injects explicit "seek urgent care" guidance.

## Tech stack

- **Frontend:** React 18, Vite, React Router, hand-written CSS (no heavy UI deps)
- **Backend:** Python 3.10+, FastAPI, Pydantic v2 (+ pydantic-settings), SQLAlchemy 2, Uvicorn
- **AI:** provider abstraction — `DemoAIProvider` (offline, deterministic) and
  `OpenAICompatibleProvider` (any `/chat/completions` compatible endpoint). **Alibaba Cloud Qwen
  will be integrated as the production provider behind this same interface** (see
  [docs/qwen-integration.md](docs/qwen-integration.md)).
- **Reports:** pypdf text extraction + regex lab-value normalization
- **Database:** SQLite via SQLAlchemy ORM
- **Tests:** pytest + FastAPI TestClient (67 tests)

## Project structure

```
ai-healthguard/
├── frontend/
│   ├── src/
│   │   ├── components/   # Header, Stepper, RiskBadge, Loader, Section, DisclaimerBanner
│   │   ├── pages/        # Landing, Profile, Symptoms, FollowUp, Report, Analyzing, Results, History
│   │   ├── services/     # api.js fetch wrapper
│   │   ├── context/      # FlowContext (assessment wizard state)
│   │   ├── hooks/        # useDemoMode
│   │   ├── types/        # JSDoc typedefs
│   │   └── App.jsx / main.jsx / styles.css
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/          # routes/ (profiles, symptoms, follow_up, reports, analyses, health), deps, error handlers
│   │   ├── core/         # config (.env), logging, constants, errors
│   │   ├── database/     # engine/session/init
│   │   ├── models/       # SQLAlchemy: HealthProfile, AnalysisSession, SymptomInput, Report, AnalysisResult
│   │   ├── schemas/      # Pydantic request/response + AI output contract
│   │   ├── services/
│   │   │   ├── ai/       # base, factory, demo_provider, openai_compatible, prompts, parsing
│   │   │   ├── symptoms/
│   │   │   ├── reports/  # pdf_parser, normalizer, service
│   │   │   ├── risk/     # red_flags (rules), engine (override logic)
│   │   │   └── analysis/ # orchestrator
│   │   └── main.py
│   ├── requirements.txt / requirements-dev.txt / .env.example
├── tests/                # schemas, risk engine, providers, reports, API flows
├── docs/                 # architecture + Qwen integration plan
├── README.md
└── .gitignore
```

---

## Local setup

### Prerequisites

- Python 3.10+ (developed on 3.14)
- Node.js 18+

### Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt

copy .env.example .env   # Windows  (cp .env.example .env on macOS/Linux)
```

The app starts fully working with `AI_PROVIDER=demo` — no keys needed.

### Database initialization

The SQLite database (`healthguard.db`) is created automatically at startup. To force it manually:

```bash
python -c "from app.database.session import init_db; init_db()"
```

### Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

### Running the backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs for interactive Swagger documentation.
The Vite dev server proxies `/api/*` to port 8000, so no CORS friction during development.

## Environment variables

All configuration lives in `.env` (see `backend/.env.example`). Never commit real secrets.

```ini
AI_PROVIDER=demo              # demo | openai (any OpenAI-compatible endpoint; qwen planned)
AI_API_KEY=                   # required when AI_PROVIDER != demo
AI_BASE_URL=                  # e.g. https://dashscope-compatible-endpoint/v1 (for Qwen later)
AI_MODEL=                     # e.g. qwen-max
AI_TIMEOUT_SECONDS=45
AI_MAX_FOLLOW_UP_QUESTIONS=4

DATABASE_URL=sqlite:///./healthguard.db

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
UPLOAD_MAX_BYTES=10485760
LOG_LEVEL=INFO
```

## Demo mode

With `AI_PROVIDER=demo`, the `DemoAIProvider` produces **deterministic, clearly synthetic**
analyses from keyword rules so the entire product flow works offline. Every demo response is
prefixed `[DEMO OUTPUT]`, the UI shows a persistent **DEMO MODE** chip, and results are labeled
"DEMO OUTPUT — SYNTHETIC". Demo mode must never be presented as real medical output.

## AI provider architecture

All providers implement one interface (`backend/app/services/ai/base.py`):

```python
class AIProvider(ABC):
    def generate_follow_up_questions(self, symptom_context) -> list[str]
    def analyze_health_information(self, payload) -> AnalysisResultSchema
    def explain_medical_report(self, report_text, findings) -> str
```

Selection is environment-driven (`PROVIDER_REGISTRY` in `factory.py`). Adding Qwen means adding
one class and one registry entry — no application code changes. Responses must pass the Pydantic
`AnalysisResultSchema`; fenced/embedded JSON is tolerated by the safe parser, but garbage becomes a
controlled `502 ai_invalid_response`, never raw model output in the UI.

## API overview

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Service status, active provider, demo-mode flag |
| POST | `/api/profile` | Create health profile + open analysis session |
| POST | `/api/symptoms` | Submit symptom record for a session |
| POST | `/api/follow-up` | Generate follow-up questions for a session |
| POST | `/api/follow-up/answers` | Store answers to generated questions |
| POST | `/api/reports/upload` | Upload PDF/image report (multipart) |
| POST | `/api/reports/{id}/explain` | Plain-language report explanation |
| POST | `/api/analyze` | Run combined analysis for a session |
| GET | `/api/analyses` | List recent analyses |
| GET | `/api/analyses/{id}` | Fetch one full analysis |

Errors use a consistent envelope: `{"error": {"code": "...", "message": "...", "details": [...]}}`.
Stack traces, keys, and internals are never exposed.

## Testing

```bash
cd backend
.venv\Scripts\python -m pytest ..\tests -v
```

Covered cases include:

1. **Fever + cough** — normal flow, non-emergency risk
2. **Headache + dizziness** — normal flow
3. **Chest pain + difficulty breathing** — verifies the safety layer **overrides** the lower
   AI/demo risk level to HIGH and inserts urgent-care guidance (`safety_override=true`)
4. **Report parsing** — lab values, units, ranges, flags; scanned-PDF failure reported honestly;
   image accepted without pretending OCR worked
5. **Malformed AI response** — controlled `502` envelope, raw output never leaks
6. Schema validation, CSV symptom parsing, oversized/unsupported uploads, profile bounds, and more.

Current status: **67 passed, 0 failed.**

## Medical safety limitations

- Not a diagnosis, not a medical device, not certified for clinical use.
- Red-flag patterns catch *obvious* emergency signals only; absence of flags ≠ absence of danger.
- Report parsing handles plain-text PDF labs; scanned documents fail clearly rather than guessing.
- The demo provider is intentionally simplistic and exists purely to exercise the workflow.
- All outputs carry persistent disclaimers and cautious phrasing.

## Future Alibaba Cloud / Qwen integration plan

Qwen will be integrated as the production AI provider. See
[docs/qwen-integration.md](docs/qwen-integration.md) for the exact steps.
