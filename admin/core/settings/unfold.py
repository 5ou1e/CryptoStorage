from django.templatetags.static import static
from django.urls import reverse, reverse_lazy
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

from .config import config


def get_wallets_favorite_tab_url():
    base_url = reverse_lazy("admin:solana_wallet_changelist")
    query_params = "is_my_favorite=1"
    return f"{base_url}?{query_params}"


def get_wallets_all_tab_url():
    base_url = reverse_lazy("admin:solana_wallet_changelist")
    query_params = "period=30d&is_scammer=0&is_bot=0&is_blacklisted=0"
    return f"{base_url}?{query_params}"


UNFOLD = {
    "SHOW_LANGUAGES": True,
    "SITE_TITLE": config.django_unfold.site_title,
    "SITE_HEADER": config.django_unfold.site_header,
    "SITE_URL": "/",
    # "SITE_ICON": lambda request: static("icon.svg"),  # both modes, optimise for 32px height
    "SITE_ICON": {
        "light": lambda request: static("img/logo.png"),  # light mode
        "dark": lambda request: static("img/logo.png"),  # dark mode
    },
    # "SITE_LOGO": lambda request: static("img/logo.png"),  # both modes, optimise for 32px height
    # "SITE_LOGO": {
    #     "light": lambda request: static("img/logo.png"),  # light mode
    #     "dark": lambda request: static("img/logo.png"),  # dark mode
    # },
    "SITE_SYMBOL": "speed",  # symbol from icon set
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/svg+xml",
            "href": lambda request: static("img/logo.png"),
        },
    ],
    "SHOW_HISTORY": True,  # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": True,  # show/hide "View on site" button, default: True
    # "ENVIRONMENT": "sample_app.environment_callback",
    # "DASHBOARD_CALLBACK": "sample_app.dashboard_callback",
    # "THEME": "dark", # Force theme: "dark" or "light". Will disable theme switcher
    "LOGIN": {
        "image": lambda request: static("sample/login-bg.jpg"),
        # "redirect_after": lambda request: reverse_lazy("admin:APP_MODEL_changelist"),
    },
    "STYLES": [
        lambda request: static("css/style.css"),
    ],
    "SCRIPTS": [
        lambda request: static("js/script.js"),
    ],
    "COLORS": {
        "base": {
            "50": "#fafafa",
            "100": "#f4f4f5",
            "200": "#e4e4e7",
            "300": "#d4d4d8",
            "400": "#a1a1aa",
            "500": "#71717a",
            "600": "#52525b",
            "700": "#3f3f46",
            "800": "#27272a",
            "900": "#18181b",
            "950": "#09090b",
        },
        "primary": {
            "50": "#f5f3ff",
            "100": "#ede9fe",
            "200": "#ddd6fe",
            "300": "#c4b5fd",
            "400": "#a78bfa",
            "500": "#8b5cf6",
            "600": "#7c3aed",
            "700": "#6d28d9",
            "800": "#5b21b6",
            "900": "#4c1d95",
            "950": "#2e1065",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",  # text-base-500
            "subtle-dark": "var(--color-base-400)",  # text-base-400
            "default-light": "var(--color-base-600)",  # text-base-600
            "default-dark": "var(--color-base-300)",  # text-base-300
            "important-light": "var(--color-base-900)",  # text-base-900
            "important-dark": "var(--color-base-100)",  # text-base-100
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇧🇪",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,  # Search in applications and models names
        "show_all_applications": True,  # Dropdown with all applications and models
        "navigation": [
            # {
            #     "title": _("Учетные записи"),
            #     "separator": True,  # Top border
            #     "collapsible": False,  # Collapsible group of links
            #     "items": [
            #         {
            #             "title": _("Пользователи"),
            #             "icon": "people",
            #             "link": reverse_lazy("admin:users_user_changelist"),
            #         },
            #         {
            #             "title": _("Группы пользователей"),
            #             "icon": "groups",
            #             "link": reverse_lazy("admin:auth_group_changelist"),
            #         },
            #     ],
            #
            # },
            {
                "title": _("Solana"),
                "separator": True,  # Top border
                "collapsible": False,  # Collapsible group of links
                "items": [
                    # {
                    #     "title": _("Кошельки"),
                    #     "icon": "account_balance_wallet",
                    #     "link": reverse_lazy("admin:solana_walletproxy_changelist"),
                    #     "permission": lambda request: request.user.has_perm("solana.view_walletproxy"),
                    # },
                    {
                        "title": _("Токены"),
                        "icon": "token",
                        "link": reverse_lazy("admin:solana_token_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "solana.view_token"
                        ),
                    },
                    {
                        "title": _("Цены токенов"),
                        "icon": "attach_money",
                        "link": reverse_lazy("admin:solana_tokenprice_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "solana.view_token"
                        ),
                    },
                    {
                        "title": _("Свапы"),
                        "icon": "send_money",
                        "link": reverse_lazy("admin:solana_walletactivity_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "solana.view_walletactivity"
                        ),
                    },
                ],
            },
            {
                "title": _("Статистики"),
                "separator": True,  # Top border
                "collapsible": False,  # Collapsible group of links
                "items": [
                    {
                        "title": _("Кошельки"),
                        "icon": "account_balance_wallet",
                        "link": lazy(get_wallets_all_tab_url, str)(),
                        "permission": lambda request: request.user.has_perm(
                            "solana.view_wallet"
                        ),
                    },
                    {
                        "title": _("Кошельки (Buy Price Gt 15k)"),
                        "icon": "account_balance_wallet",
                        "link": reverse_lazy(
                            "admin:solana_walletbuypricegt15k_changelist"
                        ),
                        "permission": lambda request: request.user.has_perm(
                            "solana.view_walletbuypricegt15k"
                        ),
                    },
                ],
            },
            {
                "title": _("Внешние сервисы"),
                "separator": True,  # Top border
                "collapsible": False,  # Collapsible group of links
                "items": [
                    {
                        "title": _("FlipsideCrypto конфиг"),
                        "icon": "settings",
                        "link": reverse_lazy(
                            "admin:external_services_flipsideconfig_changelist"
                        ),
                        "permission": lambda request: request.user.has_perm(
                            "external_services.view_flipsideconfig"
                        ),
                    },
                    {
                        "title": _("FlipsideCrypto Аккаунты"),
                        "icon": "settings",
                        "link": reverse_lazy(
                            "admin:external_services_flipsideaccount_changelist"
                        ),
                        "permission": lambda request: request.user.has_perm(
                            "external_services.view_flipsideaccount"
                        ),
                    },
                ],
            },
            # {
            #     "title": _("Периодические задачи"),
            #     "separator": True,  # Top border
            #     "collapsible": False,  # Collapsible group of links
            #     "items": [
            #         {
            #             "title": _("Periodic tasks"),
            #             "icon": "task",
            #             "link": reverse_lazy("admin:django_celery_beat_periodictask_changelist"),
            #             "permission": lambda request: request.user.has_perm("django_celery_beat.view_periodictask"),
            #         },
            #         {
            #             "title": _("Task results"),
            #             "icon": "summarize",
            #             "link": reverse_lazy("admin:django_celery_results_taskresult_changelist"),
            #             "permission": lambda request: request.user.has_perm("django_celery_results.view_taskresult"),
            #         },
            #         # {
            #         #     "title": _("Group results"),
            #         #     "icon": "bar_chart",
            #         #     "link": reverse_lazy("admin:django_celery_results_groupresult_changelist"),
            #         #     "permission": lambda request: request.user.has_perm("django_celery_results.view_groupresult"),
            #         # },
            #         # {
            #         #     "title": _("Crontabs"),
            #         #     "icon": "update",
            #         #     "link": reverse_lazy("admin:django_celery_beat_crontabschedule_changelist"),
            #         #     "permission": lambda request: request.user.has_perm("django_celery_beat.view_crontabschedule"),
            #         # },
            #         # {
            #         #     "title": _("Clocked"),
            #         #     "icon": "hourglass_bottom",
            #         #     "link": reverse_lazy("admin:django_celery_beat_clockedschedule_changelist"),
            #         #     "permission": lambda request: request.user.has_perm("django_celery_beat.view_clockedschedule"),
            #         # },
            #         # {
            #         #     "title": _("Intervals"),
            #         #     "icon": "arrow_range",
            #         #     "link": reverse_lazy("admin:django_celery_beat_intervalschedule_changelist"),
            #         #     "permission": lambda request: request.user.has_perm("django_celery_beat.view_intervalschedule"),
            #         # },
            #         # {
            #         #     "title": _("Solar"),
            #         #     "icon": "event",
            #         #     "link": reverse_lazy("admin:django_celery_beat_solarschedule_changelist"),
            #         #     "permission": lambda request: request.user.has_perm("django_celery_beat.view_solarschedule"),
            #         # },
            #     ],
            #
            # },
        ],
    },
    "TABS": "solana.admin.tabs_callback",
    # "TABS": [
    #     {
    #         "models": [
    #             "solana.wallet",
    #         ],
    #         "items": [
    #             {
    #                 "title": _("Главная"),
    #                 "link": lazy(get_wallets_all_tab_url, str)(),
    #                 # "permission": "users.permission_callback",
    #             },
    #             {
    #                 "title": _("Избранные"),
    #                 "link": lazy(get_wallets_favorite_tab_url, str)(),
    #                 # "permission": "users.permission_callback",
    #             }
    #         ],
    #     }
    # ],
}
