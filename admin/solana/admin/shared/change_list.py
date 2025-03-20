from django.contrib.admin.options import IncorrectLookupParameters  # noqa
from django.contrib.admin.sites import AdminSite
from unfold.admin import ModelAdmin


class GenericChangeListAdmin:

    def get_queryset(self, *args, **kwargs):
        return self._queryset

    def has_change_permission(self, *args, **kwargs):
        return False

    def __init__(self, title, queryset, **kwargs):
        # create a dummy model admin instance
        model = queryset.model
        admin_site = AdminSite(name=title)
        model_admin = ModelAdmin(model=model, admin_site=admin_site)

        model_admin.get_queryset = self.get_queryset
        model_admin.has_change_permission = self.has_change_permission

        # set input attributes
        for name, value in kwargs.items():
            setattr(model_admin, name, value)

        # some defaults to disallow editing
        model_admin.actions = None
        model_admin.list_editable = ()
        # model_admin.list_filter_sheet = kwargs.get('list_filter_sheet', False)
        model_admin.list_fullwidth = True

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


def _url_for_result(result):
    return result.get_absolute_url()


def get_change_list(
    title,
    request,
    queryset,
    ordering=None,
    list_display=("__str__",),
    list_display_links=(),
    list_filter=(),
    list_filter_sheet=False,
    list_filter_submit=False,
    actions_row=None,
    date_hierarchy=None,
    search_fields=(),
    list_select_related=False,
    list_per_page=25,
    list_max_show_all=100,
    sortable_by=None,
    search_help_text=None,
    show_full_result_count=True,
    url_for_result=None,
):
    # prepare generic model-admin
    model_admin = GenericChangeListAdmin(
        title=title,
        queryset=queryset,
        ordering=ordering,
        list_display=list_display,
        list_display_links=list_display_links,
        list_filter=list_filter,
        list_filter_sheet=list_filter_sheet,
        list_filter_submit=list_filter_submit,
        actions_row=actions_row,
        date_hierarchy=date_hierarchy,
        search_fields=search_fields,
        list_select_related=list_select_related,
        list_per_page=list_per_page,
        list_max_show_all=list_max_show_all,
        sortable_by=sortable_by,
        search_help_text=search_help_text,
        show_full_result_count=show_full_result_count,
    )

    cl = model_admin.get_changelist_instance(request)
    cl.formset = None
    cl.url_for_result = url_for_result or _url_for_result
    return cl
