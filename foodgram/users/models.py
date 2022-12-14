from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLES = {
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    }
    email = models.EmailField(
        verbose_name= ('Адрес email'),
        max_length=254,
        unique=True,
        blank=False,
        error_messages={
            'unique': ('Пользователь с таким email уже существует!'),
        },
        help_text= ('Укажите email'),
    )
    username = models.CharField(
        verbose_name= ('Логин'),
        max_length=150,
        unique=True,
        error_messages={
            'unique': ('Пользователь с таким ником уже существует!'),
        },
        help_text= ('Укажите свой ник'),
    )
    first_name = models.CharField(
        verbose_name= ('Имя'),
        max_length=150,
        blank=True,
        help_text= ('Укажите своё имя'),
    )
    last_name = models.CharField(
        verbose_name= ('Фамилия'),
        max_length=150,
        blank=True,
        help_text= ('Укажите свою фамилию'),
    )
    role = models.CharField(
        verbose_name= ('статус'),
        max_length=20,
        choices=ROLES,
        default=USER,
    )
    date_joined = models.DateTimeField(
        verbose_name= ('Дата регистрации'),
        auto_now_add=True,
    )
    password = models.CharField(
        verbose_name= ('Пароль'),
        max_length=150,
        help_text= ('Введите пароль'),
    )

    class Meta:
        swappable = 'AUTH_USER_MODEL'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name()

    @property
    def is_moderator(self):
        return self.is_staff or self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.is_superuser or self.role == self.ADMIN


User = CustomUser


class Follow(models.Model):
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                name='Ограничение на единственную связь',
                fields=['user', 'following'],
            ),
            models.CheckConstraint(
                name='Ограничение на самоподписку',
                check=~models.Q(following=models.F('user')),
            ),
        ]
