class Iterator:
    def __init__(self, collection):
        self.collections = collection
        self.index = 0
        self.max = len(collection)

    def next_(self):
        self.index += 1
        if self.index > self.max - 1:
            self.index = 0
        return self.collections[self.index]

    def reversed_next(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.max - 1
        return self.collections[self.index]