from pathlib import Path

from fraoverstebenk.app import create_app
from fraoverstebenk.content import load_hats

REPO_ROOT = Path(__file__).parent.parent


def test_real_content_renders() -> None:
    app = create_app({"CONTENT_DIR": REPO_ROOT / "content", "TESTING": True})
    client = app.test_client()
    assert client.get("/").status_code == 200
    overview = client.get("/hatter/").get_data(as_text=True)
    assert "Solhatt" in overview
    assert client.get("/hatter/solhatt/").status_code == 200
    posts = client.get("/godt-a-vite/").get_data(as_text=True)
    assert "Stell av hatten" in posts


def test_referenced_images_exist() -> None:
    hats = load_hats(REPO_ROOT / "content")
    assert hats, "Fant ingen hatter i content/hatter"
    for hat in hats:
        image_path = REPO_ROOT / hat.image.lstrip("/")
        assert image_path.is_file(), f"Mangler bilde: {hat.image}"
