from django.db import models
from django.urls import reverse


class FacilityObject(models.Model):

    name = models.CharField(
        "Название производственного объекта",
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        "Уникальная строка идентификатор (slug)",
        max_length=100,
        unique=True
    )

    def get_url_kwargs(self):
        kwargs = {
            "facility_slug": self.slug,
        }
        return kwargs

    def get_absolute_url(self):
        kwargs = self.get_url_kwargs()
        return reverse(
            "movement-lists",
            kwargs=kwargs
        )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Производственный объект"
        verbose_name_plural = "Производственные объекты"
