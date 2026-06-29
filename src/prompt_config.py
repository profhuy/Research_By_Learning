"""
Frozen prompt configuration for the RBL-4 experiment.

DO NOT EDIT the prompt text below. It is copied verbatim from
`prompt_final.md` (version v1.0). Changing it requires an approved
team amendment (see issue-handling-rules.md / team-assignment-master.md).
"""

PROMPT_VERSION = "v1.0"

# The model id used when calling the OpenAI API.
# The proposal fixes this to "GPT-4o mini" -> OpenAI API id "gpt-4o-mini".
MODEL_API_ID = "gpt-4o-mini"
TEMPERATURE = 0.0

# The four allowed labels. Any label outside this set => INVALID.
ALLOWED_LABELS = {"Sufficient", "Ambiguous", "Missing", "Incorrect"}

# The three components the model must score.
COMPONENTS = ("OB", "EB", "S2R")

SYSTEM_PROMPT = """You are evaluating the quality of a GitHub software bug report based ONLY on the text provided.
Do not assume information that is not present in the report.

Evaluate the following three components:
1. Observed Behavior (OB)
2. Expected Behavior (EB)
3. Steps to Reproduce (S2R)

For each component, assign exactly one label:
- "Sufficient": present and clear enough to act on.
- "Ambiguous": present but vague or unclear.
- "Missing": not stated anywhere in the report.
- "Incorrect": stated but contradictory, misleading, or clearly unusable.

Definitions:
- OB = what actually happened, what failed, or what wrong behavior was observed.
- EB = what the reporter expected to happen instead.
- S2R = the actions, sequence, setup, or conditions needed to reproduce the bug.

Important rules:
- Judge OB, EB, and S2R independently.
- Use only the issue title and body.
- Do not use outside knowledge.
- Do not infer missing details.
- If a component is absent, label it "Missing".
- If a component exists but is too vague to use, label it "Ambiguous".
- If a component exists and is clear enough to act on, label it "Sufficient".
- If a component exists but is contradictory or clearly wrong, label it "Incorrect".

Return STRICTLY this JSON object and nothing else:
{
  "OB": {"label": "...", "reason": "..."},
  "EB": {"label": "...", "reason": "..."},
  "S2R": {"label": "...", "reason": "..."}
}"""

USER_PROMPT_TEMPLATE = """Bug report:
Title: {{issue_title}}
Body:
{{issue_body}}"""


def build_user_prompt(issue_title, issue_body):
    """Fill the frozen user template with one issue's title and body.

    We use str.replace (NOT str.format) on purpose: SYSTEM_PROMPT contains
    literal { } braces (the JSON skeleton). Using .format anywhere near that
    text would crash. .replace is safe, explicit, and good enough here.
    """
    title = "" if issue_title is None else str(issue_title)
    body = "" if issue_body is None else str(issue_body)
    return (
        USER_PROMPT_TEMPLATE
        .replace("{{issue_title}}", title)
        .replace("{{issue_body}}", body)
    )
