NAME: {
    "median": (
        dict(zip(*df_to_columns(IDENTIFIER_STATS)))
        if groups
        else IDENTIFIER_STATS.item()
    ),
}
