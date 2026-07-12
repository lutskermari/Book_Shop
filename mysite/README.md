# 📚 Book Shop — Django Bookstore Project

A full-featured bookstore web application built with Django, PostgreSQL, Redis, and Stripe payment integration.

## 🚀 Tech Stack

- **Backend:** Django 6.0, Python 3.12
- **Database:** PostgreSQL 16
- **Cache & Sessions:** Redis 7
- **Payment:** Stripe Checkout
- **Containerization:** Docker, Docker Compose
- **Testing:** pytest, factory-boy, coverage 83%
- **i18n:** Ukrainian + English

## 📋 Features

- Book catalog with search and categories
- Session-based shopping cart
- Order creation with Stripe payment
- Email confirmation after payment
- User registration and authentication
- Google OAuth login
- Role-based access (Manager / User)
- Admin panel with inline OrderItems
- Async views for API endpoints
- Custom middleware (request logging, login logging)
- Internationalization (Ukrainian/English)

## 🛠 Installation

### Requirements
- Docker Desktop
- Git

### Setup

```bash
# Clone repository
git clone https://github.com/lutskermari/Book_Shop.git
cd Book_Shop

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Build and run
docker-compose up --build
```

### Access
- App: http://localhost:8000
- Admin: http://localhost:8000/admin (admin/admin)

## ⚙️ Environment Variables

```
SECRET_KEY=your-secret-key
DEBUG=True
POSTGRES_DB=bookshop
POSTGRES_USER=bookshop_user
POSTGRES_PASSWORD=bookshop_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/0
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

## 🧪 Testing

```bash
# Run all tests
docker-compose exec web pytest tests/ -v

# Run with coverage
docker-compose exec web pytest tests/ --cov=bookshop --cov-report=term-missing
```

**Coverage: 83%** ✅

## 📁 Project Structure

```
Book_Shop/
  mysite/
    bookshop/          # Main app
      models.py        # Book, Category, Order, OrderItem
      views.py         # All views with docstrings
      cart.py          # Session-based cart
      admin.py         # Admin with inlines
      middleware.py    # Request & login logging
      async_views.py   # Async API views
    users/             # Auth app
    tests/             # pytest tests
    locale/            # i18n translations
  docker-compose.yml
  AI_REVIEW.md
  AI_PROMPTS.md
```

## 🌐 API Endpoints (Async)

| URL | Description |
|-----|-------------|
| `/api/books/` | List all books (JSON) |
| `/api/books/<id>/` | Book detail (JSON) |
| `/api/stats/` | Catalog statistics (JSON) |

---

## 🤖 AI Usage

This project used **Claude AI (claude.ai)** to improve code quality, generate tests, and create documentation.

---

### Code Review

AI reviewed 3 complex views and suggested improvements.

**Prompts used:**
```
Review these Django views for potential issues with error handling,
security, and code quality. Suggest improvements.
```
```
Analyze this code for security issues and edge cases.
Check for potential double payment processing.
```
```
What are the potential problems with this Django view?
Check for missing validations and best practices.
```

**Changes applied based on AI recommendations:**
- Replaced `Book.objects.get()` with `get_object_or_404()` to handle 404 properly
- Moved Stripe session creation outside `transaction.atomic()` to avoid data inconsistency
- Added `@require_POST` decorator to cart views
- Added double payment protection in `order_success`

See full details in [AI_REVIEW.md](AI_REVIEW.md)

---

### Test Generation

AI generated tests for models: `Book`, `Order`, `OrderItem`, `Category`.

**Prompt used:**
```
Generate pytest tests for Django models: Category, Book, Order, OrderItem.
Use factory-boy for fixtures. Include edge cases.
Add comment "# Generated with AI, reviewed and modified" to each test.
```

All generated tests were reviewed and modified manually before use.

---

### Documentation

AI generated docstrings for all views in `bookshop/views.py`.

**Prompt used:**
```
Generate docstrings for all views in this Django file.
Follow Google Python Style Guide format.
Include Args and Returns sections.
```

---
