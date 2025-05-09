PRIVACY_UNIT_BLOCK
PRIVACY_LOSS_BLOCK
# See the OpenDP Library docs for more on Context:
# https://docs.opendp.org/en/stable/api/user-guide/context/index.html#context:
context = dp.Context.compositor(
    data=pl.scan_csv(CSV_PATH, encoding="utf8-lossy").with_columns(EXTRA_COLUMNS),
    privacy_unit=privacy_unit,
    privacy_loss=privacy_loss,
    split_by_weights=WEIGHTS,
    margins=MARGINS_LIST,
)
