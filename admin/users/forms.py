# users/forms.py
from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group

from .models import User


class CustomUserCreationForm(UserCreationForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),  # Все доступные группы
        required=False,  # Необязательное поле
        widget=forms.CheckboxSelectMultiple  # Отображение как чекбоксы
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'is_staff', 'groups')  # Добавьте нужные вам поля


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'is_staff', 'groups')  # Добавьте нужные вам поля