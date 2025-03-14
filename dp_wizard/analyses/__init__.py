from dp_wizard.analyses import histogram, mean


def get_analysis_by_name(name):  # pragma: no cover
    match name:
        case histogram.name:
            return histogram
        case mean.name:
            return mean
        case _:
            raise Exception("Unexpected analysis")
