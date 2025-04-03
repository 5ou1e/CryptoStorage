from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from unfold.views import UnfoldModelAdminViewMixin

from core import settings
from solana.admin.wallet_token_stats.admin import \
    WalletTokenStatisticForWalletStatsPageAdmin
from solana.models import Wallet, WalletTokenStatistic

from .services import get_wallet_statistics_data
from core.settings.config import config

class WalletStatisticView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Статистика кошелька"
    model = WalletTokenStatistic
    template_name = "admin/wallet/statistic.html"
    permission_required = ()

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_wallet_tokens_queryset(self, wallet):
        return WalletTokenStatistic.objects.filter(wallet=wallet)

    def get_wallet_data(self, user, wallet):
        return get_wallet_statistics_data(user, wallet)

    def get_context_data(self, **kwargs):
        user = self.request.user
        wallet_address = self.kwargs["wallet_address"]
        wallet = Wallet.objects.filter(address=wallet_address).first()
        if not wallet:
            raise Http404("Кошелёк не найден")

        tokens_queryset = self.get_wallet_tokens_queryset(wallet)
        wallet_data = self.get_wallet_data(user, wallet)

        try:
            cl = get_change_list(
                title="Token activities",
                request=self.request,
                queryset=tokens_queryset,
                model_admin_class=WalletTokenStatisticForWalletStatsPageAdmin,
            )
        except IncorrectLookupParameters:
            return redirect("/")

        context = super().get_context_data(**kwargs)

        context.update(
            {
                "cl": cl,
                "opts": cl.opts,
                # "actions_on_top": True,
                "wallet": wallet_data,
                "admin_base_url": config.admin.base_url,
                "backend_base_url": config.backend.base_url
            }
        )
        return context


class WalletStatisticBuyPriceGt15kView(WalletStatisticView):
    def get_wallet_tokens_queryset(self, wallet):
        return WalletTokenStatistic.objects.filter(
            wallet=wallet,
            first_buy_price_usd__gte=0.000008,
            total_buy_amount_usd__gte=100,
        )

    def get_wallet_data(self, user, wallet):
        return get_wallet_statistics_data(user, wallet, use_buy_price_gt_20k_stats=True)


def get_change_list(
    title,
    request,
    queryset,
    model_admin_class,
):
    def get_queryset(self, *args, **kwargs):
        return queryset

    model = queryset.model
    admin_site = AdminSite(name=title)
    model_admin = model_admin_class(model=model, admin_site=admin_site)
    model_admin.get_queryset = (
        get_queryset  # Переопределяем метод, чтобы получать нужный нам кверисет
    )

    cl = model_admin.get_changelist_instance(request)
    cl.formset = None
    cl.url_for_result = model_admin._url_for_result

    return cl
