## Object-Oriented Design

### Abstraction
- Simplified interfaces hide implementation details:
  - `app.routes.get_db` yields a ready-to-use SQLAlchemy `Session` and handles closing it.
  - `app.crud` exposes create/enroll/import functions so routes don’t handle ORM minutiae.

### Encapsulation
- Data and behavior are grouped; internals aren’t accessed directly:
  - `app.models` defines columns and relationships; other layers use them only via sessions.
  - `app.database` encapsulates engine/session construction and initialization.
  - Deletion safety: relationships declare cascades (e.g., `Student.enrollments`), so deleting a parent removes dependent rows. Routes call CRUD delete functions rather than issuing raw SQL.

### Inheritance
- Shared structure via base classes/mixins:
  - `PersonMixin` (id, name, email) is reused by `Student` and `Teacher` to avoid duplication.
  - Pydantic models like `StudentOut` extend `StudentCreate` to add `id` and config.

### Polymorphism
- Same API, different concrete types/backends:
  - SQLAlchemy `Session` works uniformly across `Student`, `Teacher`, `Course`, `Enrollment`, `ScrapedResource`.
  - The database backend is interchangeable (SQLite/MySQL) by changing `DATABASE_URL`; calling code is unchanged.

### Key files
- `app/models.py` — entities and relationships
- `app/crud.py` — business logic
- `app/routes.py` — HTTP surface and dependency injection
- `app/database.py` — engine/session and table creation
