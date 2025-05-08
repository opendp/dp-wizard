title = (
    f"DP means for COLUMN_NAME, "
    f"assuming {contributions} contributions per individual"
)

if groups:
    title += f" (grouped by {'/'.join(groups)})"
plot_bars(STATS_NAME, error=0, cutoff=0, title=title)
