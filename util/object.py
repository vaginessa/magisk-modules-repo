
class _Dict(dict):
    def __init__(self, seq=None, **kwargs):
        if seq is None:
            seq = kwargs
        else:
            seq.update(kwargs)

        super().__init__(seq)

        for key in self.keys():
            self.__setattr__(key, self.get(key))

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        self.__setitem__(key, value)

    def __getattr__(self, item):
        if item not in self.__dict__:
            return None
        else:
            return self.__dict__[item]

    @property
    def dict(self):
        return self.copy()


class _List(list):
    def __init__(self, seq=None):
        super().__init__()
        if seq is not None:
            self.extend(seq)

    @property
    def size(self):
        return self.__len__()

    @property
    def dict2dict_(self):
        for i in range(self.__len__()):
            o = self.__getitem__(i)
            if type(o) is dict:
                self.__setitem__(i, _Dict(o))
        return _List(self.copy())

    @property
    def dict_2dict(self):
        for i in range(self.__len__()):
            o = self.__getitem__(i)
            if type(o) is _Dict:
                self.__setitem__(i, o.dict)
        return _List(self.copy())


dict_ = _Dict
list_ = _List
