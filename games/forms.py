from django import forms
from django.contrib.auth.models import User
from .models import Game


# =========================
# GAME FORM
# =========================

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = [
            'title',
            'description',
            'original_price',
            'discount_percent',
            'image',
        ]
# =========================
# REGISTER FORM
# =========================

class RegisterForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput()
    )

    class Meta:

        model = User

        fields = [
            'username',
            'email',
            'password'
        ]