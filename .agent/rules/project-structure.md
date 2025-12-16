---
trigger: always_on
---

# PROJECT_STRUCTURE_RULE: base-repository

## 1. [PROJECT_IDENTITY]
**NAME**: `base-repository`
**TYPE**: Python Library (SQLAlchemy Wrapper)
**DESCRIPTION**: Provides a generic Repository pattern implementation with built-in CRUD, strict typing, and a Query DSL for complex filtering/sorting.

## 2. [TECH_STACK]
*   **Core**: Python 3.10+, SQLAlchemy >=1.4, Pydantic (v1/v2 compat).
*   **Package Manager**: `uv` (Strict enforcement).
*   **Linting/Formatting**: `ruff` (Line-length: 120, Quote: Single).
*   **Type Safety**: `mypy` (Strict mode).
*   **Testing**: `pytest` (Asyncio support).

## 3. [DIRECTORY_MAP]
| Path | Purpose |
| :--- | :--- |
| `/base_repository` | **SOURCE ROOT**. The package source code. |
| `/base_repository/repository` | **CORE LOGIC**. Contains `BaseRepository` (CRUD implementation). |
| `/base_repository/query` | **DSL ENGINE**. `ListQuery` and strategies for dynamic SQL generation. |
| `/tests` | **TEST SUITE**. Unit and Integration tests. Separated from source. |
| `/docs` | **DOCUMENTATION**. Project guides and API docs. |
| `/scripts` | **UTILITIES**. Maintenance and dev scripts. |

## 4. [MODULE_RESPONSIBILITIES]
### `base_repository` (Root Package)
*   **`repository/base_repo.py`**: The "God Class" for DB interactions. Implements `get`, `save`, `delete`, `update`, `search`.
*   **`query/list_query.py`**: Handles parsing of search parameters (limit, offset, filter, sort) into SQLAlchemy statements.
*   **`base_filter.py`**: Base class for defining custom filters.
*   **`validator.py`**: Input validation logic.

## 5. [DEVELOPMENT_RULES]
1.  **Strict Typing**: All new code MUST pass `mypy --strict`. Use `py.typed` marker.
2.  **Formatting**: Run `ruff format` before commit.
3.  **Imports**: Use absolute imports (e.g., `from base_repository.repository import ...`).
4.  **Testing**: New features must include `pytest` cases in `/tests`.
