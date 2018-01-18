class _GenConst(object):
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return u'<const: {}>'.format(self._name)


DEFAULT_SETTINGS = {}
SETTINGS_HEADER = u"""# madcc settings file
#
"""
