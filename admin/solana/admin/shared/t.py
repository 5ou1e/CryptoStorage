from django.contrib.admin.options import IncorrectLookupParameters  # noqa
from django.contrib.admin.sites import AdminSite
from unfold.admin import ModelAdmin


class GenericChangeListAdmin:

    def get_queryset(self, *args, **kwargs):
        return self._queryset

    def has_change_permission(self, *args, **kwargs):
        return False

    def __init__(self, title, queryset, model_admin_class=None, **kwargs):
        # create a dummy model admin instance
        model = queryset.model
        admin_site = AdminSite(name=title)
        # if not model_admin_class:
        #     model_admin_class = ModelAdmin
        model_admin = model_admin_class(model=model, admin_site=admin_site)

        model_admin.get_queryset = self.get_queryset
        model_admin.has_change_permission = self.has_change_permission

        # set input attributes
        for name, value in kwargs.items():
            setattr(model_admin, name, value)

        self._queryset = queryset
        self._model_admin = model_admin

    def __getattr__(self, name):
        # called when attribute not found
        allowed_attrs = [
            "opts",
            "show_full_result_count",
            "ordering",
            "admin_site",
            "paginator",
            # functions
            "get_preserved_filters",
            "lookup_allowed",
            "get_ordering",
            "get_paginator",
            "get_search_results",
            "get_empty_value_display",
            "get_changelist_instance",
        ]
        if name in allowed_attrs:
            return getattr(self._model_admin, name)
        else:
            raise AttributeError("Attribute not allowed", name)


def get_change_list(
    title,
    request,
    queryset,
    ordering=None,
    model_admin_class=None,
    list_display=("__str__",),
    list_display_links=(),
    list_filter=(),
    url_for_result=None,
):
    # prepare generic model-admin
    model_admin = GenericChangeListAdmin(
        title=title,
        queryset=queryset,
        model_admin_class=model_admin_class,
        # ordering=ordering,
        list_display=list_display,
        list_display_links=list_display_links,
        list_filter=list_filter,
    )

    cl = model_admin.get_changelist_instance(request)
    cl.formset = None
    cl.url_for_result = url_for_result or _url_for_result
    return cl
