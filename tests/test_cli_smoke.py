
from click.testing import CliRunner
from PIL import Image

from image_similarity.cli import cli


def test_init_scan_search_mock(tmp_path):
    photos = tmp_path / "photos"
    photos.mkdir()
    index_root = tmp_path / "indexes"
    Image.new("RGB", (32, 32), color=(255, 0, 0)).save(photos / "a.png")
    Image.new("RGB", (32, 32), color=(254, 0, 0)).save(photos / "b.png")
    runner = CliRunner()
    assert runner.invoke(
        cli,
        ["init", "demo", "--root", str(photos), "--index-root", str(index_root)],
    ).exit_code == 0
    assert runner.invoke(
        cli,
        ["scan", "demo", "--index-root", str(index_root)],
    ).exit_code == 0
    r = runner.invoke(
        cli,
        [
            "search",
            "demo",
            "--query",
            str(photos / "a.png"),
            "--top-k",
            "2",
            "--index-root",
            str(index_root),
        ],
    )
    assert r.exit_code == 0
    assert "a.png" in r.output
