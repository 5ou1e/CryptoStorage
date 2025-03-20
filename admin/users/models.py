from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid6 import uuid7


class User(AbstractUser):  # Название модели "User"
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    hashed_password = models.CharField(max_length=128, verbose_name="password")
    password = models.CharField(max_length=128, verbose_name="password")  # Оставляем поле
    wallets = models.ManyToManyField('solana.Wallet', through='UserWallet')

    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.hashed_password = make_password(raw_password)

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.hashed_password)

    class Meta:
        db_table = "auth_user"  # Задаем имя таблицы как у стандартной модели Django
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'


class UserWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user_wallet', verbose_name="Пользователь")
    wallet = models.ForeignKey('solana.Wallet', on_delete=models.CASCADE, related_name='user_wallet', verbose_name="Кошелек")
    is_favorite = models.BooleanField(default=False, verbose_name="Кошелек в избранном")
    is_blacklisted = models.BooleanField(default=False, verbose_name="Кошелек в блек-листе")
    is_watch_later = models.BooleanField(default=False, verbose_name="Кошелек в 'посмотреть позже'")
    remark = models.TextField(null=True, blank=True, verbose_name='Заметка')
    # дополнительные поля, если нужно, например:
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_wallet'
        verbose_name = 'пользователь-кошелек'
        verbose_name_plural = 'пользователь-кошелек'
        unique_together = ("user", "wallet")
#
# class UserTokenInsiderAlert(models.Model):
#     user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user_token_insider_alerts")  # Ссылка на пользователя
#     token = models.ForeignKey("solana.Token", on_delete=models.CASCADE, related_name="user_token_insider_alerts")
#     send_alerts = models.BooleanField(default=True)  # Статус отправки оповещений
#     last_tg_msg_id = models.BigIntegerField(null=True, blank=True)  # ID последнего сообщения в Telegram
#     last_tg_msg_timestamp = models.DateTimeField(null=True, blank=True)  # Время отправки последнего сообщения в Telegram
#     last_sent_time = models.DateTimeField(null=True, blank=True)  # Время последней отправки оповещения
#
#     class Meta:
#         db_table = "user_insider_token_alert"
#
#     def __str__(self):
#         return f"User: {self.user.username}, Token: {self.token.address}, Alerts Enabled: {self.send_alerts}"