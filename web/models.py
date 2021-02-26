from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import pandas as pd


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Exchange(models.Model):
    COUNTRIES = [
        (1, 'USA'),
        (2, 'CZ'),
    ]
    name = models.CharField(max_length=20)
    alternative_name = models.CharField(max_length=50, null=True)
    country = models.PositiveSmallIntegerField(choices=COUNTRIES, default=1)


class Security(TimeStampMixin):
    TYPES = [
        (1, 'Stock'),
        (2, 'ETF'),
        (3, 'Bond'),
        (4, 'Fund'),
    ]
    user = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UsersSecurities')
    ticker = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    alternative_name = models.CharField(max_length=50)
    description = models.TextField()
    data_source = models.TextField()
    status = models.BooleanField(default=True)
    ipo_date = models.DateField(null=True, blank=True)
    delisting_date = models.DateTimeField(null=True, blank=True)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE, default=1)
    security_type = models.PositiveSmallIntegerField(choices=TYPES, default=1)

    def process_import(data):
        exchanges = Exchange.objects.all()
        list_exchanges = {}
        for exchange in exchanges:
            list_exchanges[exchange.name] = exchange

        for row in data[1:].itertuples(index=False, name='Pandas'):
            existingSecurity = Security.objects.filter(ticker=row[0])
            if existingSecurity.exists():
                security = existingSecurity.first()
            else:
                security = Security()
            security.ticker = row[0]
            security.name = row[1]
            if row[2] in list_exchanges:
                security.exchange = list_exchanges[row[2]]
            else:
                newExchange = Exchange.objects.create(name=row[2])
                list_exchanges[row[2]] = newExchange
                security.exchange = list_exchanges[row[2]]

            security.security_type = 1 if row[3] == "Stock" else 2
            security.ipo_date = row[4]
            if pd.notnull(row[5]) and row[5] != "null":
                security.delisting_date = row[5]
            security.status = True if row[6] == "Active" else False
            security.save()


class UsersSecurities(TimeStampMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    security = models.ForeignKey(Security, on_delete=models.CASCADE)
    purchase_price = models.FloatField(null=False, blank=False)
    purchase_time = models.DateTimeField(null=False, blank=False)
    purchase_fee = models.FloatField(null=False, blank=False)
    amount = models.IntegerField(null=False, blank=False)
    sell_price = models.FloatField(null=True, blank=True)
    sell_time = models.DateTimeField(null=True, blank=True)
    sell_fee = models.FloatField(null=True, blank=True)
