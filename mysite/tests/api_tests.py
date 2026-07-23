import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from bookshop.models import Book, Category, Order

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_factory():
    def make_user(username="test_user", password="password123", **kwargs):
        return User.objects.create_user(username=username, password=password, **kwargs)
    return make_user

@pytest.fixture
def admin_user(user_factory):
    return user_factory(username="admin_user", is_staff=True, is_superuser=True)

@pytest.fixture
def auth_client(api_client, user_factory):
    user = user_factory(username="auth_user", is_staff=True)
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client

@pytest.fixture
def category_factory():
    def make_category(name="Фантастика", slug=None):
        if not slug:
            slug = f"cat-{Category.objects.count() + 1}"
        return Category.objects.create(name=name, slug=slug)
    return make_category

@pytest.fixture
def book_factory(category_factory):
    def make_book(title="Тестова Книга", price="100.00", **kwargs):
        count = Book.objects.count() + 1
        book = Book.objects.create(
            title=f"{title} {count}" if title == "Тестова Книга" else title,
            author=kwargs.get('author', 'Автор'),
            price=price,
            description=kwargs.get('description', 'Опис книги'),
            stock=kwargs.get('stock', True)
        )
        cat = kwargs.get('category') or category_factory()
        book.category.add(cat)
        return book

    def create_batch(size):
        return [make_book() for _ in range(size)]
    
    make_book.create_batch = create_batch
    return make_book

@pytest.fixture
def order_factory():
    def make_order(email="user@example.com"):
        return Order.objects.create(
            first_name="Іван",
            last_name="Тестовий",
            email=email,
            address="Київ, вул. Хрещатик"
        )
    return make_order

@pytest.fixture
def regular_auth_client(api_client, user_factory):
    user = user_factory(username="regular_user", is_staff=False)
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def auth_client(api_client, user_factory):
    user = user_factory(username="auth_user", is_staff=True)
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
def test_jwt_obtain_token_success(api_client, user_factory):
    user_factory(username="jwt_user", password="password123")
    url = reverse('token_obtain_pair')
    response = api_client.post(url, {'username': 'jwt_user', 'password': 'password123'})
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data

