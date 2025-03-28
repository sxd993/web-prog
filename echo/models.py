from django.db import models
from django.contrib.auth.models import User

# Модель книг в БД
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default='')

    def __str__(self):
        return self.title

# Модель корзины в БД
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"

# Модель оформления заказа в БД
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Новый') 
    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"

# Модель объектов заказа в БД
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"