class WrongPipeline:
    def __init__(self, x):
        self._x = x

    def feature_a(self):
        return sum(v * v for v in self._x)
