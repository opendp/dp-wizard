"""
This is a target for pyinstaller.
"""

if __name__ == "__main__":
    import webbrowser

    import shiny

    host = "127.0.0.1"
    port = 8000

    shiny.run_app(
        app="dp_wizard.app",
        host=host,
        port=port,
        launch_browser=False,
        reload=False,
    )

    webbrowser.open(f"http://{host}:{port}/")
