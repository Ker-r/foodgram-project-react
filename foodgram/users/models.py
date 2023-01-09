from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField('email', null=False, unique=True)
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLES = {
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    }
    role = models.CharField(
        verbose_name='статус',
        max_length=20,
        choices=ROLES,
        default=USER,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        ordering = ['id']

    def __str__(self):
        return f'Пользователь {self.email}'

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
