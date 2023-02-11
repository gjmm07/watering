class Iterator:
    def __init__(self, collection, rw_control):
        self.collections = collection
        self.rw_control = rw_control
        self.index = 0
        self.max = len(collection)
        self.current = collection[0], rw_control[0]

    def next_(self):
        self.index += 1
        if self.index > self.max - 1:
            self.index = 0
        self.current = self.collections[self.index], self.rw_control[self.index]

    def reversed_next(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.max - 1
        self.current = self.collections[self.index], self.rw_control[self.index]
    
    def update_collection(self, collection):
        self.collection = collection
        self.current = self.collection[self.index], self.rw_control[self.index]