class Query():
    def __init__(self, query_text: str):
        self.query_text = query_text

    def query(self):
        return self.query_text

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return self.query_text == other.query_text

class NameQuery(Query):
    def __init__(self, name: str):
        super().__init__(name)

    @staticmethod
    def add_parser(p):
        p.add_argument("--name", metavar='string', type=str, help="Filter artifacts by name.")

class PathQuery(Query):
    def __init__(self, path: str):
        super().__init__(path)

    @staticmethod
    def add_parser(p):
        p.add_argument("--path", metavar='file|dir', type=str, help="Path of the artifact from NCA root")

class RelPathQuery(Query):
    def __init__(self, path: str):
        super().__init__(path)

    @staticmethod
    def add_parser(p):
        p.add_argument("--relpath", metavar='file|dir', type=str, help="Path of the artifact relative to git root")

class JqQuery(Query):
    def __init__(self, jq: str):
        super().__init__(jq)

    @staticmethod
    def add_parser(p):
        p.add_argument("--jq", metavar='string', type=str, help="Jq on meta-data.")

class AndQuery(Query):
    def __init__(self, *args):
        super().__init__("and")
        self.queries = args
