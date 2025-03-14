def get_analysis_by_name(name):  # pragma: no cover
    # Avoid circular import:
    from dp_wizard.analyses import histogram, mean

    match name:
        case histogram.name:
            return histogram
        case mean.name:
            return mean
        case _:
            raise Exception("Unrecognized analysis")
