PRIVACY_UNIT_BLOCK
PRIVACY_LOSS_BLOCK
context = dp.Context.compositor(
    data=pl.scan_csv(CSV_PATH, encoding="utf8-lossy").with_columns(COLUMNS),
    privacy_unit=privacy_unit,
    privacy_loss=privacy_loss,
    split_by_weights=WEIGHTS,
    margins=MARGINS_DICT,
)
