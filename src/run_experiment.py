"""
RBL-4 LLM Runner (Phuc).

Reads a sample CSV of GitHub bug reports, runs each one through GPT-4o mini
using the frozen prompt, parses the JSON answer into OB/EB/S2R labels, and writes:
  - one row per issue into  results/<mode>_llm_output.csv      (matches repo template)
  - one line per call into   results/<mode>_api_log.txt          (matches repo template)

Run from the REPO ROOT so that data/ and results/ resolve correctly, e.g.:
  python src/run_experiment.py --mode pilot --mock     # offline test, no key
  python src/run_experiment.py --mode pilot            # real run (needs key + data)
  python src/run_experiment.py --mode full             # week 8

Design choices that make it play nice with the GitHub repo:
  - MOCK output goes to results/_mock/ (gitignored) so it NEVER touches the
    real repo files. Real output goes to results/ (the committed templates).
  - The repo ships results/<mode>_llm_output.csv and _api_log.txt as
    placeholder templates. On a real run we auto-clean those placeholders so
    the real output stays clean (real progress rows are preserved for resume).
  - Checkpoint/resume: already-processed issues are skipped, so a crash or a
    rate-limit interruption never re-spends money or duplicates rows.
  - INVALID handling: empty / unparseable / wrong-schema responses are marked
    raw_json_status=INVALID with BLANK labels (labels are never guessed).
"""

import argparse
import csv
import json
import os
from datetime import datetime, timezone

from prompt_config import (
    SYSTEM_PROMPT, build_user_prompt,
    MODEL_API_ID, TEMPERATURE, PROMPT_VERSION,
    ALLOWED_LABELS, COMPONENTS,
)
from llm_client import call_llm, estimate_cost


