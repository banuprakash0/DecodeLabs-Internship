# Enterprise Future Scalability Roadmap

This document maps out the architectural transition of `TaskManager` from a standalone CLI application into an enterprise-grade distributed platform.

---

## Evolution Stages

```text
+-------------------+      +-------------------+      +-------------------+
|  Phase 1 (Current)|      | Phase 2 (REST API)|      | Phase 3 (Cloud)   |
| Terminal CLI App  | ---> | FastAPI + ORM DB  | ---> | Microservices     |
| JSON Storage Engine|      | PostgreSQL + JWT  |      | Docker + K8s      |
+-------------------+      +-------------------+      +-------------------+
```

---

## Phase 2: RESTful Web Service Migration

### 1. Database Layer Replacement (SQLAlchemy & Alembic)
The `StorageInterface` in `storage.py` enables seamless database migration.
```python
# Replace JSONStorage with PostgreSQL ORM repository
class SQLAlchemyStorage(StorageInterface):
    def __init__(self, db_session: Session):
        self.session = db_session
    ...
```

### 2. FastAPI Web Framework Integration
Convert core service methods into async REST API endpoints:
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks` - List tasks with query parameters (`status`, `priority`, `search`)
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `POST /api/v1/auth/token` - OAuth2 JWT authentication token generation

---

## Phase 3: Frontend & Cloud Infrastructure

### 1. Web & Mobile Frontends
- **React / Next.js**: Modern web portal with Kanban board view, drag-and-drop task prioritization, and live WebSocket updates.
- **Flutter / React Native**: Mobile applications for iOS and Android task synchronization.

### 2. Microservices Architecture
- **Auth Service**: Keycloak / JWT bearer token issuer.
- **Task Microservice**: Core domain CRUD logic.
- **Notification Service**: Asynchronous Celery / RabbitMQ worker dispatching email and push reminders for overdue tasks.

### 3. Containerization & Deployment
- Docker containerization with multi-stage builds.
- Kubernetes deployment manifests with horizontal pod autoscaling (HPA).
- CI/CD pipelines configured via GitHub Actions.
