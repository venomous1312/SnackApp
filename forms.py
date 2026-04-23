from django import forms
from django.contrib.auth.models import User
from .models import Business
from django.utils.text import slugify

# --- CUSTOMER SIGN UP ---
class CustomerSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

# --- BUSINESS OWNER SIGN UP ---
class BusinessSignUpForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    business_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )
        Business.objects.create(
            name=self.cleaned_data['business_name'],
            owner=user,
            slug=slugify(self.cleaned_data['business_name'])
        )
        return user