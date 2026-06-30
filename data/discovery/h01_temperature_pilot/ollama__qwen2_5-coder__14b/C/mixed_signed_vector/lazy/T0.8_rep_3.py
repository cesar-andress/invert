class FeaturePipeline:
    def __init__(self, x, feature_a_fn, feature_b_fn, feature_c_fn):
        self.x = x
        self.feature_a_fn = feature_a_fn
        self.feature_b_fn = feature_b_fn
        self.feature_c_fn = feature_c_fn
        self._feature_a_cache = None
        self._feature_b_cache = None
        self._feature_c_cache = None

    def get_feature_a(self):
        if self._feature_a_cache is None:
            self._feature_a_cache = self.feature_a_fn(self.x)
        return self._feature_a_cache

    def get_feature_b(self):
        if self._feature_b_cache is None:
            self._feature_b_cache = self.feature_b_fn(self.x)
        return self._feature_b_cache

    def get_feature_c(self):
        if self._feature_c_cache is None:
            self._feature_c_cache = self.feature_c_fn(self.x)
        return self._feature_c_cache