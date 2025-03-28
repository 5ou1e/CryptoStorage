from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from unfold.decorators import action

from users.models import UserWallet


def update_wallet_status(
    user, wallet, *, is_favorite=None, is_blacklisted=None, is_watch_later=None
):
    """Обновляет статус кошелька пользователя, сбрасывая другие статусы, если передан хотя бы один True."""
    user_wallet, created = UserWallet.objects.get_or_create(
        user=user, wallet_id=wallet.id
    )

    # Если какой-то статус ставится в True, сбрасываем остальные
    if is_favorite or is_blacklisted or is_watch_later:
        user_wallet.is_favorite = False
        user_wallet.is_blacklisted = False
        user_wallet.is_watch_later = False

    # Применяем переданные статусы
    if is_favorite is not None:
        user_wallet.is_favorite = is_favorite
    if is_blacklisted is not None:
        user_wallet.is_blacklisted = is_blacklisted
    if is_watch_later is not None:
        user_wallet.is_watch_later = is_watch_later

    user_wallet.save()


class WalletActions:
    @action(description="Выгрузить адреса кошельков")
    def export_wallets_to_file(self, request, queryset):
        data = "\n".join(str(obj.address) for obj in queryset)
        response = HttpResponse(data, content_type="text/plain")
        response["Content-Disposition"] = 'attachment; filename="wallets_export.txt"'
        return response

    @action(description="Добавить в блек-лист")
    def add_wallets_to_blacklist(self, request, queryset):
        for obj in queryset:
            update_wallet_status(request.user, obj, is_blacklisted=True)

    @action(description="Убрать из блек-листа")
    def remove_wallets_from_blacklist(self, request, queryset):
        for obj in queryset:
            update_wallet_status(request.user, obj, is_blacklisted=False)

    @action(description="Добавить в избранное")
    def add_wallets_to_favorites(self, request, queryset):
        for obj in queryset:
            update_wallet_status(request.user, obj, is_favorite=True)

    @action(description="Убрать из избранных")
    def remove_wallets_from_favorites(self, request, queryset):
        for obj in queryset:
            update_wallet_status(request.user, obj, is_favorite=False)

    @action(description="Добавить в 'Смотреть позже'")
    def add_wallets_to_watch_later(self, request, queryset):
        for obj in queryset:
            update_wallet_status(request.user, obj, is_watch_later=True)

    @action(description="Убрать из 'Смотреть позже'")
    def remove_wallets_from_watch_later(self, request, queryset):
        for obj in queryset:
            update_wallet_status(request.user, obj, is_watch_later=False)

    @action(
        description=_("Статистика"),
        url_path="changelist-wallet-open-stats",
        attrs={"target": "_blank"},
    )
    def open_stats(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        new_url = (
            reverse("admin:solana_wallet_changelist") + f"{obj.address}/statistics/"
        )
        return redirect(new_url)

    @action(
        description=_("Открыть на GMGN"),
        url_path="changelist-wallet-open-gmgn",
        attrs={"target": "_blank"},
    )
    def open_gmgn(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        wallet_address = obj.address
        return redirect(f"https://gmgn.ai/sol/address/{wallet_address}")

    @action(
        description=_("Открыть на Cielo"),
        url_path="changelist-wallet-open-cielo",
        attrs={"target": "_blank"},
    )
    def open_cielo(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        wallet_address = obj.address
        return redirect(f"https://app.cielo.finance/profile/{wallet_address}")

    @action(
        description=_("Открыть на Solscan"),
        url_path="changelist-wallet-open-solscan",
        attrs={"target": "_blank"},
    )
    def open_solscan(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        wallet_address = obj.address
        return redirect(f"https://solscan.io/account/{wallet_address}")
