from typing import Union

from django.db import models
from django.contrib.auth import get_user_model

from .models import ChangeLog
from .utils import ChangeMeta


class ChangeLogMixin(models.Model):
    """
    Миксин для автоматического создания исторических записей
    """

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(ChangeLogMixin, self).__init__(*args, **kwargs)
        self._original_values = {
            field.name: getattr(self, field.name)
            for field in self._meta.get_fields()
        }

    def _get_delta_names(self) -> list:
        """
        Возвращает имена измененных полей
        """
        names = []
        for field in self._meta.get_fields():
            name = field.name
            original = self._original_values[name]
            actual = getattr(self, name)
            if actual != original:
                names.append(name)
        return names

    def _get_changes(self, delta_names: list) -> dict:
        """
        Возвращает значение затронутых полей до и после изменений
        """
        prev = {}
        post = {}
        for name in delta_names:
            original = self._original_values[name]
            actual = getattr(self, name)
            prev[name] = original
            post[name] = actual
        delta = {
            "prev_change": prev,
            "post_change": post,
        }
        return delta

    def _update_original_values(self, delta_names: list):
        """
        Обновляет оригинальные значения на новые
        """
        for name in delta_names:
            self._original_values[name] = getattr(self, name)

    def _create_history_entry(self, meta: ChangeMeta):
        meta_dict = meta.get()
        log = ChangeLog.objects.create(
            change_datetime=meta_dict["change_datetime"],
            changed_by=meta_dict["change_by"],
            action=meta_dict["action"],
            model=meta_dict["model"],
            model_pk=["model_pk"],
            prev_change=meta.get_prev_change_json(),
            post_change=meta.get_post_change_json(),
            comment=meta_dict["comment"],
        )
        return log

    def _history_dispatch(self, meta: ChangeMeta) -> Union[ChangeLog, None]:
        """
        Выбор метода для действия
        """
        if meta.action == ChangeMeta.UPDATE_ACTION:
            delta = self._get_delta_names()
            changes = self._get_changes(delta)
            self._update_original_values(delta)
            meta.prev_change = changes["prev_change"]
            meta.post_change = changes["post_change"]
            return self._create_history_entry(meta)
        elif meta.action == ChangeMeta.CREATE_ACTION:
            return self._create_history_entry(meta)
        elif meta.action == ChangeMeta.DELETE_ACTION:
            return self._create_history_entry(meta)
        elif meta.action == ChangeMeta.RESTORE_ACTION:
            return self._create_history_entry(meta)
        return None

    def make_history(
        self,
        user: get_user_model(),
        action=ChangeMeta.CREATE_ACTION,
        comment=""
    ) -> Union[ChangeLog, None]:
        """
        Создаёт историческую запись ChangeLog
        в зависимости от типа действия
        """
        meta = ChangeMeta(
            action=action,
            changed_by=user,
            model=self._meta.model,
            model_pk=self._meta.pk,
            comment=comment
        )
        return self._history_dispatch(meta)
