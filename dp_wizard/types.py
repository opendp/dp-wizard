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
    """

    pass


class ColumnIdentifier(str):
    """
    A human-readable form that is a valid Python identifier.
    """

    pass
