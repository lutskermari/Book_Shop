# AI Code Review — Book Shop Project

## Overview
Code review was conducted using Claude AI for 3 complex views:
1. `order_create` — order creation with Stripe payment
2. `cart_add` / `cart_remove` — cart management
3. `order_success` — payment success handler

---

## View 1: `order_create`

### Original Code
```python
def order_create(request):
    cart = Cart(request)
    if not cart:
        return redirect('cart_detail')

    if request.method == "POST":
        with transaction.atomic():
            order = Order.objects.create(
                first_name=request.POST["first_name"],
                last_name=request.POST["last_name"],
                email=request.POST["email"],
                address=request.POST["address"],
            )
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    book=item["book"],
                    price=item["price"],
                    quantity=item["quantity"],
                )

            payment_url = create_payment_session(request, order)

        cart.clear()
        return redirect(payment_url, code=303)

    return render(request, "order_create.html", {"cart": cart})
```

### AI Recommendations
> **Prompt used:** "Review this Django view for potential issues with error handling, security, and code quality. Suggest improvements."

1. **Critical:** `create_payment_session` is called inside `transaction.atomic()`. If Stripe fails, the transaction rolls back but the Stripe request has already been sent — this can cause data inconsistency.
2. **Missing:** No logging for failed order creation.
3. **Suggestion:** Move Stripe session creation outside the atomic block.

### Final Code
```python
def order_create(request):
    """
    Creates an order from cart items.
    Uses transaction.atomic for data integrity.
    Stripe session is created OUTSIDE the transaction to avoid inconsistency.
    """
    cart = Cart(request)
    if not cart:
        return redirect('cart_detail')

    if request.method == "POST":
        with transaction.atomic():
            order = Order.objects.create(
                first_name=request.POST["first_name"],
                last_name=request.POST["last_name"],
                email=request.POST["email"],
                address=request.POST["address"],
            )
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    book=item["book"],
                    price=item["price"],
                    quantity=item["quantity"],
                )
            logger.info(f"Замовлення #{order.id} створено | user: {request.user}")

        # Outside atomic — so rollback does not affect Stripe
        payment_url = create_payment_session(request, order)
        cart.clear()
        return redirect(payment_url, code=303)

    return render(request, "order_create.html", {"cart": cart})
```

### Changes Applied
- ✅ Moved `create_payment_session` outside `transaction.atomic()`
- ✅ Added logging after order creation

---

## View 2: `cart_add` / `cart_remove`

### Original Code
```python
def cart_add(request, book_id):
    cart = Cart(request)
    book = Book.objects.get(id=book_id)
    quantity = int(request.POST.get("quantity", 1))
    cart.add(book=book, quantity=quantity)
    return redirect("cart_detail")

def cart_remove(request, book_id):
    cart = Cart(request)
    book = Book.objects.get(id=book_id)
    cart.remove(book)
    return redirect("cart_detail")
```

### AI Recommendations
> **Prompt used:** "What are the potential problems with this Django view? Check for missing validations and best practices."

1. **Critical:** `Book.objects.get()` raises `DoesNotExist` exception if book not found — returns 500 error instead of 404.
2. **Missing:** `@require_POST` decorator — GET requests should not modify data.
3. **Suggestion:** Use `get_object_or_404` and add `@require_POST`.

### Final Code
```python
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST


@require_POST
def cart_add(request, book_id):
    """
    Adds a book to the session-based cart.
    Only accepts POST requests.
    Returns 404 if book does not exist.
    """
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    quantity = int(request.POST.get("quantity", 1))
    cart.add(book=book, quantity=quantity)
    return redirect("cart_detail")


@require_POST
def cart_remove(request, book_id):
    """
    Removes a book from the session-based cart.
    Only accepts POST requests.
    Returns 404 if book does not exist.
    """
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    cart.remove(book)
    return redirect("cart_detail")
```

### Changes Applied
- ✅ Replaced `Book.objects.get()` with `get_object_or_404()`
- ✅ Added `@require_POST` decorator to both views

---

## View 3: `order_success`

### Original Code
```python
def order_success(request):
    order = Order.objects.get(id=request.GET.get('order_id'))
    
    order.paid = True
    order.save()
    
    send_mail(
        subject=f"Замовлення #{order.id} успішно оплачено!",
        message=f"Дякуємо за оплату замовлення на суму {order.get_total_cost()} грн.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[order.email],
    )
    
    return render(request, "order_success.html", {"order": order})
```

### AI Recommendations
> **Prompt used:** "Analyze this code for security issues and edge cases. Check for potential double payment processing."

1. **Critical:** `Order.objects.get()` raises 500 if order_id is invalid or missing.
2. **Critical:** No protection against double payment — refreshing the page sends the email again.
3. **Suggestion:** Use `get_object_or_404` and check `if not order.paid` before processing.

### Final Code
```python
def order_success(request):
    """
    Handles successful Stripe payment.
    Protected against double processing via order.paid check.
    Sends confirmation email only once.
    """
    order = get_object_or_404(Order, id=request.GET.get('order_id'))

    if not order.paid:
        order.paid = True
        order.save()
        logger.info(f"Замовлення #{order.id} оплачено")
        send_mail(
            subject=f"Замовлення #{order.id} успішно оплачено!",
            message=f"Дякуємо за оплату на суму {order.get_total_cost()} грн.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.email],
        )

    return render(request, "order_success.html", {"order": order})
```

### Changes Applied
- ✅ Replaced `Order.objects.get()` with `get_object_or_404()`
- ✅ Added `if not order.paid` check to prevent double processing
- ✅ Added logging

---

## Summary of All Changes

| Issue | Severity | Fixed |
|-------|----------|-------|
| Stripe called inside `transaction.atomic()` | Critical | ✅ |
| `Book.objects.get()` without 404 handling | High | ✅ |
| `Order.objects.get()` without 404 handling | High | ✅ |
| Double payment processing possible | High | ✅ |
| Missing `@require_POST` on cart views | Medium | ✅ |
| Missing docstrings | Low | ✅ |

---

## AI Tool Used
- **Tool:** Claude (claude.ai)
- **Model:** Claude Sonnet
- **Date:** July 2026
