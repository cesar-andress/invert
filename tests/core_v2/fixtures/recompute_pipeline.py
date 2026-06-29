class FeaturePipeline:
    def __init__(self, x, feature_a_fn, feature_b_fn, feature_c_fn):
        self._x = x
        self._feature_a_fn = feature_a_fn
        self._feature_b_fn = feature_b_fn
        self._feature_c_fn = feature_c_fn

    def get_feature_a(self):
        return self._feature_a_fn(self._x)

    def get_feature_b(self):
        return self._feature_b_fn(self._x)

    def get_feature_c(self):
        return self._feature_c_fn(self._x)
