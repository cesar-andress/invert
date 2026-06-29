class FeaturePipeline:
    def __init__(self, x, feature_a_fn, feature_b_fn, feature_c_fn):
        self.feature_a = feature_a_fn(x)
        self.feature_b = feature_b_fn(x)
        self.feature_c = feature_c_fn(x)

    def get_feature_a(self):
        return self.feature_a

    def get_feature_b(self):
        return self.feature_b

    def get_feature_c(self):
        return self.feature_c
