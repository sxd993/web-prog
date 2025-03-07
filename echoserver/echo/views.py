from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Book
from .forms import BookForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test

# Функция для проверки, является ли пользователь администратором


def is_admin(user):
    return user.is_staff

# Неавторизованный пользователь может просматривать список книг


def book_list(request):
    books = Book.objects.all()
    paginator = Paginator(books, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'books/book_list.html', {'page_obj': page_obj})

# Авторизованный пользователь может добавлять книги


@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/book_create.html', {'form': form})

# Администратор может редактировать книги


@login_required
@user_passes_test(is_admin)
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)

    return render(request, 'books/book_update.html', {'form': form})

# Администратор может удалять книги


@login_required
@user_passes_test(is_admin)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'books/book_delete.html', {'book': book})

# Представление для регистрации


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('book_list')
    else:
        form = UserCreationForm()

    return render(request, 'books/register.html', {'form': form})

# Представление для авторизации


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'book_list')
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, 'books/login.html', {'form': form})

# Представление для выхода


def logout_view(request):
    logout(request)
    return redirect('book_list')