@pytest.mark.django_db
def test_jwt_obtain_token_invalid_credentials(api_client, user_factory):
    user_factory(username="jwt_user", password="password123")
    url = reverse('token_obtain_pair')
    response = api_client.post(url, {'username': 'jwt_user', 'password': 'wrong_password'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_jwt_verify_token(api_client, user_factory):
    user_factory(username="jwt_user", password="password123")
    token_res = api_client.post(reverse('token_obtain_pair'), {'username': 'jwt_user', 'password': 'password123'})
    access_token = token_res.data['access']
    
    verify_res = api_client.post(reverse('token_verify'), {'token': access_token})
    assert verify_res.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_jwt_refresh_token(api_client, user_factory):
    user_factory(username="jwt_user", password="password123")
    token_res = api_client.post(reverse('token_obtain_pair'), {'username': 'jwt_user', 'password': 'password123'})
    refresh_token = token_res.data['refresh']
    
    refresh_res = api_client.post(reverse('token_refresh'), {'refresh': refresh_token})
    assert refresh_res.status_code == status.HTTP_200_OK
    assert 'access' in refresh_res.data

@pytest.mark.django_db
def test_unauthenticated_request_to_protected_endpoint(api_client):
    url = reverse('api_categories-list')
    response = api_client.post(url, {'name': 'New Cat', 'slug': 'new-cat'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_get_books_list_pagination(api_client, book_factory):
    book_factory.create_batch(25) 
    url = reverse('api_books-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 25
    assert len(response.data['results']) == 20 

@pytest.mark.django_db
def test_filter_books_by_price(api_client, book_factory):
    book_factory(title="Cheap", price=50.00)
    book_factory(title="Expensive", price=500.00)
    url = f"{reverse('api_books-list')}?min_price=100&max_price=600"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert response.data['results'][0]['title'] == "Expensive"

@pytest.mark.django_db
def test_search_books_by_title(api_client, book_factory):
    book_factory(title="Cyberpunk 2077")
    book_factory(title="The Witcher")
    url = f"{reverse('api_books-list')}?search=Witcher"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1

@pytest.mark.django_db
def test_ordering_books_by_price_desc(api_client, book_factory):
    book_factory(price="100.00")
    book_factory(price="900.00")
    url = f"{reverse('api_books-list')}?ordering=-price"
    response = api_client.get(url)
    assert float(response.data['results'][0]['price']) == 900.00

@pytest.mark.django_db
def test_get_book_detail_api(api_client, book_factory):
    book = book_factory(title="Dune")
    url = reverse('api_books-detail', args=[book.id])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == "Dune"

@pytest.mark.django_db
def test_create_book_authenticated(auth_client, category_factory):
    cat = category_factory()
    url = reverse('api_books-list')
    data = {
        'title': 'New Book',
        'author': 'Author',
        'price': '120.00',
        'description': 'Desc',
        'category_ids': [cat.id]
    }
    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_update_book_authenticated(auth_client, book_factory):
    book = book_factory(title="Old Title")
    url = reverse('api_books-detail', args=[book.id])
    response = auth_client.patch(url, {'title': 'Updated Title'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'Updated Title'

@pytest.mark.django_db
def test_delete_book_authenticated(auth_client, book_factory):
    book = book_factory()
    url = reverse('api_books-detail', args=[book.id])
    response = auth_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
def test_regular_user_cannot_create_category(regular_auth_client):
    url = reverse('api_categories-list')
    response = regular_auth_client.post(url, {'name': 'Sci-Fi', 'slug': 'sci-fi'})
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_admin_user_can_create_category(admin_client):
    url = reverse('api_categories-list')
    response = admin_client.post(url, {'name': 'Sci-Fi', 'slug': 'sci-fi'})
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_get_categories_list_open_for_all(api_client, category_factory):
    category_factory()
    url = reverse('api_categories-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_admin_can_delete_category(admin_client, category_factory):
    cat = category_factory()
    url = reverse('api_categories-detail', args=[cat.id])
    response = admin_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
def test_orders_list_forbidden_for_regular_user(regular_auth_client):
    url = reverse('api_orders-list')
    response = regular_auth_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_orders_list_accessible_for_admin(admin_client, order_factory):
    order_factory()
    url = reverse('api_orders-list')
    response = admin_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_api_cart_empty_get(api_client):
    url = reverse('api_cart')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['total_price'] == 0

@pytest.mark.django_db
def test_api_cart_add_item(api_client, book_factory):
    book = book_factory(price="100.00")
    url = reverse('api_cart')
    response = api_client.post(url, {'book_id': book.id, 'quantity': 2})
    assert response.status_code == status.HTTP_201_CREATED
    
    cart_res = api_client.get(url)
    assert cart_res.data['total_price'] == 200.00

@pytest.mark.django_db
def test_api_cart_invalid_book_id(api_client):
    url = reverse('api_cart')
    response = api_client.post(url, {'book_id': 9999, 'quantity': 1})
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_api_create_order_flow(api_client, book_factory):
    book = book_factory(price="150.00")
    api_client.post(reverse('api_cart'), {'book_id': book.id, 'quantity': 1})
    
    order_data = {
        'first_name': 'Олена',
        'last_name': 'Петрова',
        'email': 'olena@test.com',
        'address': 'Львів'
    }
    response = api_client.post(reverse('api_orders-list'), order_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Order.objects.filter(email='olena@test.com').exists()

@pytest.mark.django_db
def test_swagger_docs_endpoint_status(api_client):
    url = reverse('swagger-ui')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_openapi_schema_generation(api_client):
    url = reverse('schema')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "openapi" in response.data