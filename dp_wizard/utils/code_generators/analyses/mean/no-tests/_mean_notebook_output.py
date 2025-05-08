title = (
    f"DP means for COLUMN_NAME, "
    f"assuming {contributions} contributions per individual"
)

group_names = GROUP_NAMES
if group_names:
    title += f" (grouped by {'/'.join(group_names)})"
plot_bars(STATS_NAME, error=0, cutoff=0, title=title)
