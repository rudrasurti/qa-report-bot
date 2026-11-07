"""QA Report Bot: turn JUnit XML results into a short Markdown report.

Works with any tool that writes JUnit XML (Robot Framework --xunit, Playwright,
pytest, TestNG, Jest). Marks a test as flaky when it failed and then passed
in the same run (the retry pattern most runners use).
"""
import argparse
import glob
import sys
import xml.etree.ElementTree as ET
from collections import OrderedDict

MARKER = "<!-- qa-report-bot -->"


def parse(paths):
    results = OrderedDict()  # test id -> list of outcomes in order
    durations = 0.0
    for path in paths:
        root = ET.parse(path).getroot()
        for case in root.iter("testcase"):
            tid = f"{case.get('classname', '')}::{case.get('name', '')}".strip(":")
            durations += float(case.get("time", 0) or 0)
            if case.find("skipped") is not None:
                outcome, msg = "skipped", ""
            else:
                bad = case.find("failure")
                if bad is None:
                    bad = case.find("error")
                outcome = "failed" if bad is not None else "passed"
                msg = (bad.get("message") or (bad.text or "")).strip().splitlines()[0][:200] if bad is not None else ""
            results.setdefault(tid, []).append((outcome, msg))
    return results, durations


def summarise(results):
    passed, failed, skipped, flaky, failures = 0, 0, 0, [], []
    for tid, runs in results.items():
        final = runs[-1][0]
        if final == "passed" and any(o == "failed" for o, _ in runs[:-1]):
            flaky.append(tid)
        if final == "passed":
            passed += 1
        elif final == "skipped":
            skipped += 1
        else:
            failed += 1
            failures.append((tid, runs[-1][1]))
    return passed, failed, skipped, flaky, failures


def render(title, passed, failed, skipped, flaky, failures, seconds):
    total = passed + failed + skipped
    status = "✅ All tests passed" if failed == 0 else f"❌ {failed} test(s) failed"
    lines = [MARKER, f"### {title}", "", f"**{status}**", "",
             "| Total | Passed | Failed | Skipped | Flaky | Time |",
             "|---|---|---|---|---|---|",
             f"| {total} | {passed} | {failed} | {skipped} | {len(flaky)} | {seconds:.1f}s |"]
    if failures:
        lines += ["", "<details><summary>Failed tests</summary>", ""]
        lines += [f"- `{tid}`: {msg}" for tid, msg in failures]
        lines += ["", "</details>"]
    if flaky:
        lines += ["", "⚠️ **Flaky tests** (failed, then passed on retry):", ""]
        lines += [f"- `{tid}`" for tid in flaky]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--junit", required=True, help="Glob for JUnit XML files")
    ap.add_argument("--title", default="Test results")
    ap.add_argument("--out", default="qa-report.md")
    args = ap.parse_args(argv)
    paths = sorted(glob.glob(args.junit, recursive=True))
    if not paths:
        print(f"No JUnit files match {args.junit}", file=sys.stderr)
        return 2
    results, seconds = parse(paths)
    p, f, s, fl, fails = summarise(results)
    md = render(args.title, p, f, s, fl, fails, seconds)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    print(f"failed={f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
