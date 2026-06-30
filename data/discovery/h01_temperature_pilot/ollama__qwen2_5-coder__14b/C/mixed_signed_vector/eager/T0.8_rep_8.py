class FeaturePipeline:
    def __init__(self, x, feature_a_fn, feature_b_fn, feature_c_fn):
        self._feature_a = feature_a_fn(x)
        self._feature_b = feature_b_fn(x)
        self._feature_c = feature_c_fn(x)

    def get_feature_a(self):
        return self._feature_a

    def get_feature_b(self):
        return self._feature_b

    def get_feature_c(self):
        return self._feature_c