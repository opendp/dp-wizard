groups = [BIN_NAME] + GROUP_NAMES
QUERY_NAME = context.query().group_by(groups).agg(pl.len().dp.noise())
ACCURACY_NAME = QUERY_NAME.summarize(alpha=1 - confidence)["accuracy"].item()
HISTOGRAM_NAME = QUERY_NAME.release().collect()
HISTOGRAM_NAME
