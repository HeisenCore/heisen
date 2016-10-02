from addict import Dict


class Memory(Dict):
    def __init__(self, *args, **kwargs):
        self._name = kwargs.pop('_name')
        self._callback = kwargs.pop('_callback')

        super(Memory, self).__init__(*args, **kwargs)

    def __getitem__(self, name):
        if name not in self and name not in ['_name', '_callback']:
            self[name] = Memory(_name=self._name, _callback=self._callback)

        return super(Memory, self).__getitem__(name)

    def __setattr__(self, name, value):
        super(Memory, self).__setattr__(name, value)

        if name not in ['_name', '_callback']:
            self._callback(self._name)

    def __delattr__(self, name):
        super(Memory, self).__delattr__(name)

        if name not in ['_name', '_callback']:
            self._callback(self._name)

    def update(self, *args, **kwargs):
        notify = kwargs.pop('_notify', True)

        super(Memory, self).update(*args, **kwargs)

        if notify:
            self._callback(self._name)

    def to_dict(self):
        """ Recursively turn your addict Dicts into dicts. """
        base = {}
        for key, value in self.items():
            if isinstance(value, type(self)):
                base[key] = value.to_dict()

            elif isinstance(value, (list, tuple)):
                base[key] = type(value)(
                    item.to_dict() if isinstance(item, type(self)) else
                    item for item in value)
            else:
                base[key] = value

        base.pop('_name', None)
        base.pop('_callback', None)

        return base
