from django.db import models
from django.contrib.auth import get_user_model


class HistoryMixin(models.Model):

    modified_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True
    )
    modified_datetime = models.DateTimeField("Время внесения изменений")
    serialized_prev_delta = models.TextField("Данные до изменения")
    serialized_post_delta = models.TextField("Данные после изменения")

    class Meta:
        abstract = True
