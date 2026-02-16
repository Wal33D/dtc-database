# Release Notes

## 2026-02-16 - Documentation/Alignment Update

This repository maintenance update aligns code and documentation with the current dataset and schema.

### Fixed

- Python wrapper query logic now correctly reads the composite schema:
  - `code + manufacturer + locale`
  - generic-first and manufacturer-aware lookups
- Python manufacturer lookups now return expected rows for uppercase manufacturer keys (for example, `FORD`)
- Java core wrapper (`java/DTCDatabaseCore.java`) rebuilt to target the current SQLite schema
- Android Java statistics logic now correctly treats `manufacturer='GENERIC'` as generic and filters by locale

### Documentation Synced

- README counts and examples now match the current database:
  - total definitions: `18,805`
  - generic: `9,415`
  - manufacturer-specific definitions: `9,390`
  - unique codes: `12,128`
- Installation/API docs updated for the current repository workflow
- TypeScript README and metadata updated to reflect current source-based distribution status

### Validation

- `python3 test.py` passes
- `python3 test_schema.py` passes
- `cd typescript && npm run build && npm test` passes
- `cd java && javac DTCDatabaseCore.java` passes

## v0.1.0 (2025-10-23)

Initial tagged release on GitHub.
