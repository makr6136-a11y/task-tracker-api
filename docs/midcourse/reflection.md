# Reflection - Mid-Course Project

## What went well

Both features were built using the same disciplined loop: write a strict, scoped prompt referencing real files, review the generated code line by line, verify manually with curl before trusting it, write automated tests, and prove those tests were meaningful with a deliberate Break Test. This caught two genuine bugs before they became invisible problems: a silent due_date field drop in storage.add_task() (caused by an explicit field list that simply never got updated), and a copy/paste artifact that briefly looked like a missing test assertion but wasn't. Neither would have been caught by "it looks right" - both needed actual execution and verification.

## What I corrected

The biggest recurring source of false leads throughout this project wasn't the AI-generated logic - it was environment noise. Several times, a test or a curl check appeared to fail ([] instead of expected results) not because of a real bug, but because the in-memory storage had reset after an unrelated server restart. Learning to distinguish "the code is wrong" from "the server just restarted and wiped memory" became a real, repeated diagnostic skill over the course of this project, not a one-time lesson.

I also had to actively reject a mismatched prompt at least twice - reusing an old Module 1/2 "generate everything from scratch" prompt would have risked overwriting working code, when what I actually needed was a small, scoped addition to existing files. Recognizing that distinction (generate vs. extend) before running a prompt, rather than after seeing bad output, saved real rework.

## What I would do differently

I would set up the CI pipeline to build/verify the Dockerfile from the start rather than relying entirely on manual docker build checks - this came up explicitly in a separate technical decision note, and it is a pattern worth applying earlier next time: automate the check as soon as the artifact exists, not after.

I would also keep branches more strictly separated by scope. At one point I merged unrelated Module 4 coursework (Docker, CI) into the midterm branch out of habit, when the midterm brief never asked for it - not harmful, but unnecessary noise in a branch that is supposed to represent a focused, gradeable deliverable.

## Assumption corrected per feature

Feature 1 (Due Dates): The AI assumed, without being told, that a same-status "transition" should be silently allowed once frontend integration surfaced an edge case (editing a task without touching its status still resent the current status value). The correct fix was in the frontend - only send status when it actually changed - not in weakening the backend's transition validation, which had already been correctly built and tested. Restoring the backend rule and fixing the actual root cause preserved both correctness and existing test coverage.

Feature 2 (Search): No incorrect assumption from the AI itself, but I had to correct my own initial framing of an "AI inaccuracy" - an early candidate for one of the assumption corrections was based on a garbled copy/paste of AI's own output, not something the AI actually got wrong. Verifying directly against the source before concluding something was a mistake mattered here too.
