# Antigravity Prompt Pack

Use these files in order:

1. `00-project-brief.md`
2. `01-main-build-prompt.txt`
3. `02-fix-and-complete-prompt.txt`
4. `03-polish-and-demo-prompt.txt`
5. `04-testing-suite-prompt.txt`

Recommended workflow:

1. Paste the project brief if you want Antigravity to understand the product idea first.
2. Paste `01-main-build-prompt.txt` to generate the MVP codebase.
3. Paste `02-fix-and-complete-prompt.txt` right after generation to make it runnable.
4. Paste `03-polish-and-demo-prompt.txt` to improve the UI, tests, and presentation quality.
5. Paste `04-testing-suite-prompt.txt` at the very end so Antigravity creates or completes the testing suite after the build is already stable.

Why multiple prompts instead of one:

- The project has backend, frontend, persistence, extraction, reconciliation, validation, and tests.
- One giant prompt usually creates a decent draft but often leaves runtime issues.
- The second and third prompts push Antigravity to verify and finish the project properly.
- The final testing prompt turns the project into a checked deliverable instead of an unverified code dump.

Expected outcome:

- A runnable MVP for "Memora: A Persistent and Reconcilable Memory System for LLM Agents"
- FastAPI backend
- Streamlit demo UI
- SQLite persistence
- Memory states, conflict handling, and audit trail
- Tests and documentation
