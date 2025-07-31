class AnalysisName(str):
    """
    A name like "Histogram" or "Mean".
    """

    pass


class ColumnName(str):
    """
    The exact column header in the CSV.
    """

    pass


class ColumnLabel(str):
    """
    The column label displayed in the UI.
    """

    pass


class ColumnId(str):
    """
    The opaque string we pass as a module ID.

    If we just sanitize the user string, it might collide with another string.
    Hashing is safer, though hash collisions are not impossible.

    >>> import re
    >>> assert re.match(r'^[_0-9]+$', ColumnId('xyz'))
    """

    def __new__(cls, content):
        id = str(hash(content)).replace("-", "_")
        return str.__new__(cls, id)


class ColumnIdentifier(str):
    """
    A human-readable form that is a valid Python identifier.
    """

    pass
