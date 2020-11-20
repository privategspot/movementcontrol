class Link:

    def __init__(self, url, value):
        self._url = url
        self.value = value

    def __str__(self):
        return self._url
