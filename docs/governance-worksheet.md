# Governance Worksheet — Module 5

## What I Shared With AI Tools

| Item shared | Risk | Reason | Safer future version | Ambiguity to resolve |
|---|---|---|---|---|
| Full application source code (`app/main.py`, `models.py`, `storage.py`, `business_rules.py`, `filters.py`) | Low | Course toy-project code with no real users. | Paste only the minimal relevant function, with configuration values removed. | Confirm no embedded credentials or unauthorized code. |
| Full test suite content (`tests/*.py`) | Low | Synthetic fixtures/assertions only. | Paste only the failing test and minimal fixture. | Confirm no real data in fixtures. |
| Frontend HTML/CSS/JS (`frontend/index.html`) | Low | No embedded tokens or private endpoints. | Share only the affected component, endpoints replaced with placeholders. | Confirm no embedded keys or PII. |
| `Dockerfile` and `.dockerignore` | Medium | Reveals internal build structure even without secrets. | Share only the relevant build stage, paths/registries replaced. | Confirm no credentials or production config included. |
| `.github/workflows/ci.yml` | Medium | Reveals repo internals, deployment architecture. | Paste only the relevant job, secrets/targets replaced. | Confirm no secret values or privileged credentials exposed. |
| `requirements.txt` | Low | Non-sensitive dependency metadata. | Paste only the relevant dependency/version. | Confirm no private package sources. |
| GitHub repository URLs | Medium | Connects conversation to specific accounts/identity. | Use placeholder repo URLs; state public/private separately. | Confirm repos were public; check for access-bearing URL params. |
| **GitHub Personal Access Tokens (pasted at least twice)** | **High** | Credentials permitting repository/account access. | Never paste; use a placeholder like `GITHUB_TOKEN=<redacted>`. | **Resolved: both tokens have been revoked.** |
| Full terminal output (local paths, Windows username) | Medium | Can reveal personal identifiers and machine structure. | Replace usernames/paths with placeholders. | Confirm no tokens/emails also present in the same output. |
| **Screenshots of GitHub account settings + personal email addresses** | **High** | Personal email is PII; account screenshots may expose security/recovery details. | Crop to exact UI element; blur emails/usernames/tokens. | Confirm no additional security/recovery info was exposed. |
| `systeminfo` output | Medium | Exposes machine/network context. | Share only generalized relevant fields. | Confirm no IP/MAC/domain info included. |
| `CLAUDE.md` / `AGENTS.md` | Medium | Reveals non-public repo structure and conventions. | Paste only the relevant instruction, org names replaced. | Confirm no secrets or proprietary business context. |
| Test/fake data only (e.g., "Buy milk") | Low | Clearly synthetic, no real-person data. | Continue using fictional values. | None — confirmed no real user data used. |

## Remediation Taken

Both GitHub Personal Access Tokens referenced in this course (generated on `uarm12` and `makr6136-a11y` accounts) were revoked via GitHub Settings → Developer Settings → Personal Access Tokens, following the High-risk classification identified in this review.

See `docs/ai-usage.md` for the traced code block and three governance rules derived from this worksheet.