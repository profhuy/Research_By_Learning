"""
RBL-4 LLM Runner (Phuc) - prompt v3 variant.

This is the same runner flow as run_experiment.py, but it binds to
prompt_config_v3 so the team can rerun full experiment safely without
editing the main runner by hand.
"""

import argparse
import csv
import json
import os
from datetime import datetime, timezone

from prompt_config_v3 import (
    SYSTEM_PROMPT,
    build_user_prompt,
    MODEL_API_ID,
    TEMPERATURE,
    PROMPT_VERSION,
    ALLOWED_LABELS,
    COMPONENTS,
)
from llm_client import call_llm, estimate_cost

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
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.endswith("```"):
            text = text[:-3]
    return text.strip()


def blank_label_fields():
    fields = {f"llm_{component.lower()}_label": "" for component in COMPONENTS}
    fields.update({f"llm_{component.lower()}_reason": "" for component in COMPONENTS})
    return fields


def parse_and_validate(raw_text):
    if raw_text is None or raw_text.strip() == "":
        return "INVALID", blank_label_fields(), "empty_response"

    try:
        data = json.loads(strip_code_fences(raw_text))
    except json.JSONDecodeError:
        return "INVALID", blank_label_fields(), "parse_error"

    fields = {}
    for component in COMPONENTS:
        node = data.get(component)
        if not isinstance(node, dict) or "label" not in node:
            return "INVALID", blank_label_fields(), "schema_error"
        label = node.get("label")
        if label not in ALLOWED_LABELS:
            return "INVALID", blank_label_fields(), "schema_error"
        fields[f"llm_{component.lower()}_label"] = label
        fields[f"llm_{component.lower()}_reason"] = str(node.get("reason", ""))

    return "VALID", fields, ""


def clean_template_output(output_path):
    if not os.path.exists(output_path):
        return
    with open(output_path, newline="", encoding="utf-8") as handle:
        real_rows = [row for row in csv.DictReader(handle) if str(row.get("issue_id", "")).strip() != ""]
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in real_rows:
            writer.writerow({key: row.get(key, "") for key in OUTPUT_COLUMNS})


def clean_template_log(log_path):
    if not os.path.exists(log_path):
        return
    with open(log_path, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    if not any(line.startswith("timestamp=") for line in lines):
        open(log_path, "w", encoding="utf-8").close()


def load_processed_keys(output_path):
    done = set()
    if not os.path.exists(output_path):
        return done
    with open(output_path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            issue_id = str(row.get("issue_id", "")).strip()
            if issue_id:
                done.add((row.get("repo", ""), issue_id))
    return done


def append_output_row(output_path, row_dict):
    new_file = not os.path.exists(output_path)
    with open(output_path, "a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerow(row_dict)


def append_log(log_path, fields):
    line = " | ".join(f"{key}={value}" for key, value in fields.items())
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def select_rows(rows):
    flagged = [
        row for row in rows
        if str(row.get("selected_for_pilot", "")).strip().lower() in ("1", "true", "yes", "y")
    ]
    if flagged:
        return flagged
    return [row for row in rows if str(row.get("issue_id", "")).strip() != ""]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["pilot", "full"], default="pilot")
    parser.add_argument("--mock", action="store_true", help="use offline mock LLM (no key, no cost)")
    parser.add_argument("--input", default=None, help="override input CSV path")
    args = parser.parse_args()

    input_path = args.input or f"data/{args.mode}_sample.csv"
    results_dir = "results/_mock" if args.mock else "results"
    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, f"{args.mode}_llm_output.csv")
    log_path = os.path.join(results_dir, f"{args.mode}_api_log.txt")

    if not args.mock and not os.getenv("OPENAI_API_KEY"):
        env_path = ".env"
        if os.path.exists(env_path):
            with open(env_path, encoding="utf-8") as handle:
                for raw_line in handle:
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())
        if not os.getenv("OPENAI_API_KEY"):
            raise SystemExit(
                "OPENAI_API_KEY not found. Copy .env.example to .env and fill it in, "
                "or run with --mock for offline testing."
            )

    clean_template_output(output_path)
    clean_template_log(log_path)

    with open(input_path, newline="", encoding="utf-8-sig") as handle:
        all_rows = list(csv.DictReader(handle))
    rows = select_rows(all_rows)

    processed = load_processed_keys(output_path)
    n_total = n_valid = n_invalid = 0

    for row in rows:
        repo = row.get("repo", "")
        issue_id = str(row.get("issue_id", "")).strip()
        if (repo, issue_id) in processed:
            continue

        n_total += 1
        user_prompt = build_user_prompt(row.get("title", ""), row.get("body", ""))

        error_message = ""
        response_model = ""
        usage = None
        try:
            raw_text, response_model, usage = call_llm(SYSTEM_PROMPT, user_prompt, use_mock=args.mock)
            status, fields, error_message = parse_and_validate(raw_text)
        except Exception as exc:
            status = "INVALID"
            fields = blank_label_fields()
            error_message = f"api_error: {exc}"

        if status == "VALID":
            n_valid += 1
        else:
            n_invalid += 1

        out_row = {
            "repo": repo,
            "issue_id": issue_id,
            "issue_url": row.get("issue_url", ""),
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
