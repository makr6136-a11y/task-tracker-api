# Course Reflection

Across this whole course, the tool that fit best really did depend on the shape of the task, not on which one felt most impressive.

For building new features (due dates/overdue filter, search), Copilot in VS Code worked well because I could give it a small, strict, file-referencing prompt and review the diff before applying it - good for focused, incremental changes to code I already understood.

For infrastructure work (Dockerfile, CI, the red/green pipeline proof), Claude Code was the right fit specifically because it could actually run things - build the image, execute git, verify a live container - not just describe them in text.

For security review, governance retrospectives, and architecture/context-strategy experiments, Codex fit best, mainly because those tasks needed something to read across many files and produce a structured, citable output, not just generate code.

For reasoning through decisions, drafting documentation, and reflecting on what actually happened (like this reflection itself), a general chat without direct repo access was enough, and honestly clearer, since it forced me to explain things in my own words instead of letting a tool that could touch files also make the call.

If I had to pick one rule that mattered more than any other across the entire course, it is this: verify before you trust. Every real problem I hit - the due_date field silently not saving, the AGENTS.md file confidently claiming a feature existed when it did not, the GOV-01 finding blaming the wrong file - was only caught because I checked the actual file, ran the actual command, or reproduced the actual behavior myself, instead of accepting a plausible-sounding claim as fact.
