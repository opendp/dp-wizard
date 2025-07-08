# CONFIDENCE_NOTE
column_name = COLUMN_NAME
title = (
    f"DP counts for {column_name}, "
    f"assuming {contributions} contributions per individual"
)

group_names = GROUP_NAMES
if group_names:
    title += f" (grouped by {'/'.join(group_names)})"
plot_bars(HISTOGRAM_NAME, error=ACCURACY_NAME, cutoff=0, title=title)
