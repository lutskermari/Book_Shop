import factory
from decimal import Decimal
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "bookshop.Category"

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "bookshop.Book"

    title = factory.Sequence(lambda n: f"Book {n}")
    author = factory.Sequence(lambda n: f"Author {n}")
    price = Decimal("299.00")
    description = "Test description"
    stock = True

    @factory.post_generation
    def category(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for cat in extracted:
                self.category.add(cat)


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "bookshop.Order"

    first_name = "User"
    last_name = "Name"
    email = factory.Sequence(lambda n: f"order_{n}@example.com")
    address = "st. Sunny"
    paid = False


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "bookshop.OrderItem"

    order = factory.SubFactory(OrderFactory)
    book = factory.SubFactory(BookFactory)
    price = Decimal("299.00")
    quantity = 1