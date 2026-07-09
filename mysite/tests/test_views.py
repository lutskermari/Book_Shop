import pytest
from django.urls import reverse
from unittest.mock import patch
from tests.factories import OrderFactory


@pytest.mark.django_db
class TestIndexView:
    def test_status_200(self, client):
        assert client.get(reverse("index")).status_code == 200


@pytest.mark.django_db
class TestBookDetailView:
    def test_404_for_missing(self, client):
        response = client.get(reverse("book_detail", kwargs={"pk": 9999}))
        assert response.status_code == 404


@pytest.mark.django_db
class TestBookCreateView:
    def test_redirects_anonymous(self, client):
        response = client.get(reverse("book_create"))
        assert response.status_code == 302


@pytest.mark.django_db
class TestCartViews:
    def test_cart_detail_200(self, client):
        assert client.get(reverse("cart_detail")).status_code == 200


@pytest.mark.django_db
class TestOrderViews:
    @patch("bookshop.views.send_mail")
    def test_order_success(self, mock_mail, client):
        order = OrderFactory()
        response = client.get(reverse("order_success") + f"?order_id={order.pk}")
        assert response.status_code == 200
        assert mock_mail.called