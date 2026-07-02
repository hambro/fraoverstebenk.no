from fraoverstebenk.app import create_app


def test_create_app_returns_flask_app() -> None:
    app = create_app()
    assert app.name == "fraoverstebenk.app"


def test_config_overrides_are_applied() -> None:
    app = create_app({"CONTENT_DIR": "somewhere"})
    assert app.config["CONTENT_DIR"] == "somewhere"
