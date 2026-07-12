import pytest
from decimal import Decimal
from tests.factories import CategoryFactory, BookFactory, OrderFactory, OrderItemFactory


@pytest.mark.django_db
class TestCategoryModel:
    def test_str(self):
        cat = CategoryFactory(name="Програмування")
        assert str(cat) == "Програмування"

    def test_slug_saved(self):
        cat = CategoryFactory(slug="programming")
        assert cat.slug == "programming"

    def test_unique_slug(self):
        CategoryFactory(slug="unique-slug")
        with pytest.raises(Exception):
            CategoryFactory(slug="unique-slug")


@pytest.mark.django_db
class TestBookModel:

    def test_str(self):
        book = BookFactory(title="Python")
        assert str(book) == "Python"

    def test_price_decimal(self):
        book = BookFactory(price=Decimal("199.99"))
        assert book.price == Decimal("199.99")

    def test_stock_default_true(self):
        book = BookFactory()
        assert book.stock is True

    def test_no_published_date(self):
        book = BookFactory()
        assert book.published_date is None

@pytest.mark.django_db
class TestOrderModel:
    def test_str_contains_id(self):
        order = OrderFactory()
        assert str(order.id) in str(order)

    def test_paid_default_false(self):
        order = OrderFactory()
        assert order.paid is False

    def test_total_cost_empty(self):
        order = OrderFactory()
        assert order.get_total_cost() == 0

    def test_total_cost_with_items(self):
        order = OrderFactory()
        OrderItemFactory(order=order, price=Decimal("100.00"), quantity=3)
        assert order.get_total_cost() == Decimal("300.00")

    def test_created_at_auto(self):
        order = OrderFactory()
        assert order.created_at is not None

    def test_order_email_field(self):
        #Перевіряє що email зберігається коректно в моделі Order
        order = OrderFactory(email="test@example.com")
        assert order.email == "test@example.com"

    def test_order_first_last_name(self):
        #Перевіряє що ім'я та прізвище зберігаються коректно
        order = OrderFactory(first_name="Марія", last_name="Луцкер")
        assert order.first_name == "Марія"
        assert order.last_name == "Луцкер"


@pytest.mark.django_db
class TestOrderItemModel:
    def test_str(self):
        book = BookFactory(title="Django Book")
        item = OrderItemFactory(book=book, quantity=2)
        assert "Django Book" in str(item)
        assert "2" in str(item)

    def test_get_cost(self):
        item = OrderItemFactory(price=Decimal("150.00"), quantity=3)
        assert item.get_cost() == Decimal("450.00")

    def test_quantity_default(self):
        item = OrderItemFactory()
        assert item.quantity == 1

    def test_order_item_order_relation(self):
        #Перевіряє що OrderItem правильно пов'язаний з Order через ForeignKey
        order = OrderFactory()
        item = OrderItemFactory(order=order)
        assert item.order == order
