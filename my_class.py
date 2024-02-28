class Info:
    def __init__(self, url=None, idx=None):
        self.idx = idx
        self.url = url
        self.error = []
        self.name = None
        self.cv = None
        self.tag = None

    def set_name(self, name):
        self.name = name

    def set_cv(self, cv):
        self.cv = cv

    def set_tag(self, tag):
        self.tag = tag

    def add_error(self, error):
        self.error.append(error)

    def clear_error(self):
        self.error = []

    def error_empty(self):
        if len(self.error) == 0:
            return True
        return False


class Item:
    def __init__(self, info, societies_name, series_name=None):
        if info.tag is None:
            self.tag = []
        else:
            self.tag = info.tag

        if info.cv is None:
            self.cv = []
        else:
            self.cv = info.cv

        if series_name is not None:
            self.series_name = series_name

        self.societies_name = societies_name
        self.name = info.name
        self.idx = info.idx
