# groups = GROUP_NAMES
QUERY_NAME = context.query().select(
    pl.col(NAME).fill_null(0).dp.mean((LOWER_BOUND, UPPER_BOUND))
)
ACCURACY_NAME = QUERY_NAME.summarize(alpha=1 - confidence)["accuracy"].item()
STATS_NAME = QUERY_NAME.release().collect()
STATS_NAME
