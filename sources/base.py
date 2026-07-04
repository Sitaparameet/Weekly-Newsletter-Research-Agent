from model import Article


class BaseSource:
    """
    All sources must implement fetch() and return List[Article].
    This ensures MCP/API/RSS are interchangeable.
    """

    def fetch(self):
        raise NotImplementedError("Source must implement fetch()")