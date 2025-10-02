query = stats_context.query()
identifier_column = IDENTIFIER_COLUMN
if identifier_column is not None:
    query = query.truncate_per_group(IDENTIFIER_TRUNCATION)

groups = GROUP_NAMES
QUERY_NAME = (
    query.group_by(groups).agg(EXPR_NAME) if groups else query.select(EXPR_NAME)
)
STATS_NAME = QUERY_NAME.release().collect()
STATS_NAME
