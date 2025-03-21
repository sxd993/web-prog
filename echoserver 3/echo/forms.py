from django import forms
from .models import Book
from django.contrib.auth import get_user_model
from captcha.fields import CaptchaField

User = get_user_model()

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'price']

class UserProfileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False, label='Новый пароль')
    password_confirm = forms.CharField(widget=forms.PasswordInput(), required=False, label='Подтвердите новый пароль')
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        
        if password and password != password_confirm:
            self.add_error("password_confirm", "Пароли не совпадают")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    captcha = CaptchaField()