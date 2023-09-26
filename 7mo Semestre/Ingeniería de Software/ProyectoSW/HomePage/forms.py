from django import forms
from .models import Transaction

class RegisterForm(forms.Form):
    user = forms.CharField(label="Usuario", required = True)
    email = forms.EmailField(label="Correo electrónico", required = True)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput,required = True)
    repeatPassword  = forms.CharField(label="Repetir contraseña", widget=forms.PasswordInput,required = True)

class LoginForm(forms.Form):
    user = forms.CharField(label="Usuario", required = True)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput,required = True)

class NewTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('transaction_type', 'amount', 'date', 'comment')
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control'}),
            'comment': forms.TextInput(attrs={'class': 'form-control'})
        }    