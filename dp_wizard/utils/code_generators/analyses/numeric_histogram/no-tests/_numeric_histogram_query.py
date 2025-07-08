groups = [BIN_NAME] + GROUP_NAMES
QUERY_NAME = context.query().group_by(groups).agg(pl.len().dp.noise().alias("count"))
ACCURACY_NAME = QUERY_NAME.summarize(alpha=1 - confidence)["accuracy"].item()
STATS_NAME = QUERY_NAME.release().collect()
STATS_NAME
