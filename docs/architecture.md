# Architecture

## Layers

1. **API layer** (`app/api/`) — thin FastAPI routers: validation via Pydantic schemas, dependency
   injection for DB session/settings/provider, consistent error envelopes via registered handlers.
2. **Service layer** (`app/services/`) — all business logic:
   - `ai/` provider abstraction + parsing + prompts
   - `symptoms/` symptom persistence and context extraction
   - `reports/` upload validation, PDF text extraction, lab normalization
   - `risk/` deterministic red-flag detection and escalation
   - `analysis/` orchestrator combining everything into a persisted result
3. **Data layer** (`app/models/`, `app/database/`) — SQLAlchemy 2 models on SQLite.

## Data model

- `HealthProfile 1—N AnalysisSession 1—N {SymptomInput, Report, AnalysisResult}`
- Session tracks wizard status: `created → symptoms_recorded → follow_up_pending →
  follow_up_complete → analyzed`.

## Request flow (analysis)

```
POST /api/analyze {session_id}
  → orchestrator.run_analysis()
      → build payload (profile + symptoms + answers + report findings)
      → provider.analyze_health_information(payload)     # validated AnalysisResultSchema
      → assess_text_safety(...)                          # deterministic regex red flags
      → apply_safety_layer(analysis, assessment)         # max-escalation merge
      → persist AnalysisResult, mark session analyzed
```

## Safety invariants

- Risk can only be escalated by the safety layer (`LOW < MODERATE < HIGH`).
- Red-flag hits always append explicit urgent-care guidance to next steps.
- AI responses failing schema validation become controlled errors — never rendered.
- Demo outputs are visibly labeled at every layer (summary prefix, UI chip, API source field).
