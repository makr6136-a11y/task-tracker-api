# Release Evidence

This file consolidates the core evidence that the Task Tracker is working,
released correctly, and that AI usage throughout this project was reviewed
rather than accepted blindly.

## 1. Baseline Check

Command: `pytest -v` (run on the `final-project` branch, after merging
`mid-course-project`'s search feature into `main`)

Result: **37 passed, 0 failed**

This confirms the full test suite — covering CRUD, validation, status
transitions, due dates, the overdue filter, and search — passes on the
exact branch being released.

## 2. CI Check

Workflow: `.github/workflows/ci.yml`, run on every `push` and `pull_request`.

Evidence: **CI #28**, triggered by commit `5578242` on `final-project`,
status **Success**, completed in 22 seconds.
https://github.com/makr6136-a11y/task-tracker-api/actions/runs/30741891647

This is a real, automated CI run on GitHub's infrastructure (not just a
local test run), confirming the release branch builds and passes on a
clean environment (Python 3.11, Ubuntu).

## 3. Docker Check

Commands run on `final-project`:

docker build -t task-tracker:final .
docker run --rm -d -p 8000:8000 --name tt-final task-tracker:final
curl.exe -s http://localhost:8000/health
docker exec tt-final whoami
docker stop tt-final


Results:
- Build: succeeded, all 16 layers completed.
- Container started successfully, health endpoint responded `200 OK`
  with `{"status":"ok","timestamp":"..."}`.
- `docker exec tt-final whoami` returned `app` — confirmed running as the
  non-root user, not root.
- Container stopped and auto-removed cleanly (`--rm` flag).

## 4. Documentation Checks

Three core documents provide evidence that AI output throughout this
project was reviewed, graded, corrected, or rejected — not accepted
blindly:

- **[`docs/security-review.md`](security-review.md)** — An AI-generated
  security audit (Codex) was independently graded, finding by finding, as
  Valid, False Positive, or Noise. One finding (SEC-05) was a real bug,
  fixed and verified live. One finding (GOV-01) was initially misdiagnosed
  by the AI itself and corrected after direct verification. An independent
  manual scan found a real concurrency issue (YOU-01) the AI's review
  missed entirely.

- **[`docs/ai-usage.md`](ai-usage.md)** — Contains a line-by-line trace of
  an AI-generated function (`update_task`), checking each line's purpose,
  risk, and whether it is genuinely understood, plus three concrete
  personal AI usage rules (never-paste, always-verify, record) each backed
  by a specific incident from this course.

- **[`docs/ai-playbook.md`](ai-playbook.md)** — A one-page personal AI
  coding playbook covering when AI is and is not used, non-negotiable
  rules, review habits, a completed Decision Card naming a specific tool
  for each task shape (new feature, review, debugging, infrastructure),
  and a 30-day re-read commitment.

Together with [`docs/governance-worksheet.md`](governance-worksheet.md)
(risk-classified log of everything shared with AI tools, including the
GitHub Personal Access Token exposure and its remediation) and
[`docs/final-ai-review.md`](final-ai-review.md) (explaining the one
`app/`/`frontend/` change made in this final release round), this
constitutes the full evidence trail for how AI was used, reviewed, and
governed across this project.