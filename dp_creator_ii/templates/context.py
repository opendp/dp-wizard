PRIVACY_UNIT_BLOCK
context = dp.Context.compositor(
    data=pl.scan_csv(CSV_PATH, encoding="utf8-lossy"),
    privacy_unit=privacy_unit,
    privacy_loss=dp.loss_of(epsilon=LOSS),
    split_by_weights=WEIGHTS,
)
