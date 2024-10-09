from shiny import ui, reactive


def analysis_ui():
    return ui.nav_panel(
        "Define Analysis",
        ui.markdown(
            "Select numeric columns of interest in *TODO*, "
            "and for each numeric column indicate the expected range, "
            "the number of bins for the histogram, "
            "and its relative share of the privacy budget."
        ),
        ui.markdown(
            "[TODO: Column selection]"
            "(https://github.com/opendp/dp-creator-ii/issues/33)"
        ),
        ui.markdown(
            "What is your privacy budget for this release? "
            "Values above 1 will add less noise to the data, "
            "but have greater risk of revealing individual data."
        ),
        ui.markdown(
            "[TODO: Logarithmic slider]"
            "(https://github.com/opendp/dp-creator-ii/issues/25)"
        ),
        ui.markdown(
            "## Preview\n"
            "These plots assume a normal distribution for the columns you've selected, "
            "and demonstrate the effect of different parameter choices."
        ),
        ui.markdown("TODO"),
        ui.input_action_button("go_to_results", "Download results"),
        value="analysis_panel",
    )


def analysis_server(input, output, session):
    @reactive.effect
    @reactive.event(input.go_to_results)
    def go_to_results():
        ui.update_navs("top_level_nav", selected="results_panel")
