PRIVACY_UNIT_BLOCK
PRIVACY_LOSS_BLOCK
OPTIONAL_CSV_BLOCK
# See the OpenDP Library docs for more on Context:
# https://docs.opendp.org/en/OPENDP_VERSION/api/user-guide/context/index.html#context:
synth_context = dp.Context.compositor(
    data=pl.scan_csv(CSV_PATH, encoding="utf8-lossy"),
    privacy_unit=privacy_unit,
    privacy_loss=privacy_loss,
    # The release of the contingency table with be a single query,
    # so we don't need to split our budget across multiple queries.
    split_by_weights=[1],
)
