from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Book, Cart, Order, OrderItem
from .forms import BookForm, UserProfileForm
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
import random
from django.http import HttpResponse
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.utils.timezone import localtime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.conf import settings


def is_admin(user):
    print(f"User: {user}, is_staff: {user.is_staff}")
    return user.is_staff


# Неавторизованный пользователь может просматривать список книг
def book_list(request):
    books = Book.objects.all()

    # Фильтрация по автору и диапазону цен
    author = request.GET.get('author', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    if author:
        books = books.filter(author__icontains=author)
    if min_price:
        books = books.filter(price__gte=min_price)
    if max_price:
        books = books.filter(price__lte=max_price)

    # Пагинация
    paginator = Paginator(books, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "books/book_list.html", {
        "page_obj": page_obj,
        "author": author,
        "min_price": min_price,
        "max_price": max_price
    })


# Авторизованный пользователь может добавлять книги
@login_required
def book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("book_list")
    else:
        form = BookForm()
    return render(request, "books/book_create.html", {"form": form})


# Администратор может редактировать книги
@login_required
@user_passes_test(is_admin)
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect("book_list")
    else:
        form = BookForm(instance=book)

    return render(request, "books/book_update.html", {"form": form})


# Администратор может удалять книги
@login_required
@user_passes_test(is_admin)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        book.delete()
        return redirect("book_list")
    return render(request, "books/book_delete.html", {"book": book})


# Представление для регистрации
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("book_list")
    else:
        form = UserCreationForm()

    return render(request, "books/register.html", {"form": form})

# Представление для списка заказов
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('orderitem_set__book')
    
    order_data = []
    for order in orders:
        items = order.orderitem_set.all()
        total_cost = sum(item.book.price * item.quantity for item in items)
        order_data.append({
            'order': order.id,
            'order_date': order.created_at,
            'order_items': items,
            'total_cost': total_cost,
        })
    
    return render(request, 'books/order_list.html', {'orders': order_data})

# Представление для авторизации
def login_view(request):
    captcha_error = None

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        captcha_key = request.POST.get("captcha_0", "")
        captcha_value = request.POST.get("captcha_1", "")

        if settings.TESTING or CaptchaStore.objects.filter(
            hashkey=captcha_key, response=captcha_value
        ).exists():
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                next_url = request.GET.get("next", "book_list")
                return redirect(next_url)
        else:
            captcha_error = "Неверный код CAPTCHA"

    else:
        form = AuthenticationForm()

    # Генерация CAPTCHA
    captcha_key = CaptchaStore.generate_key()
    captcha_url = captcha_image_url(captcha_key)

    return render(
        request,
        "books/login.html",
        {
            "form": form,
            "captcha_key": captcha_key,
            "captcha_url": captcha_url,
            "captcha_error": captcha_error,
            "TESTING": settings.TESTING,  # передаём в шаблон, если нужно
        },
    )

def logout_view(request):
    logout(request)
    return redirect("book_list")


# Личный кабинет
@login_required
def user_profile(request):
    user = request.user
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = UserProfileForm(instance=user)
    return render(request, "books/profile.html", {"form": form})


@login_required
def add_to_cart(request, book_id):
    book = Book.objects.get(id=book_id)
    user = request.user  # получаем текущего пользователя
    cart_item, created = Cart.objects.get_or_create(user=user, book=book)

    if not created:
        # если товар уже есть в корзине, увеличиваем количество
        cart_item.quantity += 1
        cart_item.save()

    return redirect("view_cart")  # перенаправляем на страницу корзины


# Обновление корзины
@login_required
def update_cart(request):
    if request.method == "POST":
        user = request.user

        # Обновление одного товара
        if "update_item" in request.POST:
            item_id = request.POST["update_item"]
            quantity = int(request.POST.get(f"quantity_{item_id}", 1))

            if quantity > 0:
                cart_item = Cart.objects.get(id=item_id, user=user)
                cart_item.quantity = quantity
                cart_item.save()
            else:
                Cart.objects.filter(id=item_id, user=user).delete()

        # Обновление всей корзины
        elif "update_all" in request.POST:
            for item in Cart.objects.filter(user=user):
                quantity = int(request.POST.get(f"quantity_{item.id}", 1))

                if quantity > 0:
                    item.quantity = quantity
                    item.save()
                else:
                    item.delete()

        return redirect("view_cart")

    return redirect("view_cart")


# Просмотр корзины
@login_required
def view_cart(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_cost = sum(item.book.price * item.quantity for item in cart_items)
    return render(
        request, "books/cart.html", {"cart_items": cart_items, "total_cost": total_cost}
    )


# Удалить товар из корзины
@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect("view_cart")  # Перенаправление на страницу корзины


# Оформить заказ
@login_required
def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items:
        return HttpResponse("Ваша корзина пуста!", status=400)

    # Создание заказа
    order = Order(user=user)
    order.save()

    # Добавление товаров из корзины в заказ
    total_cost = 0
    for item in cart_items:
        order_item = OrderItem(order=order, book=item.book, quantity=item.quantity)
        order_item.save()
        total_cost += item.book.price * item.quantity

    # Обновляем случайный номер заказа (например, через random)
    order_number = random.randint(1000, 9999)
    order.number = order_number
    order.total_cost = total_cost
    order.save()

    # Очистка корзины после оформления заказа
    cart_items.delete()

    # Перенаправление на страницу деталей заказа
    return redirect("order_detail", order_id=order.id)


# Детали заказа
@login_required
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    total_cost = sum(item.book.price * item.quantity for item in order_items)
    order_date = localtime(order.created_at).strftime("%d-%m-%Y %H:%M:%S")

    # Отображаем информацию о заказе
    return render(
        request,
        "books/order_detail.html",
        {
            "order": order,
            "order_items": order_items,
            "total_cost": total_cost,
            "order_date": order_date,
        },
    )


@csrf_exempt
@require_POST
def check_email(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()

        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        if '@' not in email or '.' not in email.split('@')[1]:
            return JsonResponse({'error': 'Invalid email format'}, status=400)

        exists = get_user_model().objects.filter(email__iexact=email).exists()
        return JsonResponse({'is_unique': not exists})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
