class x0:

    def __init__(self, x1, x2, x3, x4):
        self.x = x1
        self.feature_a_fn = x2
        self.feature_b_fn = x3
        self.feature_c_fn = x4
        self._feature_a = None
        self._feature_b = None
        self._feature_c = None
        self._computed = x5()

    def x6(self):
        if 'a' not in self._computed:
            self._feature_a = self.feature_a_fn(self.x)
            self._computed.add('a')
        return self._feature_a

    def x7(self):
        if 'b' not in self._computed:
            self._feature_b = self.feature_b_fn(self.x)
            self._computed.add('b')
        return self._feature_b

    def x8(self):
        if 'c' not in self._computed:
            self._feature_c = self.feature_c_fn(self.x)
            self._computed.add('c')
        return self._feature_c