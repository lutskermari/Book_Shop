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
from django.urls import path
from bookshop import views as catalog_views
from bookshop.views import BookListView, BookDetailView, BookCreateView, BookUpdateView, BookDeleteView
from users import views as users_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('catalog/', catalog_views.index, name="index"),
    path('catalog/categories/', catalog_views.category_list, name="category"),
    path('catalog/books/', BookListView.as_view(), name="book_list"),
    path('catalog/books/<int:pk>/', BookDetailView.as_view(), name="book_detail"),
    path('catalog/new/', BookCreateView.as_view(), name="book_create"),
    path('catalog/books/<int:pk>/edit/', BookUpdateView.as_view(), name='book_edit'),
    path('catalog/books/<int:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
    
    path('register/', users_views.register_view, name='register'),
    path('login/', users_views.login_view, name='login'),
    path('logout/', users_views.logout_view, name='logout')
]
