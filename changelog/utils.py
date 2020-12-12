import json

from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder


class ChangeMeta:
    """
    Мета информация о изменении
    """

    CREATE_ACTION = "CREATE"
    UPDATE_ACTION = "UPDATE"
    DELETE_ACTION = "DELETE"
    RESTORE_ACTION = "RESTORE"

    def __init__(
        self,
        changed_by,
        model,
        model_pk,
        action=CREATE_ACTION,
        comment=None,
        prev_changes=None,
        post_changes=None,
        change_datetime=None,
        *args,
        **kwargs,
    ):
        self._action = action
        self._changed_by = changed_by
        self._model = model
        self._model_pk = model_pk
        self._comment = "" if not comment else comment
        self._change_datetime =\
            timezone.now() if not change_datetime else change_datetime
        self._prev_change =\
            {} if not prev_changes else prev_changes
        self._post_change =\
            {} if not post_changes else post_changes

    @property
    def action(self):
        return self._action

    def _get_prev_change(self):
        return self._prev_change

    def _set_prev_change(self, value):
        if type(value) is dict:
            self._prev_change = value
        else:
            raise TypeError("Value should be a dict")

    prev_change = property(_get_prev_change, _set_prev_change)

    def _get_post_change(self):
        return self._post_change

    def _set_post_change(self, value):
        if type(value) is dict:
            self._post_change = value
        else:
            raise TypeError("Value should be a dict")

    post_change = property(_get_post_change, _set_post_change)

    def get(self):
        return {
            "changed_by": self._changed_by,
            "change_datetime": self._change_datetime,
            "action": self._action,
            "model": self._model,
            "model_pk": self._model_pk,
            "comment": self._comment,
            "prev_change": self._prev_change,
            "post_change": self._post_change,
        }

    def get_json(self):
        data = self.get()
        data = json.dumps(data, cls=DjangoJSONEncoder)
        return data

    def get_prev_change_json(self):
        data = self.prev_change
        data = json.dumps(data, cls=DjangoJSONEncoder)
        return data

    def get_post_change_json(self):
        data = self.post_change
        data = json.dumps(data, cls=DjangoJSONEncoder)
        return data
