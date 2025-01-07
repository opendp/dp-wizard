# CONFIDENCE_NOTE
column_name = COLUMN_NAME
title = (
    f"DP counts for {column_name}, "
    f"assuming {contributions} contributions per invidual"
)
plot_histogram(HISTOGRAM_NAME, error=ACCURACY_NAME, cutoff=0, title=title)
