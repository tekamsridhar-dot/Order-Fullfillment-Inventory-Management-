# Order Fulfillment & Inventory Management Platform

## 1. Project Overview

The Order Fulfillment & Inventory Management Platform is a REST API application built using FastAPI and PostgreSQL. It manages products, warehouses, inventory, customer orders, fulfillment operations, returns, notifications, and audit logs.

The project focuses on secure authentication, role-based access control, inventory reservation, transactional consistency, concurrency handling, idempotency, and automated testing.

## 2. Technology Stack

- **Language:** Python 3.13
- **Backend Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Database Migrations:** Alembic
- **Data Validation:** Pydantic
- **Authentication:** JWT
- **Testing:** Pytest
- **API Testing:** Postman
- **Containerization:** Docker and Docker Compose

## 3. User Roles

The application supports the following roles:

- **Admin:** Manages products, warehouses, users, and system operations.
- **Warehouse Manager:** Manages inventory and operations for authorized warehouses.
- **Fulfillment Agent:** Processes, packs, and ships assigned orders.
- **Customer:** Places orders, views personal orders, cancels eligible orders, and requests returns.

Access is controlled through authentication, role-based permissions, resource ownership, and warehouse authorization.

## 4. Key Features

### Authentication and Authorization
- User registration and login.
- Password hashing.
- JWT access and refresh tokens.
- Token refresh and revocation.
- Role-based endpoint protection.

### Product and Warehouse Management
- Product and category management.
- Unique product SKU validation.
- Warehouse creation and management.
- Warehouse-user assignments.
- Product activation and deactivation.

### Inventory Management
- Warehouse-specific inventory tracking.
- Inventory adjustments and transfers.
- Available, reserved, and damaged quantities.
- Inventory transaction history.
- Low-stock detection and alerts.
- Inventory reservation and release.

### Order Management
- Order creation and retrieval.
- Order item pricing snapshots.
- Automatic order total calculation.
- Inventory reservation during order creation.
- Order cancellation and inventory release.
- Order assignment and fulfillment tracking.

### Returns and Payments
- Return requests and status transitions.
- Return item and quantity validation.
- Payment confirmation and status tracking.

### Notifications and Audit Logging
- User notifications.
- Read and read-all notification operations.
- Audit logs for important system activities.
- Tracking of inventory and order changes.

### Additional Features
- Pagination, filtering, and sorting.
- Dashboard and reporting endpoints.
- Centralized error handling.
- Idempotency for critical operations.
- Automated tests.

## 5. Project Structure

```text
order-fulfillment-platform/
├── app/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── routers/
│   ├── utils/
│   ├── tasks/
│   ├── database.py
│   └── main.py
├── alembic/
│   └── versions/
├── tests/
├── diagrams/
│   ├── database-schema.png
│   ├── architecture-diagram.png
├── postman/
│   ├── order-fulfillment-api.postman_collection.json
│   └── order-fulfillment-local.postman_environment.json
├── .env.example
├── .gitignore
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

The exact structure may include additional modules depending on the implementation.

## 6. Prerequisites

Install the following:

- Python 3.13 or a compatible version.
- PostgreSQL, or Docker with Docker Compose.
- Git.
- Postman (optional, for API testing).

## 7. Installation and Local Setup

### Step 1: Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd order-fulfillment-platform
```

### Step 2: Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### Step 3: Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create your local `.env` file using `.env.example` as a template.

Configure the database URL, JWT secret, token expiration settings, and any other variables required by your application.

Example format:

```env
DATABASE_URL=postgresql+psycopg://<DB_USER>:<DB_PASSWORD>@localhost:5432/order_fulfillment_db
SECRET_KEY=<YOUR_SECRET_KEY>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Use the actual variable names expected by `app/core/config.py` or your configuration module. Do not commit real credentials or secrets to GitHub.

### Step 5: Run database migrations

Apply existing Alembic migrations:

```bash
alembic upgrade head
```

Check whether model changes require a migration:

```bash
alembic check
```

If new model changes need a migration, create one:

```bash
alembic revision --autogenerate -m "describe schema changes"
alembic upgrade head
```

Review generated migration files before applying them.

### Step 6: Start the API

```bash
uvicorn app.main:app --reload
```

The local API should be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

ReDoc documentation:

```text
http://localhost:8000/redoc
```

## 8. Docker Setup

If Docker Compose is configured for your project, run:

```bash
docker compose up --build
```

Check the container status:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f api
```

Stop the containers:

```bash
docker compose down
```

To remove the database volume as well, use `docker compose down -v` only when you intentionally want to delete the persisted database data.

Ensure that database migrations are applied as part of your startup workflow or run them explicitly using your configured container setup.

## 9. API Endpoints

The following is a summary of the expected API groups. Verify each route in `/docs` before submission.

