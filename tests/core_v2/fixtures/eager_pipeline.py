class FeaturePipeline:
    def __init__(self, x, feature_a_fn, feature_b_fn, feature_c_fn):
        self._a = feature_a_fn(x)
        self._b = feature_b_fn(x)
        self._c = feature_c_fn(x)

    def get_feature_a(self):
        return self._a

    def get_feature_b(self):
        return self._b

    def get_feature_c(self):
        return self._c
