label_width = "10em"  # Just wide enough so the text isn't trucated.
col_widths = {
    # Controls stay roughly a constant width;
    # Graph expands to fill space.
    "sm": [4, 8],
    "md": [3, 9],
    "lg": [2, 10],
}

default_weight = "2"
weight_choices = {
    "1": "Less accurate",
    default_weight: "Default",
    "4": "More accurate",
}

bounds_tooltip_text = """
DP requires that we limit the sensitivity to the contributions
of any individual. To do this, we need an estimate of the lower
and upper bounds for each variable. We should not look at the
data when estimating the bounds! In this case, we could imagine
that "class year" would vary between 1 and 4, and we could limit
"grade" to values between 50 and 100.
"""
