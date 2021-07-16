from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Currency(TimeStampMixin):
    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=5, null=True, blank=True)
    alternative_name = models.CharField(max_length=50)
    description = models.TextField()
    ordering = models.PositiveSmallIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_currency_name')
        ]


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)


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


class Country(TimeStampMixin):
    name = models.CharField(max_length=20)
    active = models.BooleanField(default=True)
    shortcut = models.CharField(max_length=3, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_country_name')
        ]


class Exchange(TimeStampMixin):
    name = models.CharField(max_length=20)
    alternative_name = models.CharField(max_length=50, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    time_zone = models.CharField(max_length=40, null=True)
    sync_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_exchange_name')
        ]


class SecurityType(TimeStampMixin):
    name = models.CharField(max_length=40)
    show = models.BooleanField(null=True, blank=True)
    show_as = models.ForeignKey('self', null=True, on_delete=models.CASCADE)


class Security(TimeStampMixin):
    user = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UsersSecurities')
    ticker = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    alternative_name = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    data_source = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)
    ipo_date = models.DateField(null=True, blank=True)
    delisting_date = models.DateTimeField(null=True, blank=True)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    security_type = models.ForeignKey(SecurityType, on_delete=models.CASCADE)
    sync_at = models.DateTimeField(null=True, blank=True)

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
    DEPOSIT = 5
    OTHER = 5

    TRANSACTION_TYPES = [
        (FEE, 'fee'),
        (SELL, 'sell'),
        (WITHDRAWAL, 'withdrawal'),
        (DIVIDEND, 'dividend'),
        (DEPOSIT, 'deposit'),
        (OTHER, 'other'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.FloatField(null=False, blank=False)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    direction = models.PositiveSmallIntegerField(choices=DIRECTIONS, default=DIRECTION_INCOME)
    transacted_at = models.DateField(null=False, blank=False)
    transaction_type = models.PositiveSmallIntegerField(choices=TRANSACTION_TYPES, default=FEE)
    security = models.ForeignKey(Security, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