# Must match results/<mode>_llm_output.csv template on the repo, exactly.
OUTPUT_COLUMNS = [
    "repo", "issue_id", "issue_url",
    "model", "temperature", "prompt_version",
    "llm_ob_label", "llm_ob_reason",
    "llm_eb_label", "llm_eb_reason",
    "llm_s2r_label", "llm_s2r_reason",
    "raw_json_status", "run_timestamp",
]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def strip_code_fences(text):
    """Remove ``` / ```json fences if the model added them. Defensive even in
    JSON mode; costs nothing and prevents a whole class of parse failures."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else ""
        if t.endswith("```"):
            t = t[:-3]
    return t.strip()


def blank_label_fields():
    fields = {f"llm_{c.lower()}_label": "" for c in COMPONENTS}
    fields.update({f"llm_{c.lower()}_reason": "" for c in COMPONENTS})
    return fields


def parse_and_validate(raw_text):
    """Turn the raw model text into labels.

    Returns (status, fields, error_message):
      status : "VALID" or "INVALID"
      fields : dict of llm_*_label / llm_*_reason (blank if INVALID)
      error  : "" if ok, else empty_response / parse_error / schema_error
    """
    if raw_text is None or raw_text.strip() == "":
        return "INVALID", blank_label_fields(), "empty_response"

    try:
        data = json.loads(strip_code_fences(raw_text))
    except json.JSONDecodeError:
        return "INVALID", blank_label_fields(), "parse_error"

    fields = {}
    for c in COMPONENTS:
        node = data.get(c)
        if not isinstance(node, dict) or "label" not in node:
            return "INVALID", blank_label_fields(), "schema_error"
        label = node.get("label")
        if label not in ALLOWED_LABELS:
            return "INVALID", blank_label_fields(), "schema_error"
        fields[f"llm_{c.lower()}_label"] = label
        fields[f"llm_{c.lower()}_reason"] = str(node.get("reason", ""))

    return "VALID", fields, ""


def clean_template_output(output_path):
    """The repo ships results/<mode>_llm_output.csv as a header + one blank
    template row. Strip blank rows so our real output stays clean, while
    PRESERVING any genuine rows already written (so resume still works)."""
    if not os.path.exists(output_path):
        return
    with open(output_path, newline="", encoding="utf-8") as f:
        real_rows = [r for r in csv.DictReader(f)
                     if str(r.get("issue_id", "")).strip() != ""]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for r in real_rows:
            writer.writerow({k: r.get(k, "") for k in OUTPUT_COLUMNS})


def clean_template_log(log_path):
    """The repo ships results/<mode>_api_log.txt as a text placeholder. If the
    file has no real log lines (none start with 'timestamp='), clear it before
    we append real ones. Real logs from a previous run are kept."""
    if not os.path.exists(log_path):
        return
    with open(log_path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    has_real = any(line.startswith("timestamp=") for line in lines)
    if not has_real:
        open(log_path, "w", encoding="utf-8").close()


def load_processed_keys(output_path):
    """Read (repo, issue_id) pairs already in the output CSV, for resume."""
    done = set()
    if not os.path.exists(output_path):
        return done
    with open(output_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            iid = str(row.get("issue_id", "")).strip()
            if iid:
                done.add((row.get("repo", ""), iid))
    return done


def append_output_row(output_path, row_dict):
    new_file = not os.path.exists(output_path)
    with open(output_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerow(row_dict)


def append_log(log_path, fields):
    line = " | ".join(f"{k}={v}" for k, v in fields.items())
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def select_rows(rows):
    """Use rows flagged selected_for_pilot if that column is filled; otherwise
    fall back to every row that has an issue_id."""
    flagged = [
        r for r in rows
        if str(r.get("selected_for_pilot", "")).strip().lower() in ("1", "true", "yes", "y")
    ]
    if flagged:
        return flagged
    return [r for r in rows if str(r.get("issue_id", "")).strip() != ""]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["pilot", "full"], default="pilot")
    parser.add_argument("--mock", action="store_true",
                        help="use offline mock LLM (no key, no cost)")
    parser.add_argument("--input", default=None, help="override input CSV path")
    args = parser.parse_args()

    input_path = args.input or f"data/{args.mode}_sample.csv"

    # MOCK writes to results/_mock/ (gitignored) so it never touches repo files.
    results_dir = "results/_mock" if args.mock else "results"
    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, f"{args.mode}_llm_output.csv")
    log_path = os.path.join(results_dir, f"{args.mode}_api_log.txt")

    if not args.mock:
        from dotenv import load_dotenv
        load_dotenv()
        if not os.getenv("OPENAI_API_KEY"):
            raise SystemExit(
                "OPENAI_API_KEY not found. Copy .env.example to .env and fill it in, "
                "or run with --mock for offline testing."
            )

    # Make the repo's placeholder templates clean before a real run.
    clean_template_output(output_path)
    clean_template_log(log_path)

    with open(input_path, newline="", encoding="utf-8-sig") as f: 
        all_rows = list(csv.DictReader(f))
    rows = select_rows(all_rows)

    processed = load_processed_keys(output_path)
    n_total = n_valid = n_invalid = 0

    for r in rows:
        repo = r.get("repo", "")
        issue_id = str(r.get("issue_id", "")).strip()
        if (repo, issue_id) in processed:
            continue  # checkpoint: already done -> skip (no re-spend, no dup)

        n_total += 1
        user_prompt = build_user_prompt(r.get("title", ""), r.get("body", ""))

        error_message = ""
        response_model = ""
        usage = None
        try:
            raw_text, response_model, usage = call_llm(
                SYSTEM_PROMPT, user_prompt, use_mock=args.mock
            )
            status, fields, error_message = parse_and_validate(raw_text)
        except Exception as e:  # network/SDK failure after all retries
            status = "INVALID"
            fields = blank_label_fields()
            error_message = f"api_error: {e}"

        if status == "VALID":
            n_valid += 1
        else:
            n_invalid += 1

        out_row = {
            "repo": repo,
            "issue_id": issue_id,
            "issue_url": r.get("issue_url", ""),
            "model": MODEL_API_ID,
            "temperature": TEMPERATURE,
            "prompt_version": PROMPT_VERSION,
            "raw_json_status": status,
            "run_timestamp": now_iso(),
            **fields,
        }
        append_output_row(output_path, out_row)

        append_log(log_path, {
            "timestamp": now_iso(),
            "repo": repo,
            "issue_id": issue_id,
            "response_model": response_model or "NA",
            "success_or_fail": "success" if status == "VALID" else "fail",
            "parse_status": status,
            "token_usage": usage if usage else "NA",
            "cost_usd": round(estimate_cost(usage), 6),
            "error_message": error_message or "NA",
        })

    invalid_rate = (n_invalid / n_total * 100) if n_total else 0.0
    print("==== RUN SUMMARY ====")
    print(f"mode           : {args.mode}  (mock={args.mock})")
    print(f"input          : {input_path}")
    print(f"newly processed: {n_total}")
    print(f"VALID          : {n_valid}")
    print(f"INVALID        : {n_invalid}")
    print(f"invalid_rate   : {invalid_rate:.1f}%   (investigate before scaling if > 20%)")
    print(f"output -> {output_path}")
    print(f"log    -> {log_path}")


if __name__ == "__main__":
    main()
