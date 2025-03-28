from typing import Any

from django.http import HttpRequest
from django.urls import reverse_lazy

from .token import TokenAdmin, TokenPriceAdmin
from .wallet import WalletAdmin, WalletProxyAdmin
from .wallet_activity import WalletActivityAdmin
from .wallet_stats import (WalletStatistic7dAdmin, WalletStatistic30dAdmin,
                           WalletStatisticAllAdmin)
from .wallet_token_stats import WalletTokenStatisticAdmin

__all__ = [
    "WalletAdmin",
    "WalletProxyAdmin",
    "TokenAdmin",
    "TokenPriceAdmin",
    "WalletStatistic7dAdmin",
    "WalletStatistic30dAdmin",
    "WalletStatisticAllAdmin",
    "WalletActivityAdmin",
    "WalletTokenStatisticAdmin",
]

from urllib.parse import parse_qs, urlparse

from django.http import HttpRequest
from django.urls import reverse_lazy


def tabs_callback(request: HttpRequest) -> list[dict[str, Any]]:
    default_period = "30d"
    base_url = str(reverse_lazy("admin:solana_wallet_changelist"))  # Главная
    base_url = f"{base_url}?period={default_period}"
    main_url = f"{base_url}&is_scammer=0&is_bot=0&is_blacklisted=0"
    favorite_url = f"{base_url}&is_my_favorite=1"  # Избранные
    watch_later_url = f"{base_url}&is_watch_later=1"  # Смотреть позже
    blacklist_url = f"{base_url}&is_blacklisted=1"  # Блеклист

    # Разбираем параметры запроса
    query_params = parse_qs(urlparse(request.get_full_path()).query)

    # Определяем количество активных фильтров
    active_filters = [
        key
        for key in ["is_my_favorite", "is_watch_later", "is_blacklisted"]
        if query_params.get(key) == ["1"]
    ]

    # Если ровно один фильтр → он становится активной вкладкой, иначе активна "Главная"
    active_tab = active_filters[0] if len(active_filters) == 1 else "main"

    base = [
        {
            "page": "custom_page",
            "models": ["solana.wallet"],
            "items": [
                {
                    "title": "Главная",
                    "link": main_url,
                    "active": active_tab == "main",
                },
                {
                    "title": "Избранные",
                    "link": favorite_url,
                    "active": active_tab == "is_my_favorite",
                },
                {
                    "title": "Смотреть позже",
                    "link": watch_later_url,
                    "active": active_tab == "is_watch_later",
                },
                {
                    "title": "Блеклист",
                    "link": blacklist_url,
                    "active": active_tab == "is_blacklisted",
                },
            ],
        },
    ]
    return base


# from urllib.parse import urlparse, parse_qs
# from django.urls import reverse
# from django.http import HttpRequest
#
# def is_active_tab(request: HttpRequest, expected_url: str) -> bool:
#     """Точная проверка соответствия URL"""
#     parsed_request = urlparse(request.get_full_path())
#     parsed_expected = urlparse(expected_url)
#
#     return parsed_request.path == parsed_expected.path and parse_qs(parsed_request.query) == parse_qs(parsed_expected.query)
#
# def tabs_callback(request: HttpRequest) -> list[dict[str, Any]]:
#     base_url = str(reverse("admin:solana_wallet_changelist"))  # Без reverse_lazy, берем строку сразу
#     favorite_url = f"{base_url}?is_my_favorite=1"
#
#     print(is_active_tab(request, base_url))
#     print(is_active_tab(request, favorite_url))
#     base = [
#         {
#             "page": "custom_page",
#             "models": ["solana.wallet"],
#             "items": [
#                 {
#                     "title": "Главная",
#                     "link": base_url,
#                     "active": is_active_tab(request, base_url),  # Принудительное указание `active`
#                 },
#                 {
#                     "title": "Избранные",
#                     "link": favorite_url,
#                     "active": is_active_tab(request, favorite_url),  # Принудительное указание `active`
#                 },
#             ],
#         },
#     ]
#     return base
