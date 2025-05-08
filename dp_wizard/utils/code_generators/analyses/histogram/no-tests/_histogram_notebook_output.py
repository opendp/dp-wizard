# CONFIDENCE_NOTE
column_name = COLUMN_NAME
title = (
    f"DP counts for {column_name}, "
    f"assuming {contributions} contributions per individual"
)

if groups:
    title += f" (grouped by {'/'.join(groups)})"
plot_bars(HISTOGRAM_NAME, error=ACCURACY_NAME, cutoff=0, title=title)
