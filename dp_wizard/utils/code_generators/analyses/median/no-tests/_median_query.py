groups = GROUP_NAMES
QUERY_NAME = (
    stats_context.query().group_by(groups).agg(EXPR_NAME)
    if groups
    else stats_context.query().select(EXPR_NAME)
)
STATS_NAME = QUERY_NAME.release().collect()
STATS_NAME
