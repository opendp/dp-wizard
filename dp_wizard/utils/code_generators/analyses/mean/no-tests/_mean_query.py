groups = GROUP_NAMES
QUERY_NAME = (
    context.query().group_by(groups).agg(CONFIG_NAME)
    if groups
    else context.query().select(CONFIG_NAME)
)
STATS_NAME = QUERY_NAME.release().collect()
STATS_NAME
