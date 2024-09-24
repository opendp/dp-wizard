context = dp.Context.compositor(
    data=pl.scan_csv(CSV_PATH),
    privacy_unit=dp.unit_of(contributions=UNIT),
    privacy_loss=dp.loss_of(epsilon=LOSS),
    split_by_weights=WEIGHTS,
)
