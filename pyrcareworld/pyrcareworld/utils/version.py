class Version():
    def __init__(self, version_string: str):
        self.raw_string = version_string
        self.version = self.raw_string.split(".")
        self.version = [int(i) for i in self.version]
        while len(self.version) < 4:
            self.version.append(0)

    def __lt__(self, other):
        for i in range(4):
            if self.version[i] < other.version[i]:
                return True
            elif self.version[i] == other.version[i]:
                continue
        return False

    def __gt__(self, other):
        for i in range(4):
            if self.version[i] > other.version[i]:
                return True
            elif self.version[i] == other.version[i]:
                continue
        return False

    def __eq__(self, other):
        for i in range(4):
            if self.version[i] != other.version[i]:
                return False
        return True

    def __str__(self):
        return self.raw_string

    def __repr__(self):
        return self.raw_string

    def toString(self):
        return self.raw_string

    def __getitem__(self, index):
        return self.version[index]

    def __setitem__(self, index, value):
        self.version[index] = value

    @staticmethod
    def sorted(versions: list, reverse=False):
        return sorted(versions, key=lambda v: v.version, reverse=reverse)



