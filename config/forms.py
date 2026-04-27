from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm as BasePasswordResetForm


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre email'}))
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre mot de passe'}))

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError("Email ou mot de passe incorrect.")

            self.user = authenticate(self.request, username=user.username, password=password)
            if self.user is None:
                raise forms.ValidationError("Email ou mot de passe incorrect.")

        return self.cleaned_data

    def get_user(self):
        return self.user


class PasswordResetForm(BasePasswordResetForm):
    """Formulaire de réinitialisation de mot de passe utilisant l'email"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser le champ email
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Entrez votre adresse email'
        })