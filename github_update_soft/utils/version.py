class Version:
    def __init__(self, version_str):
        self.version_str = version_str
        self.version_parts = self.parse_version(version_str)

    def parse_version(self, version_str):
        return list(map(int, version_str.split(".")))

    def __lt__(self, other):
        return self.version_parts < other.version_parts

    def __le__(self, other):
        return self.version_parts <= other.version_parts

    def __eq__(self, other):
        return self.version_parts == other.version_parts

    def __ne__(self, other):
        return self.version_parts != other.version_parts

    def __gt__(self, other):
        return self.version_parts > other.version_parts

    def __ge__(self, other):
        return self.version_parts >= other.version_parts

    def __str__(self):
        return self.version_str

    def __repr__(self):
        return f"Version({self.version_str})"