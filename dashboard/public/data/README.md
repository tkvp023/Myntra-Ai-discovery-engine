# Dashboard Data Directory

This folder is populated by the pipeline after Phase 3 completes.

## Expected files

| File | Description |
|---|---|
| `summary.json` | KPI cards, source distribution, top opportunities |
| `q1.json` — `q10.json` | Per-question breakdown, segments, quotes, trends |
| `systemic_gaps.json` | Secondary source analysis |
| `corpus_meta.json` | Corpus statistics and run metadata |

## While pipeline hasn't run

The dashboard falls back to realistic mock data defined in `lib/mockData.ts`.
Drop the real JSON files here once `pipeline/export.py` has run.

## Schema

See `DOCS/data_contracts.md` for the full JSON schema for each file.
