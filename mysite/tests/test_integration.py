import pytest
from django.urls import reverse
from decimal import Decimal
from unittest.mock import patch, MagicMock
from tests.factories import BookFactory, OrderFactory, OrderItemFactory, UserFactory


@pytest.mark.django_db
class TestAuthFlow:
    def test_register_page_loads(self, client):
        response = client.get("/uk/register/")
        assert response.status_code == 200

    def test_user_registers_successfully(self, client):
        from django.contrib.auth import get_user_model
        client.post(reverse("register"), {
            "username": "newuser",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        assert get_user_model().objects.filter(username="newuser").exists()

    def test_user_logs_in(self, client):
        user = UserFactory(username="loginuser")
        response = client.post(reverse("login"), {
            "username": "loginuser",
            "password": "testpass123",
        })
        assert response.status_code == 302

    def test_wrong_password_stays_on_login(self, client):
        UserFactory(username="someuser")
        response = client.post(reverse("login"), {
            "username": "someuser",
            "password": "wrongpass",
        })
        assert response.status_code == 200

    def test_logout_redirects(self, client):
        user = UserFactory()
        client.login(username=user.username, password="testpass123")
        response = client.get(reverse("logout"))
        assert response.status_code == 302


@pytest.mark.django_db
class TestCartFlow:
    def test_empty_cart_loads(self, client):
        assert client.get(reverse("cart_detail")).status_code == 200

    def test_add_book_appears_in_cart(self, client):
        book = BookFactory(title="Тестова книга")
        client.post(reverse("cart_add", kwargs={"book_id": book.pk}), {"quantity": 1})
        response = client.get(reverse("cart_detail"))
        assert "Тестова книга" in response.content.decode()

    def test_add_two_books(self, client):
        book1 = BookFactory(title="Книга А")
        book2 = BookFactory(title="Книга Б")
        client.post(reverse("cart_add", kwargs={"book_id": book1.pk}), {"quantity": 1})
        client.post(reverse("cart_add", kwargs={"book_id": book2.pk}), {"quantity": 1})
        content = client.get(reverse("cart_detail")).content.decode()
        assert "Книга А" in content
        assert "Книга Б" in content

    def test_remove_book_from_cart(self, client):
        book = BookFactory(title="Видалити мене")
        client.post(reverse("cart_add", kwargs={"book_id": book.pk}), {"quantity": 1})
        client.post(reverse("cart_remove", kwargs={"book_id": book.pk}))
        content = client.get(reverse("cart_detail")).content.decode()
        assert "Видалити мене" not in content

    def test_clear_removes_all(self, client):
        book = BookFactory(title="Очистити")
        client.post(reverse("cart_add", kwargs={"book_id": book.pk}), {"quantity": 1})
        client.get(reverse("cart_clear"))
        content = client.get(reverse("cart_detail")).content.decode()
        assert "Очистити" not in content


@pytest.mark.django_db
class TestOrderFlow:
    @patch("bookshop.views.stripe.checkout.Session.create")
    def test_order_created_in_db(self, mock_stripe, client):
        from bookshop.models import Order
        mock_stripe.return_value = MagicMock(url="https://stripe.com/pay")
        book = BookFactory()
        client.post(reverse("cart_add", kwargs={"book_id": book.pk}), {"quantity": 1})
        client.post(reverse("order_create"), {
            "first_name": "Тест",
            "last_name": "Юзер",
            "email": "flow@example.com",
            "address": "вул. Флоу 1",
        })
        assert Order.objects.filter(email="flow@example.com").exists()

    @patch("bookshop.views.stripe.checkout.Session.create")
    def test_order_items_created(self, mock_stripe, client):
        from bookshop.models import Order
        mock_stripe.return_value = MagicMock(url="https://stripe.com/pay")
        book = BookFactory()
        client.post(reverse("cart_add", kwargs={"book_id": book.pk}), {"quantity": 2})
        client.post(reverse("order_create"), {
            "first_name": "Тест",
            "last_name": "Юзер",
            "email": "items@example.com",
            "address": "вул. 1",
        })
        order = Order.objects.get(email="items@example.com")
        assert order.items.count() == 1
        assert order.items.first().quantity == 2

    @patch("bookshop.views.stripe.checkout.Session.create")
    def test_cart_empty_after_order(self, mock_stripe, client):
        mock_stripe.return_value = MagicMock(url="https://stripe.com/pay")
        book = BookFactory(title="Після замовлення")
        client.post(reverse("cart_add", kwargs={"book_id": book.pk}), {"quantity": 1})
        client.post(reverse("order_create"), {
            "first_name": "Тест",
            "last_name": "Юзер",
            "email": "clear@example.com",
            "address": "вул. 1",
        })
        content = client.get(reverse("cart_detail")).content.decode()
        assert "Після замовлення" not in content

    @patch("bookshop.views.send_mail")
    def test_order_paid_on_success(self, mock_mail, client):
        order = OrderFactory(paid=False)
        client.get(reverse("order_success") + f"?order_id={order.pk}")
        order.refresh_from_db()
        assert order.paid is True

    @patch("bookshop.views.send_mail")
    def test_email_sent_on_success(self, mock_mail, client):
        order = OrderFactory(email="notify@example.com")
        client.get(reverse("order_success") + f"?order_id={order.pk}")
        assert mock_mail.called

    @patch("bookshop.views.send_mail")
    def test_order_total_correct(self, mock_mail, client):
        order = OrderFactory()
        OrderItemFactory(order=order, price=Decimal("100.00"), quantity=3)
        assert order.get_total_cost() == Decimal("300.00")
