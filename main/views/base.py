from django.views.generic.base import RedirectView


class DefaultRedirect(RedirectView):
    """
    Редирект на страницу производственного объекта по умолчанию
    """

    permanent = False
    pattern_name = "movement-lists"
