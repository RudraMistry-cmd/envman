# Project Context

## Environment
- Language: Python 3.14.5
- Runtime: pytest 9.1.1
- Build: N/A (Python project)
- Test: python -m pytest tests/
- Package Manager: pip

## Project Type
- [x] Application (CLI/Web/Mobile/Desktop)
- Backend API with Docker orchestration

## Structure
- Source: D:\Projects\envman\backend\app
- Tests: D:\Projects\envman\backend\tests
- Docs: N/A
- Entry: D:\Projects\envman\backend\app\main.py

## Conventions
- Naming: snake_case
- Imports: absolute (from app.xxx import yyy)
- Error handling: exceptions + Pydantic validation
- Testing: pytest with pytest-asyncio

## Current Status
- ALL 184 tests PASS
- Files modified: test_environment.py, test_service_definitions.py, test_planner.py, test_verifier.py
- Dependencies added: pytest-asyncio

## Test Results
| File | Tests | Status |
|------|-------|--------|
| tests/models/test_environment.py | 28 | PASS |
| tests/registry/test_service_definitions.py | 132 | PASS |
| tests/engine/test_planner.py | 10 | PASS |
| tests/engine/test_verifier.py | 21 | PASS |
| tests/storage/test_db.py | 3 | PASS |

## Pending Tasks
- None - all tests passing

## Notes
- Docker images cached locally, so image_exists mocked for pull tests
- Service `id` field used for Docker naming, `name` is display only
- Legacy format converter requires `node` key to trigger
