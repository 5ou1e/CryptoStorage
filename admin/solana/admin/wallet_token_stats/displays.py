from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils.html import mark_safe
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from unfold.decorators import display

from utils.number_utils import formatted_number
from utils.time_utils import formatted_duration


class WalletTokenDisplays:
    @display(
        description=_("Токен"),
        ordering="-last_activity_timestamp",
    )
    def token_name_display(self, obj):
        last_activity_ago = (
            formatted_duration(now() - obj.last_activity_timestamp)
                if obj.last_activity_timestamp
            else None
        )
        last_activity_dt = obj.last_activity_timestamp
        default_logo_url = static("img/logo.png")
        logo_url = obj.token.logo if obj.token.logo else default_logo_url
        name_display = (
            obj.token.symbol
            if obj.token.symbol
            else (
                obj.token.name
                if obj.token.name
                else f"{obj.token.address[:5]}...{obj.token.address[-2:]}"
            )
        )
        created_on = obj.token.created_on
        created_on_logo = None
        created_on_title = ""
        if created_on and "pump.fun" in created_on:
            created_on_logo = static("icons/pumpfun_logo.svg")
            created_on_title = "pump.fun"

        copy_button = render_to_string(
            "admin/copy_button.html",
            {
                "copy_value": obj.token.address,
            },  # передаем нужные данные в контекст
        )
        show_warning = False
        warning_title = ""
        if (
            obj.total_sell_amount_token and obj.total_buy_amount_token > 0
        ):  # Убедиться, что деление возможно
            percentage_difference = (
                (obj.total_sell_amount_token - obj.total_buy_amount_token)
                / obj.total_buy_amount_token
            ) * 100
            if percentage_difference >= 1:
                show_warning = True
                warning_title += f"\nСумма продаж > суммы покупок"
        if obj.total_swaps_from_txs_with_mt_3_swappers:
            show_warning = True
            warning_title += f"\nОбнаружены свапы с >3 трейдерами в транзакции: {obj.total_swaps_from_txs_with_mt_3_swappers} шт"
        if obj.total_swaps_from_arbitrage_swap_events:
            show_warning = True
            warning_title += f"\nОбнаружены арбитраж-свапы: {obj.total_swaps_from_arbitrage_swap_events} шт"

        value = f"""
                <div class="flex gap-3">
                    <img src="{logo_url}" onerror="this.onerror=null;this.src='{default_logo_url}';" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />
                    <div class="flex-column">
                        <div class="flex gap-1 items-center font-semibold text-font-default-light dark:text-font-default-dark">
                            <span title="{obj.token.address}">{name_display}</span>
                            <span class="text-font-subtle-light dark:text-font-subtle-dark">{copy_button}</span>
                            {f'<i class="bx bx-error-alt" style="color:#f73d3d "title="{warning_title}"></i>' if show_warning else ''}
                            {f'<img title="{created_on_title}" src="{created_on_logo}" style="width: auto; height: 14px;" />' if created_on_logo else ''}
                        </div>
                        <div class="text-font-subtle-light dark:text-font-subtle-dark">
                            <span title="{last_activity_dt}">{last_activity_ago}</span>
                        </div>
                    </div>
                </div>
                """

        return mark_safe(value)

    @display(
        description=_("Покупки"),
        ordering="-total_buy_amount_usd",
    )
    def total_buy_amount_usd_display(self, obj):
        tooltip = f'<span title="{formatted_number(obj.total_buy_amount_usd, suffix=" $", decimals=10)}">{formatted_number(obj.total_buy_amount_usd, suffix=" $")}</span>'
        return mark_safe(tooltip)

    @display(
        description=_("Продажи"),
        ordering="-total_sell_amount_usd",
    )
    def total_sell_amount_usd_display(self, obj):
        tooltip = f'<span title="{formatted_number(obj.total_sell_amount_usd, suffix=" $", decimals=10)}">{formatted_number(obj.total_sell_amount_usd, suffix=" $")}</span>'
        return mark_safe(tooltip)

    @display(
        description=_("Профит"),
        ordering="-total_profit_usd",
        label={
            "good": "success",
            "ok": "default",
            "bad": "danger",
        },
    )
    def total_profit_usd_display(self, obj):
        value = obj.total_profit_usd
        tooltip = f'<span title="{formatted_number(value, suffix=" $", decimals=10)}">{formatted_number(value, suffix=" $", add_sign=True)}</span>'
        if not value:
            return None, mark_safe(tooltip)
        return "good" if value > 0 else "bad" if value < 0 else "ok", mark_safe(tooltip)

    @display(
        description=_("Профит %"),
        ordering="-total_profit_percent",
        label={
            "good": "success",
            "ok": "default",
            "bad": "danger",
        },
    )
    def total_profit_percent_display(self, obj):
        value = obj.total_profit_percent
        tooltip = f'<span title="{formatted_number((value + 100) / 100) if value else ""}x">{formatted_number(value, suffix=" %", decimals=2, add_sign=True)}</span>'
        if not value:
            return None, mark_safe(tooltip)
        return "good" if value > 0 else "bad" if value < 0 else "ok", mark_safe(tooltip)

    @display(
        description=_("Покупок"),
        ordering="-total_buys_count",
    )
    def total_buys_count_display(self, obj):
        return obj.total_buys_count or "0"

    @display(
        description=_("Продаж"),
        ordering="-total_sales_count",
    )
    def total_sales_count_display(self, obj):
        return obj.total_sales_count or "0"

    @display(
        description=_("Ласт актив."),
        ordering="-last_activity_timestamp",
    )
    def last_activity_timestamp_display(self, obj):
        value = obj.last_activity_timestamp
        if not value:
            return None
        return mark_safe(
            f'<span title="{value}">{formatted_duration(now() - value)}</span>'
        )

    @display(
        description=_("1-я пок."),
        ordering="-first_buy_timestamp",
    )
    def first_buy_timestamp_display(self, obj):
        value = obj.first_buy_timestamp
        if not value:
            return None
        return mark_safe(
            f'<span title="{value}">{formatted_duration(now() - value)}</span>'
        )

    @display(
        description=_("1-я прод."),
        ordering="-first_sell_timestamp",
    )
    def first_sell_timestamp_display(self, obj):
        value = obj.first_sell_timestamp
        if not value:
            return None
        return mark_safe(
            f'<span title="{value}">{formatted_duration(now() - value)}</span>'
        )

    @display(
        description=_("Холд"),
        ordering="-first_buy_sell_duration",
        label={
            "good": "success",
            "ok": "default",
            "warning": "warning",
            "bad": "danger",
        },
    )
    def first_buy_sell_duration_display(self, obj):
        # Форматируем строку, возвращая HTML
        value = obj.first_buy_sell_duration
        tooltip = f'<span title="Разница во времени между 1-й покупкой и 1-й продажей">{formatted_duration(value)}</span>'
        if value is None:
            return None, mark_safe(tooltip)
        return "ok" if value >= 30 else "warning" if value >= 5 else "bad", mark_safe(
            tooltip
        )

    @display(
        description=_("1 пок. цена."),
        ordering="-first_buy_price_usd",
    )
    def first_buy_price_usd_display(self, obj):
        value = formatted_number(
            obj.first_buy_price_usd, suffix=" $", decimals=10, subscript=True
        )
        tooltip = f'<span title="Стоимость токена в момент 1-ой покупки">{value or "-"}</span>'
        return mark_safe(tooltip)

    @display(
        description=_("1 прод. цена."),
        ordering="-first_sell_price_usd",
    )
    def first_sell_price_usd_display(self, obj):
        value = formatted_number(
            obj.first_sell_price_usd, suffix=" $", decimals=10, subscript=True
        )
        tooltip = f'<span title="Стоимость токена в момент 1-ой продажи">{value or "-"}</span>'

        return mark_safe(tooltip)

    @display(description="")
    def actions_display(self, obj):
        gmgn_logo = static("icons/gmgn_logo.svg")
        solscan_logo = static("icons/solscan_logo.svg")
        photon_logo = static("icons/photon_logo.svg")
        dexscreener_logo = static("icons/dexscreener_logo.svg")

        token_address = obj.token.address
        wallet_address = obj.wallet.address

        value = f"""
            <div class="flex">
                <div class="flex">
                    <div class="flex gap-2 font-semibold text-font-default-light dark:text-font-default-dark">
                        <a href="https://solscan.io/account/{wallet_address}?token_address={token_address}#defiactivities" target="_blank">
                            <img src="{solscan_logo}" style='width:auto; height:18px; min-width: 18px;'/>
                        </a>
                        <a href="https://gmgn.ai/sol/token/{token_address}?maker={wallet_address}" target="_blank">
                            <img src="{gmgn_logo}" style='width:auto; height:18px; min-width: 18px;'/>
                        </a>
                        <a href="https://photon-sol.tinyastro.io/en/lp/{token_address}" target="_blank">
                            <img src="{photon_logo}" style='width:auto; height:18px; min-width: 18px;'/>
                        </a>
                        <a href="https://dexscreener.com/solana/{token_address}?maker={wallet_address}" target="_blank">
                            <img src="{dexscreener_logo}" style='width:auto; height:18px; min-width: 18px;'/>
                        </a>
                    </div>
                </div>
            </div>
        """

        return mark_safe(value)
