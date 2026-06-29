class FeaturePipeline:

    def __init__(self, x, feature_a_fn, feature_b_fn, feature_c_fn):
        self.x = x
        self.feature_a_fn = feature_a_fn
        self.feature_b_fn = feature_b_fn
        self.feature_c_fn = feature_c_fn
        self._feature_a = None
        self._feature_b = None
        self._feature_c = None

    def get_feature_a(self):
        if self._feature_a is None:
            self._feature_a = self.feature_a_fn(self.x)
        return self._feature_a

    def get_feature_b(self):
        if self._feature_b is None:
            self._feature_b = self.feature_b_fn(self.x)
        return self._feature_b

    def get_feature_c(self):
        if self._feature_c is None:
            self._feature_c = self.feature_c_fn(self.x)
        return self._feature_c