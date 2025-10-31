from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class RatingForm(forms.Form):
    rating = forms.FloatField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'step': '0.5'})
    )

class PreferenceForm(forms.Form):
    favorite_genres = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Enter genres separated by commas'})
    )
    preferred_actors = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Enter actors separated by commas'})
    )
