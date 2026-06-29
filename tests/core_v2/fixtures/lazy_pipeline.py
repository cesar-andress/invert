class FeaturePipeline:
    def __init__(self, x, feature_a_fn, feature_b_fn, feature_c_fn):
        self._x = x
        self._feature_a_fn = feature_a_fn
        self._feature_b_fn = feature_b_fn
        self._feature_c_fn = feature_c_fn
        self._a = None
        self._b = None
        self._c = None

    def get_feature_a(self):
        if self._a is None:
            self._a = self._feature_a_fn(self._x)
        return self._a

    def get_feature_b(self):
        if self._b is None:
            self._b = self._feature_b_fn(self._x)
        return self._b

    def get_feature_c(self):
        if self._c is None:
            self._c = self._feature_c_fn(self._x)
        return self._c
