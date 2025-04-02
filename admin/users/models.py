from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid6 import uuid7


class User(AbstractUser):  # Название модели "User"
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    password = models.CharField(max_length=128, db_column="hashed_password")
    wallets = models.ManyToManyField("solana.WalletBase", through="UserWallet")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user"  # Задаем имя таблицы как у стандартной модели Django
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"


class UserWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="user_wallet",
        verbose_name="пользователь",
    )
    wallet = models.ForeignKey(
        "solana.WalletBase",
        on_delete=models.CASCADE,
        related_name="user_wallet",
        verbose_name="кошелек",
    )
    is_favorite = models.BooleanField(
        default=False, verbose_name="Кошелек в «Избранное»"
    )
    is_blacklisted = models.BooleanField(
        default=False, verbose_name="Кошелек добавлен в «Блек-лист»"
    )
    is_watch_later = models.BooleanField(
        default=False, verbose_name="Кошелек добавлен в «Посмотреть позже»"
    )
    remark = models.TextField(
        null=True, blank=True, verbose_name="Пользовательская заметка"
    )
    # дополнительные поля, если нужно, например:
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_wallet"
        verbose_name = "пользователь-кошелек"
        verbose_name_plural = "пользователь-кошелек"
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
