import pathlib
import report

FIX = pathlib.Path(__file__).parent / "fixtures"


def run(name, tmp_path):
    out = tmp_path / "r.md"
    assert report.main(["--junit", str(FIX / name), "--out", str(out)]) == 0
    return out.read_text()


def test_all_passed(tmp_path):
    md = run("pass.xml", tmp_path)
    assert "All tests passed" in md
    assert "| 3 | 2 | 0 | 1 | 0 |" in md


def test_failures_and_flaky(tmp_path):
    md = run("mixed.xml", tmp_path)
    assert "1 test(s) failed" in md
    assert "checkout::finish" in md and "Thank you" in md
    assert "Flaky tests" in md and "cart::add item" in md


def test_no_files_returns_2(tmp_path):
    assert report.main(["--junit", str(tmp_path / "none*.xml")]) == 2


def test_marker_for_comment_updates(tmp_path):
    assert run("pass.xml", tmp_path).startswith(report.MARKER)
