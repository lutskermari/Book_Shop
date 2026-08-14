Set-Content -Path README.md -Encoding utf8 -Value @"
# 📚 Book Shop & Analytics Platform — Microservices Architecture

A distributed web platform consisting of two Django-based microservices: an e-commerce Bookstore (**Project A**) and a dedicated Analytics Service (**Project B**), communicating via REST API with asynchronous background task processing.

![CI/CD](https://github.com/lutskermari/Book_Shop/actions/workflows/django.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-83%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/django-4.2+-green)
![DRF](https://img.shields.io/badge/DRF-3.15+-red)
![Docker](https://img.shields.io/badge/docker-ready-blue)

---

## 🏗 System Architecture & Microservices

\`\`\`
                       +-------------------------------+
                       |        NGINX (Gateway)        |
                       +---------------+---------------+
                                       |
                     +-----------------+-----------------+
                     |                                   |
                     v (Port 8000)                       v (Port 8001)
     +-------------------------------+   REST API    +-------------------------------+
     |     Project A: Book Store     | ------------> |  Project B: Analytics Service |
     |      (Django 4.2+ / Gunicorn) | (Sales Event) |    (Django REST Framework)    |
     +---------------+---------------+               +---------------+---------------+
                     |                                               |
     +---------------+---------------+                               |
     |               |               |                               |
     v               v               v                               v
+----------+   +-----------+   +-----------+                   +-----------+
| Postgres |   |   Redis   |   |  Celery   |                   | Postgres  |
| (Main DB)|   | (Cache/MQ)|   | (Worker)  |                   | (Analytics|
+----------+   +-----------+   +-----------+                   +-----------+
\`\`\`

### 1. Project A — Main Bookstore (\`mysite\`)
- **Port:** \`8000\`
- **Core Functionality:** Book catalog, search & filtering, Many-to-Many categories, session cart, Stripe checkout, user auth & profiles.
- **Inter-service Communication:** Dispatches real-time sales data to Project B upon completed order placement with built-in error handling and fallback logging.

### 2. Project B — Analytics & Tracking Service (\`analytics_service\`)
- **Port:** \`8001\`
- **Core Functionality:** Dedicated microservice for processing and aggregating sales metrics, revenue analytics, and top-selling book statistics.
- **Security:** Protected API endpoints utilizing Django REST Framework permissions (\`IsAdminUser\` / internal service secret headers).

---

## 🚀 Tech Stack

- **Backend:** Django 4.2+, Django REST Framework (DRF), Python 3.12, Gunicorn
- **Database:** PostgreSQL 16 (Independent databases for isolated services)
- **Task Queue & Caching:** Redis 7, Celery
- **Payment & Third-Party:** Stripe Checkout API, Google OAuth2
- **Documentation & Tools:** Swagger / OpenAPI (\`drf-spectacular\`), Sentry SDK
- **Containerization & Gateway:** Docker Compose, NGINX
- **Testing & Code Quality:** pytest, factory-boy, Black, Flake8, Coverage (83%)
- **i18n:** Ukrainian (\`uk\`) & English (\`en\`)

---

## 📋 Features

- Multi-service architecture with decoupled analytics data pipeline.
- Book catalog with search, filtering, and Many-to-Many categories.
- Session-based shopping cart with atomic order processing.
- Order creation with Stripe payment and automated email confirmation.
- Custom User model with extended profiles, avatar support, and phone numbers.
- Google OAuth2 authentication and role-based permissions (Manager / Admin / User).
- Internationalization (i18n) supporting Ukrainian and English.
- Redis-backed cache layer for high-throughput endpoints.
- Celery background workers for email delivery and async tasks.
- Interactive OpenAPI / Swagger documentation for all API routes.

---

## 🛠 Installation & Setup

### Requirements
- Docker Desktop
- Git

### Setup Steps

\`\`\`bash
# 1. Clone repository
git clone https://github.com/lutskermari/Book_Shop.git
cd Book_Shop

# 2. Configure environment
cp .env.example .env

# 3. Build and launch all containers
docker-compose up --build
\`\`\`

### 🔗 Service Access Points
- **Project A (Storefront):** http://localhost:8000
- **Project A (Admin):** http://localhost:8000/admin
- **Project A (Swagger API Docs):** http://localhost:8000/api/docs/
- **Project B (Analytics Summary API):** http://localhost:8001/api/analytics/summary/
- **Project B (Analytics Admin):** http://localhost:8001/admin/

---

## ⚙️ Environment Variables (\`.env\`)

\`\`\`ini
# Core Configuration
SECRET_KEY=your-secret-key
DEBUG=True

# Database: Project A
POSTGRES_DB=bookshop
POSTGRES_USER=bookshop_user
POSTGRES_PASSWORD=bookshop_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Database: Project B (Analytics)
ANALYTICS_DB_NAME=analytics_db
ANALYTICS_DB_USER=analytics_user
ANALYTICS_DB_PASSWORD=analytics_password
ANALYTICS_DB_HOST=analytics_db
ANALYTICS_DB_PORT=5432

# Redis & Celery
REDIS_URL=redis://redis:6379/0

# Payment & Auth Integrations
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
\`\`\`

---

## 🌐 API & Inter-Service Endpoints

### 🛒 Project A (Book Store)
| Method | Endpoint | Description |
|---|---|---|
| \`GET\` | \`/api/schema/\` | OpenAPI schema definition |
| \`GET\` | \`/api/docs/\` | Swagger UI documentation |
| \`GET\` | \`/api/books/\` | List all books (JSON API) |
| \`GET\` | \`/api/books/<id>/\` | Book detail (JSON API) |
| \`POST\` | \`/api/auth/token/\` | JWT token obtain pair |
| \`POST\` | \`/api/auth/token/refresh/\` | JWT token refresh |

### 📊 Project B (Analytics Service)
| Method | Endpoint | Access Level | Description |
|---|---|---|---|
| \`POST\` | \`/api/analytics/track-sale/\` | Internal Service | Records a completed sale transaction |
| \`GET\` | \`/api/analytics/summary/\` | Admin / Staff | Aggregated metrics, total revenue, and top books |

---

## 🧪 Testing & Code Quality

\`\`\`bash
# Run pytest test suite
docker-compose exec web pytest tests/ -v

# Run with test coverage report
docker-compose exec web pytest tests/ --cov=bookshop --cov-report=term-missing

# Code formatting and static lint checks
black mysite analytics_service
flake8 mysite analytics_service --max-line-length=88 --extend-ignore=E203,W503 --exclude=*/migrations/*
\`\`\`

---

## 📁 Project Structure

\`\`\`text
Book_Shop/
├── mysite/                        # 🛒 PROJECT A: Bookstore Main Service
│   ├── bookshop/                  # Catalog, Cart, Orders & Services
│   │   ├── services.py            # Microservice client (HTTP to Project B)
│   │   ├── models.py              # Book, Category, Order, OrderItem
│   │   ├── views.py               # CBV with i18n & caching support
│   │   ├── cart.py                # Session-based cart
│   │   └── middleware.py          # Request & login audit logging
│   ├── users/                     # Custom User model, profile & avatars
│   ├── settings/                  # Modular settings (base, dev, prod)
│   ├── locale/                    # Translation catalogs (uk / en)
│   ├── tests/                     # Pytest test suite & factory fixtures
│   └── manage.py
│
├── analytics_service/             # 📊 PROJECT B: Analytics Microservice
│   ├── api/                       # DRF Views, Serializers, Analytics Models
│   │   ├── models.py              # SaleAnalytics schema
│   │   ├── views.py               # TrackSaleView, AnalyticsSummaryView
│   │   └── permissions.py         # Custom permission classes
│   ├── analytics/                 # Project configuration & settings
│   └── manage.py
│
├── nginx/                         # Reverse proxy configuration
├── docker-compose.yml             # Container orchestration
├── .env.example
├── README.md
├── AI_REVIEW.md
└── AI_PROMPTS.md
\`\`\`

---

## 🤖 AI Usage

This project used **Claude AI (claude.ai)** to improve code quality, generate tests, and create documentation.

### Code Review
AI reviewed complex views and suggested optimizations:
- Replaced direct queries with \`get_object_or_404()\` for robust error handling.
- Moved Stripe checkout session initialization outside database transactions.
- Added strict HTTP method decorators and double payment guardrails.

### Test Generation
AI generated test suites for models (\`Book\`, \`Order\`, \`OrderItem\`, \`Category\`) using \`factory-boy\` fixtures with full edge-case coverage.

### Documentation
Automated docstring generation conforming to the Google Python Style Guide across all view sets and handlers.
"@