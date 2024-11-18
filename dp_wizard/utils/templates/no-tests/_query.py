QUERY_NAME = context.query().group_by(BIN_NAME).agg(pl.len().dp.noise())
ACCURACY_NAME = QUERY_NAME.summarize(alpha=1 - confidence)["accuracy"].item()
HISTOGRAM_NAME = QUERY_NAME.release().collect().sort(BIN_NAME)
plot_histogram(HISTOGRAM_NAME, ACCURACY_NAME, 0)
