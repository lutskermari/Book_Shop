"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from bookshop import views as catalog_views
from bookshop import views, async_views
from bookshop.views import BookListView, BookDetailView, BookCreateView, BookUpdateView, BookDeleteView
from users import views as users_views
from django.conf import settings 
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from bookshop import api_views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

router = DefaultRouter()
router.register(r'categories', api_views.CategoryViewSet, basename='api_categories')
router.register(r'books', api_views.BookViewSet, basename='api_books')
router.register(r'orders', api_views.OrderViewSet, basename='api_orders')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), # 🔥 Документація тут!
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('api/', include(router.urls)),
    path('api/cart/', api_views.CartAPIView.as_view(), name='api_cart'),
]

urlpatterns += i18n_patterns(
    path('accounts/', include('allauth.urls')),
    path('catalog/', catalog_views.index, name="index"),
    path('catalog/categories/', catalog_views.category_list, name="category"),
    path('catalog/books/', BookListView.as_view(), name="book_list"),
    path('catalog/books/<int:pk>/', BookDetailView.as_view(), name="book_detail"),
    path('catalog/new/', BookCreateView.as_view(), name="book_create"),
    path('catalog/books/<int:pk>/edit/', BookUpdateView.as_view(), name='book_edit'),
    path('catalog/books/<int:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
    
    path('register/', users_views.register_view, name='register'),
    path('login/', users_views.login_view, name='login'),
    path('logout/', users_views.logout_view, name='logout'),

    path('profile/', users_views.profile_view, name='profile'),

    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:book_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:book_id>/", views.cart_remove, name="cart_remove"),
    path("cart/clear/", views.cart_clear, name="cart_clear"),
    path("order/create/", views.order_create, name="order_create"),
    path("order/success/", views.order_success, name="order_success"),
)

if settings.DEBUG:
    urlpatterns = [path("__debug__/", include("debug_toolbar.urls"))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)