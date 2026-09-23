# Collecting AI-assistance logs

AI assistance is allowed. Submit **all task-related AI logs**, so the organizer can review the workflow, including with AI agents. A usage summary is helpful but does not replace the underlying logs.

## Before starting

Use fresh conversations/sessions for this exercise and check that you can preserve their histories. Enable tool/session logging where your assistant supports it. Include assistance used during setup, the timed exercise, and submission preparation; identify those phases in the index.

## What to include

- Every relevant conversation with a coding assistant or chat model, including planning, debugging, experiment design, analysis, and presentation preparation.
- All sessions, continuation threads, branches, and subagent transcripts used for the task. Keep unsuccessful attempts and corrections as well as the final approach.
- User prompts, assistant responses, tool calls and tool outputs as exposed by the tool's history/export. Preserve timestamps, message order, session IDs, and model/tool identifiers where available.
- Task-related files or attachments needed to understand those conversations, or relative paths to them elsewhere in the submission.
- Record the research-model version, seeds, prompts/settings, and reproduction commands in your code/configuration. List the experiment-output paths in the log document so conversations remain understandable. Include the small raw outputs, metadata, and source snapshots from fresh research runs, alongside summaries and plot-reproduction code. The supplied baseline may be referenced by filename and SHA-256 instead of bundled again.

Prefer original **JSON/JSONL exports**. If unavailable, use a complete Markdown, text, or HTML transcript. Screenshots and conversation links can supplement an export, but include local files that the organizer can read later. Do not replace transcripts with AI-generated summaries or select only successful exchanges.

## Organizing the files

You can ask your agent to collect the logs and put them in your submission ZIP. For example:

> Collect all AI-assistance logs for this exercise, including available conversation histories, tool traces, branches, and subagent transcripts. Complete `AI_LOGS.md` with the full transcripts or an index to bundled native exports under `ai_logs/`, and include them with my reproduction code, original `PREDICTIONS.md`, completed `PILOT_FEEDBACK.md`, fresh raw experiment outputs and metadata/source snapshots, analysis, and slides in a small submission ZIP. Exclude model weights, model/download caches, environments, bulky datasets, and the recording. Preserve the original exports, remove credentials and unrelated material with labeled redactions, and tell me about any sessions or content you cannot access so I can add them myself.

An agent may only have access to its own tool or local sessions. Check that exports from any other AI tools you used are included as well.

Complete [AI_LOGS.md](AI_LOGS.md). It indexes the submission and AI logs. Keep original predictions and timing/feedback in their separate files; reference them without copying their contents. You can paste complete text transcripts into that file or put native JSON/JSONL exports in `ai_logs/` and reference them from it. Use distinct filenames per session. Include everything in the same small submission ZIP; a summary or link to an external chat alone does not replace the logs.

Keep full task-relevant content and ordering. Remove credentials and unrelated personal or third-party material before submitting; mark each removal, for example `[REDACTED: API key]`, and describe its scope in the index. Export task-specific sessions rather than an entire account history.

If a tool cannot export some content, submit everything available and state exactly what is missing and why. Do not reconstruct absent transcripts and present them as original logs. If you used no AI assistance, write that explicitly in the index. The reproduction code/configuration remains required.

## At the time limit

Stop the research and presentation work at 120 minutes. Log export, YouTube upload/link sharing, and file transfer may happen afterward as administrative work; record that time separately in the feedback form. Do not start new substantive AI-assisted work after the timer.
