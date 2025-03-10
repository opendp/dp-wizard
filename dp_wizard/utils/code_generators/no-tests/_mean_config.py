CONFIG_NAME = pl.col(COLUMN_NAME).fill_null(0).dp.mean((LOWER_BOUND, UPPER_BOUND))
