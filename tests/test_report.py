import opendp.prelude as dp
import opendp_logger
import polars as pl


def test_logger_for_reporting():
    # Details of this calculation may change.
    # Just want to get an object that we can exercise the logger against.

    # Information you've provided that applies to the whole calculation:
    # Data:
    csv_path = "/tmp/demo.csv"
    max_possible_rows = 1000000
    # Privacy unit:
    contributions = 10
    # Privacy loss:
    epsilon = 2
    weights = [4.0, 4.0, 1.0, 1.0]
    delta = 1e-7
    # Accuracy:
    alpha = 0.05

    # Public information you've provided for the "grade" column:
    grade_min = 50
    grade_max = 100
    grade_bins_count = 10

    # Public information you've provided for the "class_year" column:
    class_year_min = 1
    class_year_max = 4
    class_year_bins_count = 4

    # From the public information, determine the bins:
    grade_bins_list = list(
        range(grade_min, grade_max, int((grade_max - grade_min + 1) / grade_bins_count))
    )
    class_year_bins_list = list(
        range(
            class_year_min,
            class_year_max,
            int((class_year_max - class_year_min + 1) / class_year_bins_count),
        )
    )

    # Finally, define a Context using the provided information.

    context = dp.Context.compositor(
        data=pl.scan_csv(csv_path, encoding="utf8-lossy").with_columns(
            # The cut() method returns a Polars categorical type.
            # Cast to string to get the human-readable label.
            pl.col("grade").cut(grade_bins_list).alias("grade_bin").cast(pl.String),
            pl.col("class_year")
            .cut(class_year_bins_list)
            .alias("class_year_bin")
            .cast(pl.String),
        ),
        privacy_unit=dp.unit_of(contributions=contributions),
        privacy_loss=dp.loss_of(epsilon=epsilon, delta=delta),
        split_by_weights=weights,
        margins={
            (): dp.polars.Margin(
                max_partition_length=max_possible_rows,
                # To calculate the mean, we need to know the total number of entries,
                # but this is not by default public information. We must opt-in:
                public_info="lengths",
            ),
            ("grade_bin",): dp.polars.Margin(
                max_partition_length=max_possible_rows,
                public_info="keys",
            ),
            ("class_year_bin",): dp.polars.Margin(
                max_partition_length=max_possible_rows,
                public_info="keys",
            ),
        },
    )
