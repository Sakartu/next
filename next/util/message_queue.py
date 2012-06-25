class MessageQueue(object):
    def __init__(self):
        self.in_stack = []
        self.out_stack = []

    def push(self, obj):
        self.in_stack.append(obj)

    def pop(self):
        if not self.out_stack:
            self.in_stack.reverse()
            self.out_stack = self.in_stack
            self.in_stack = []
        return self.out_stack.pop()

    def next(self):
        try:
            return self.pop()
        except:
            raise StopIteration  # end of iteration

    def __iter__(self):
        return self

    def __str__(self):
        result = []
        result.extend(reversed(self.in_stack))
        result.extend(self.out_stack)
        return '\n'.join(result)

    def __repr__(self):
        result = []
        result.extend(reversed(self.in_stack))
        result.extend(self.out_stack)
        return repr(result)
