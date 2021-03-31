from django.forms import ModelForm, CharField, EmailField, DateField
from django.contrib.auth.forms import UserCreationForm
from web.models import User, UsersSecurities
from django.conf import settings


class SignUpForm(UserCreationForm):
    first_name = CharField(max_length=30, required=False, help_text='Optional.')
    last_name = CharField(max_length=30, required=False, help_text='Optional.')
    email = EmailField(max_length=250, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', )


class SellForm(ModelForm):
    ticker = CharField(max_length=30, required=False, disabled=True)
    date = DateField(input_formats=[settings.DATE_INPUT_FORMAT])

    class Meta:
        model = UsersSecurities
        fields = ['ticker', 'date', 'quantity', 'price', 'fee']
