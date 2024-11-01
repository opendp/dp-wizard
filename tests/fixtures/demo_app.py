from shiny import App

from dp_creator_ii.app import app_ui, make_server_from_cli_info


app = App(app_ui, make_server_from_cli_info((None, None, True)))
