from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    USA = 1
    CZ = 2
    COUNTRIES = [
        (1, 'USA'),
        (2, 'CZ'),
    ]
    name = models.CharField(max_length=20)
    alternative_name = models.CharField(max_length=50, null=True)
    country = models.PositiveSmallIntegerField(choices=COUNTRIES, default=USA)


class Security(TimeStampMixin):
    STOCK = 1
    ETF = 2
    BOND = 3
    FUND = 4
    TYPES = [
        (STOCK, 'Stock'),
        (ETF, 'ETF'),
        (BOND, 'Bond'),
        (FUND, 'Fund'),
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
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE, default=Exchange.USA)
    security_type = models.PositiveSmallIntegerField(choices=TYPES, default=STOCK, null=False, blank=False)

    def __str__(self):
        return self.ticker + '.' + self.exchange.name


class UsersSecurities(TimeStampMixin):
    BUY = 1
    SELL = 2
    DIRECTIONS = [
        (BUY, 'BUY'),
        (SELL, 'SELL'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    security = models.ForeignKey(Security, on_delete=models.CASCADE)
    price = models.FloatField(null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    fee = models.FloatField(null=False, blank=False)
    quantity = models.IntegerField(null=False, blank=False)
    direction = models.PositiveSmallIntegerField(choices=DIRECTIONS, null=False, blank=False)


class UsersMoneyTransaction(TimeStampMixin):
    DIRECTION_INCOME = 1
    DIRECTION_OUTGOINGS = 2

    DIRECTIONS = [
        (DIRECTION_INCOME, 'INCOME'),
        (DIRECTION_OUTGOINGS, 'OUTGOINGS'),
    ]

    FEE = 1
    SELL = 2
    WITHDRAWAL = 3
    DIVIDEND = 4
    INCOME = 5

    TRANSACTION_TYPES = [
        (FEE, 'FEE'),
        (SELL, 'SELL'),
        (WITHDRAWAL, 'WITHDRAWAL'),
        (DIVIDEND, 'DIVIDEND'),
        (INCOME, 'INCOME'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.FloatField(null=False, blank=False)
    direction = models.PositiveSmallIntegerField(choices=DIRECTIONS, default=DIRECTION_INCOME)
    transacted_at = models.DateField(null=False, blank=False)
    transaction_type = models.PositiveSmallIntegerField(choices=TRANSACTION_TYPES, default=FEE)
    security = models.ForeignKey(Security, on_delete=models.SET_NULL, null=True)
