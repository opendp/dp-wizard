if groups:
    title = (
        f"DP medians for COLUMN_NAME, "
        f"assuming {contributions} contributions per individual"
    )
    plot_bars(STATS_NAME, error=0, cutoff=0, title=title)
