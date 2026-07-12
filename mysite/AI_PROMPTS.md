# AI Prompts Used in Book Shop Project

**AI Tool:** Claude (claude.ai)  
**Model:** Claude Sonnet 4.6  
**Purpose:** Code review, test generation, documentation

---

## 1. Code Review Prompts

```
Review these Django views for potential issues with error handling,
security, and code quality. Suggest improvements:
[paste views code]
```

```
What are the potential problems with this Django view?
Check for N+1 queries, missing validations, and best practices:
[paste cart views code]
```

```
Analyze this code for security issues and edge cases.
Check for potential double payment processing:
[paste order_success code]
```

---

## 2. Test Generation Prompts

```
Generate pytest tests for Django models: Category, Book, Order, OrderItem.
Use factory-boy for fixtures. Include edge cases.
Add comment "# Generated with AI, reviewed and modified" to each test.
```

```
Write integration tests for Django cart and order views.
Mock external services like Stripe and email using unittest.mock.
```

```
Generate unit tests for Django forms: CustomUserCreationForm, UserProfileForm.
Test valid and invalid data cases.
```

---

## 3. Documentation Prompts

```
Generate docstrings for all views in this Django file.
Follow Google Python Style Guide format.
Include Args and Returns sections:
[paste views.py code]
```

```
Write a professional README.md for a Django bookstore project with:
Docker, PostgreSQL, Redis, Stripe, pytest, factory-boy, i18n.
Include installation instructions, env variables, and project structure.
```

```
Create an AI_REVIEW.md file documenting code review process.
Include: original code, AI recommendations, final improved code,
and a summary table of all changes.
```

---