# Personal AI Coding Playbook

## 1. When I reach for AI first

- Generating repetitive code, like the pytest suites for checking due dates and the overdue filter, where 16 tests were generated and verified with Break Tests.
- Drafting documentation from the actual project, like README.md and AGENTS.md, that helps a reader understand or run the app. When I rewrote the README in Module 4, drafting the full structure (setup, run, test, Docker, CI sections) from the existing files took minutes instead of the hour or more it would have taken writing it from scratch - but I still had to manually catch two stale claims afterward (the wrong image name, and the "search not implemented" note left over after Feature 2 shipped).
- Exploring options before committing to a decision, like the Dockerfile design alternatives.

## 2. When I don't use AI

- To check if something really works right now. I run curl, pytest, or git status myself. One time, AI said "storage.py doesn't need changes" for the due_date feature. That was wrong. Only testing it by hand showed me the truth.
- To decide my own project's priorities. For example, which two features to build for the midterm, or choosing between "Strategy B" (more complete) and "Strategy C" (more honest).
- For anything about credentials or account security. I create and delete my own GitHub tokens. I never let a chatbot do this for me. This came from actually pasting real GitHub Personal Access Tokens into this chat and my terminal at least twice, to work around an account-flag issue - I only realized the risk during the Module 5 governance review, and had to revoke both tokens afterward.

## 3. My non-negotiable rules

- Never paste real passwords, tokens, or screenshots of my accounts into any AI chat or terminal, even when I'm in a hurry. I learned this lesson the hard way with GitHub tokens.
- Never trust what AI says about my code without checking the real file or running it myself.
- Always keep AI-edited project files (like CLAUDE.md or AGENTS.md) updated and accurate. One time an outdated file caused a real false claim (case GOV-01).

## 4. My rules for reviewing code

- For every issue AI finds, I label it myself: Valid, False Positive, or Noise - before I act on anything. I don't just go down the list in order. This came directly from the Module 5 security review, where one finding (GOV-01) was initially graded as pointing to the wrong file - the AI first blamed my README when the real error was in AGENTS.md. Grading every finding myself, instead of trusting severity labels, is what caught that reversal.
- After I finish reading the AI's review, I always do my own manual check too, especially in places the AI didn't look at. This is exactly how I found a real concurrency bug (YOU-01) that the AI's review completely missed.
- Before I say any AI-written code is "mine," I read it line by line first. I don't take ownership of code I haven't really understood. When I traced update_task line by line for Module 5's ai-usage.md, the trace independently surfaced the same concurrency risk (YOU-01) my separate manual review had already found - proving that actually reading through generated code, not just skimming it, catches real issues.

## 5. What I'm still learning

- When is it worth using structured, pre-summarized context (Strategy B)? It's more complete, but harder to verify.
- How much of my review process should be automatic, and how much should stay manual? I've seen AI reviews find real bugs, but also get things wrong with confidence (like the first version of GOV-01).
- Where's the line between "this is okay for a learning project" (like unstable Docker tags) and "this really needs to be fixed"?

## Decision Card

- For a new feature I reach for: Copilot in VS Code, with a strict prompt naming real files and exact behavior. Both midterm features were built this way - I never needed Cursor's bigger-loop style, because scoped, one-file-at-a-time prompts were easier to review safely.
- For a code review I reach for: Codex, though honestly that was the course's assignment more than my own independent choice. If I needed a real review outside this course, I would probably reason through it in a chat first, then hand the actual "read these files and find problems" job to something like Codex.
- For debugging I reach for: myself first - direct reproduction with curl or pytest, before asking any AI tool anything. The due_date/storage.py bug proved this: I only found it by testing the real behavior, not by asking AI to debug it. AI only helps once I already know what's broken.
- For infrastructure I reach for: Claude Code, specifically because it could actually run commands - build the Docker image, execute git, verify a live container's non-root user. That is different from just generating a Dockerfile as text; I needed real shell access to prove it worked, not just describe it.
- I will never paste GitHub Personal Access Tokens, screenshots of my account settings, my personal email addresses, or real user data into any AI tool. All four of these actually happened in this course, not just theoretical risks.
- My one rule is: verify before you trust. Check the actual file, run the actual command, or reproduce the actual behavior yourself - every time I skipped that step (the storage.py claim, the GOV-01 reversal, the "still implemented on this branch" mixup), the AI's confident answer turned out to be wrong in some specific, checkable way.

## 30-Day Commitment

I will re-read this playbook in 30 days and update it based on what actually happened since - not just what I assumed would happen.
