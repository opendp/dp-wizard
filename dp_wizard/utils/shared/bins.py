def round_2(number) -> float:
    """
    >>> round_2(1234)
    1200.0
    >>> round_2(0.001234)
    0.0012
    """
    return float(f"{number:.2g}")


def make_cut_points(
    lower_bound: float, upper_bound: float, bin_count: int
) -> list[float]:
    """
    Returns one more cut point than the bin_count,
    with the cut points rounded to two decimal places
    (There are actually two more bins, extending to
    -inf and +inf, but we'll ignore those.)

    Cut points are evenly spaced from lower_bound to upper_bound,

    >>> make_cut_points(0, 10, 2)
    [0.0, 5.0, 10.0]
    """
    bin_width = (upper_bound - lower_bound) / bin_count
    # Duplicate values would cause an error in Polars.
    # Use a set to return unique values.
    return sorted({round_2(lower_bound + i * bin_width) for i in range(bin_count + 1)})
