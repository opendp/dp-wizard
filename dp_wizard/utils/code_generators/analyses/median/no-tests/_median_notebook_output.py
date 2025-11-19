if groups:
    title = f"DP medians for COLUMN_NAME, assuming {contributions} contributions per individual"  # noqa: B950
    plot_bars(STATS_NAME, error=0, cutoff=0, title=title)
