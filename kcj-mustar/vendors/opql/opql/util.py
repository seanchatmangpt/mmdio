class RunningId:
    def __init__(self, prefix="id", startvalue=0):
        self.prefix = prefix
        self.running_value = startvalue

    def get_next_id(self):
        temp = self.running_value
        self.running_value += 1
        return self.prefix + str(temp)