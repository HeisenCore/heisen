from addict import Dict


class Memory(Dict):
    def __init__(self, *args, **kwargs):
        self._name = kwargs.pop('_name')
        self._callback = kwargs.pop('_callback')

        super(Memory, self).__init__(*args, **kwargs)

    def __getitem__(self, name):
        if name not in self:
            self[name] = Memory(_name=self._name, _callback=self._callback)

        return super(Memory, self).__getitem__(name)

    def __setattr__(self, name, value):
        super(Memory, self).__setattr__(name, value)
        self._callback(self._name)

    def __delattr__(self, name):
        super(Memory, self).__delattr__(name)
        self._callback(self._name)

    def update(self, *args, **kwargs):
        notify = kwargs.pop('_notify', True)

        super(Memory, self).update(*args, **kwargs)

        if notify:
            self._callback(self._name)
