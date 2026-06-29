class FeaturePipeline:

    def __init__(self, x, feature_a_fn, feature_b_fn, feature_c_fn):
        self.x = x
        self.feature_a_fn = feature_a_fn
        self.feature_b_fn = feature_b_fn
        self.feature_c_fn = feature_c_fn
        self._feature_a = None
        self._feature_b = None
        self._feature_c = None
        self._computed = set()

    def get_feature_a(self):
        if 'a' not in self._computed:
            self._feature_a = self.feature_a_fn(self.x)
            self._computed.add('a')
        return self._feature_a

    def get_feature_b(self):
        if 'b' not in self._computed:
            self._feature_b = self.feature_b_fn(self.x)
            self._computed.add('b')
        return self._feature_b

    def get_feature_c(self):
        if 'c' not in self._computed:
            self._feature_c = self.feature_c_fn(self.x)
            self._computed.add('c')
        return self._feature_c