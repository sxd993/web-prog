from django.urls import path
from django.contrib.auth import views as auth_views
from .views import book_list, book_create, book_update, book_delete, register, login_view, logout_view

urlpatterns = [
    # Страница регистрации
    path('register/', register, name='register'),

    # Стандартная страница входа
    path('login/', login_view, name='login'),

    # Страница выхода
    path('logout/', logout_view, name='logout'),

    # Главная страница с книгами (доступна после логина)
    path('', book_list, name='book_list'),

    # Страница создания книги (доступна только для авторизованных)
    path('book/create/', book_create, name='book_create'),

    # Страница редактирования книги
    path('book/<int:pk>/update/', book_update, name='book_update'),

    # Страница удаления книги
    path('book/<int:pk>/delete/', book_delete, name='book_delete'),
]
