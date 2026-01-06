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


def make_exponential_cut_points(extreme: float) -> list[int]:
    """
    Returns exponentially spaced cut points

    >>> make_exponential_cut_points(500)
    [0, 1, 10, 100, 1000]
    >>> make_exponential_cut_points(-100)
    [-100, -10, -1, 0]
    """
    from math import ceil, log10

    log_extreme = ceil(log10(abs(extreme)))
    cut_points = [0] + [10**exponent for exponent in range(log_extreme + 1)]
    if extreme < 0:
        return list(reversed([-point for point in cut_points]))
    return cut_points
