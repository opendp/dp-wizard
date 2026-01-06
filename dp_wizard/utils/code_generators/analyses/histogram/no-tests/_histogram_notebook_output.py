# CONFIDENCE_NOTE
title = (
    f"DP counts for COLUMN_NAME, "
    f"assuming {contributions} contributions per individual"
)

group_names = GROUP_NAMES
if group_names:
    title += f" (grouped by {'/'.join(group_names)})"
plot_bars(HISTOGRAM_NAME, title=title, error=ACCURACY_NAME)
