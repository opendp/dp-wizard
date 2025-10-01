query = stats_context.query()
identifier_column = IDENTIFIER_COLUMN
if identifier_column is not None:
    query = query.truncate_per_group(10)  # todo: real value

groups = [BIN_NAME] + GROUP_NAMES
QUERY_NAME = query.group_by(groups).agg(pl.len().dp.noise().alias("count"))
ACCURACY_NAME = QUERY_NAME.summarize(alpha=1 - confidence)["accuracy"].item()
STATS_NAME = QUERY_NAME.release().collect()
STATS_NAME
