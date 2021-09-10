import uuid
from datetime import date

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def validate_year(value):
    """
    Checking the title's year is in the valid range
    """
    if value > date.today().year + 10 or value < -40000:
        raise ValidationError(
            'the year %(value)s is outside the valid date range',
            params={'value': value},)


class User(AbstractUser):
    """
    New class CustomUser which is based on AbstractUser.
    Making the email field required and unique.
    """
    class UserRoles(models.TextChoices):
        """
        An iterator that will be used as value variants for the role field.
        """
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    confirmation_code = models.CharField(max_length=75, blank=True)
    email = models.EmailField(unique=True,
                              verbose_name='Адрес электронной почты')
    bio = models.TextField(max_length=750,
                           blank=True,
                           verbose_name='О себе')
    role = models.CharField(max_length=10,
                            choices=UserRoles.choices,
                            default=UserRoles.USER,
                            verbose_name=('Администратор, модератор'
                                          ' или пользователь.'))
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', )

    @property
    def moderator(self):
        return self.role == self.UserRoles.MODERATOR

    @property
    def admin(self):
        return self.role == self.UserRoles.ADMIN

    class Meta:
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name='Название категории')
    slug = models.SlugField(unique=True,
                            default=uuid.uuid1,
                            verbose_name='Ссылка на категорию')

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name='Название жанра')
    slug = models.SlugField(unique=True,
                            default=uuid.uuid1,
                            verbose_name='Ссылка на жанр')

    class Meta:
        ordering = ['name']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self) -> str:
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name='Название произведения')
    year = models.IntegerField(validators=[validate_year],
                               verbose_name='Год публикации')
    description = models.TextField(verbose_name='Описание')
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self) -> str:
        return self.name


class Review(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField(verbose_name='Текст отзыва',
                            max_length=300)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='reviews')
    score = models.IntegerField(
        verbose_name='Оценка',
        blank=True,
        validators=[MinValueValidator(1, 'Не меньше 1'),
                    MaxValueValidator(10, 'Не больше 10')]
    )
    pub_date = models.DateTimeField(verbose_name='Дата создания',
                                    auto_now_add=True,
                                    db_index=True)

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,)
    text = models.TextField(verbose_name='Текст комментария',
                            max_length=300)
    pub_date = models.DateTimeField(verbose_name='Дата создания',
                                    auto_now_add=True,
                                    db_index=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.review_id
