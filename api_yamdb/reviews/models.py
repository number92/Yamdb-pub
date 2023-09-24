from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_username, validate_year

DEFAULT_USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'


class User(AbstractUser):
    """Класс пользователей."""

    ROLE = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (DEFAULT_USER, 'Пользователь')
    )

    username = models.CharField(
        max_length=settings.USERNAME_LENGTH,
        verbose_name='Имя пользователя',
        unique=True,
        blank=False,
        validators=[validate_username],
    )
    email = models.EmailField(
        max_length=settings.EMAIL_LENGTH,
        verbose_name='Email',
        unique=True,
        blank=False
    )
    first_name = models.CharField(
        max_length=settings.FIRST_NAME_LENGTH,
        verbose_name='Имя',
        blank=True
    )
    last_name = models.CharField(
        max_length=settings.LAST_NAME_LENGTH,
        verbose_name='Фамилия',
        blank=True
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True
    )
    role = models.CharField(
        max_length=max(len(role) for role, _ in ROLE),
        verbose_name='Роль',
        choices=ROLE,
        default=DEFAULT_USER
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return (
            self.role == ADMIN or self.is_staff
        )

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_user(self):
        return self.role == DEFAULT_USER


class CategoryGenreBase(models.Model):
    """Основной класс для Category и Genre"""
    name = models.CharField('Имя', max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ('name',)
        abstract = True

    def __str__(self):
        return self.name


class Genre(CategoryGenreBase):
    """Категории жанров"""

    class Meta(CategoryGenreBase.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(CategoryGenreBase):
    """Категории (типы) произведений"""

    class Meta(CategoryGenreBase.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    """Произведения, к которым пишут отзывы."""
    name = models.CharField('Название произведения', max_length=256)
    year = models.IntegerField(
        'Год выпуска',
        null=True,
        validators=[validate_year],
        blank=True
    )
    description = models.TextField('Описание', blank=True)
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категории'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class DiscussionBase(models.Model):
    """Основной класс для Reviews и Comments"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)s"
    )
    text = models.TextField('Текст комментария')
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Review(DiscussionBase):
    """Отзывы на произведения"""
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        'Оценка',
        validators=[MinValueValidator(settings.MIN_SCORE),
                    MaxValueValidator(settings.MAX_SCORE)]
    )

    class Meta(DiscussionBase.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]


class Comment(DiscussionBase):
    """Комментарии к отзывам"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta(DiscussionBase.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