| Module | Example endpoints |
|---|---|
| Authentication | `/api/auth/register`, `/api/auth/login`, `/api/auth/me` |
| Products | `/api/products` |
| Warehouses | `/api/warehouses` |
| Inventory | `/api/inventory`, `/api/inventory/adjust`, `/api/inventory/transfer` |
| Orders | `/api/orders` |
| Fulfillment | `/api/orders/{order_id}/assign` |
| Returns | `/api/returns` |
| Notifications | `/api/notifications` |
| Audit logs | `/api/audit-logs` |
| Dashboard | `/api/dashboard/admin` |
| Payments | `/api/payments/{order_id}/confirm` |

Refer to the Swagger UI for supported methods, request schemas, query parameters, authorization requirements, and response formats.

## 10. Authentication Example

Register a customer using the registration request schema exposed by Swagger.

Log in using:

```text
POST /api/auth/login
```

Use the returned access token to authorize protected requests:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

For protected endpoints, use a valid token belonging to a user with the required permissions.

## 11. Database Design

The database includes the following core entities:

- Users and roles
- Products and categories
- Warehouses and warehouse-user assignments
- Inventory and inventory transactions
- Orders and order items
- Order status history and assignments
- Returns and return items
- Notifications and audit logs
- Refresh tokens and idempotency keys

Primary keys, foreign keys, uniqueness constraints, indexes, and appropriate validation constraints maintain data integrity.

See `docs/database-schema.png` for the ER diagram.

## 12. Architecture

The application follows a layered architecture:

```text
Client / Postman
       |
       v
FastAPI Routers
       |
       v
Dependencies and Authorization
       |
       v
Service Layer
       |
       v
Repository Layer
       |
       v
SQLAlchemy Models
       |
       v
PostgreSQL
```

- **Routers:** Define HTTP endpoints and request/response handling.
- **Dependencies:** Provide authentication, database sessions, and permission checks.
- **Services:** Implement business rules and transaction workflows.
- **Repositories:** Encapsulate database queries.
- **Models:** Define database tables and relationships.
- **PostgreSQL:** Persist application data.

See `docs/architecture-diagram.png` for the architecture diagram.

## 13. Inventory Concurrency and Transactions

Inventory operations must preserve data consistency when requests run simultaneously.

The implementation should use:

- Database transactions for related inventory and order updates.
- Row-level locking, such as `SELECT ... FOR UPDATE`, where supported.
- Quantity validation to prevent negative stock.
- Database constraints to protect important invariants.
- Deterministic row-locking order for transfers between warehouses.
- Rollback when a business operation fails.

For example, if two customers try to reserve the same available stock, the system must prevent both requests from reserving more stock than is available.

## 14. Idempotency

Critical operations, such as order creation, inventory adjustment, inventory transfer, and payment confirmation, should support idempotency where implemented.

An idempotency key identifies a logical request. Repeating the same request with the same key should not execute the business operation twice.

The implementation should also reject reuse of a key with a different request payload and use database uniqueness constraints to handle concurrent requests safely.

## 15. Order Lifecycle

The intended order lifecycle is:

```text
Pending
   |
Confirmed
   |
Processing
   |
Packed
   |
Shipped
   |
Delivered
```

Eligible orders may also transition to alternative states such as `Cancelled` or `Failed`. Returned orders follow the application's return workflow.

Invalid status transitions should be rejected, and status history should be recorded.

## 16. Error Handling

The API uses centralized error handling for consistent error responses.

Example:

```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_INVENTORY",
    "message": "Insufficient inventory for the requested product"
  }
}
```

The API should distinguish validation errors, authentication failures, permission errors, missing resources, business conflicts, and unexpected server errors.

## 17. Running Tests

Run the automated test suite:

```bash
pytest -v
```

Run tests with coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

Configure a dedicated test database using the environment variables expected by `tests/conftest.py`. Never run destructive test setup against your production database.

Important test scenarios include authentication, role permissions, product validation, inventory reservations, transfers, order calculations, cancellations, return transitions, idempotency, and concurrent inventory requests.

## 18. Postman Testing

Import the collection and environment files from the `postman/` directory.

Configure the local environment with:

```text
base_url = http://localhost:8000
```

Authenticate before calling protected endpoints and store tokens using Postman's test scripts if configured.

Test both successful and unsuccessful scenarios, including insufficient inventory, invalid state transitions, unauthorized access, and duplicate idempotency keys.

## 19. Future Improvements

Potential extensions include:

- Celery and Redis for background jobs.
- Email notifications.
- Distributed locking where necessary.
- API rate limiting.
- CSV reporting and exports.
- Structured logging and monitoring.
- CI/CD automation.

## 20. Author and Repository

**Author:** Sridhar Tekam

**GitHub Repository:** `<https://github.com/tekamsridhar-dot/Order-Fullfillment-Inventory-Management->`

This project was developed as a backend engineering assignment to demonstrate API design, database modeling, authentication, authorization, inventory control, order processing, transaction management, and automated testing.
