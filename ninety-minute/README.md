# Does showing the working help?

**A two-hour empirical AI safety exercise**

> **Pilot version.** The first participant attempt suggested that 90 minutes was overscoped. We have allowed two hours and clarified the instructions, while keeping the same two questions. We are still calibrating the workload; complete the short [pilot feedback](PILOT_FEEDBACK.md) afterward.

Language models can sometimes solve problems without displaying intermediate reasoning. Understanding when visible reasoning helps is relevant to proposals for monitoring a model's chain of thought. Investigate one small part of that question using an open-weight model.

You have **120 minutes**, including reading, experiments, slides, and recording. Aim for a defensible finding and a useful explanation. There is no expected direction of result.

## Before starting

Complete [SETUP.md](SETUP.md): install dependencies, download the model, run the smoke test, check AI-log export, and test your microphone/screen recorder. These preparations are outside the clock. Reading the research material and investigating the questions are inside it.

**You need GPU access for a new experiment:** one H100, or a comparable GPU with a successful smoke test. You can rent one through [Vast.ai](https://vast.ai/pricing), or **message Nabil for an API key and GPU setup instructions**. Allow for setup/download time as well as the exercise. No training is required.

## Understand the task

The starter uses Qwen3-8B and fresh problems with exact answers. Each problem describes **one potion** and a table of color changes when ingredients are added. Apply the ingredients sequentially to that same potion.

For example, suppose adding mint to red makes blue, and adding salt to blue makes green. A potion starting red with the sequence **mint, then salt** follows **red → blue → green**. The answer is green, and the difficulty is **two transformations**. Each step uses the current color, not the initial color.

Compare a condition that permits visible reasoning with one that requests a direct answer, using the same model and matched problems. Inspect what each condition actually produces. The package supplies a runner, grader, editable configurations, task generator, and cached baseline. You may use the cache **after recording Q1A**; disclose that reuse. Q2 should include a new experiment.

The baseline has four colors and one to three transformations. The supplied generator avoids repeated colors within a solution path, so `levels` must be smaller than the color count: deeper problems require more colors too. Changing both changes more than just sequence length. Transformation count is a task property, not a measurement of internal model reasoning.

## Reading: five to ten minutes

Use Neel Nanda's [Astra can do a concerning amount with no chain of thought](https://www.lesswrong.com/posts/eRmzz8J8Qkzqvzrgg/astra-can-do-a-concerning-amount-with-no-chain-of-thought). Find these headings on the page:

| Section | Read | Skip |
| --- | --- | --- |
| Measuring No CoT Reasoning | Opening task description and final paragraph on verifying that outputs contain no CoT | Benchmark aggregation, index fitting, and model-specific elicitation details |
| Quantifying Serial depth | Opening explanation of dependent steps, through the first accuracy-versus-steps figure | Subsequent fitted-index comparisons and factual-recall analysis |
| Appendix: No-CoT Reasoning vs Controllability | First two paragraphs distinguishing the concepts | The subsequent model-comparison study |

Skip the rest of the post, linked papers, and comments. [SOURCES.md](SOURCES.md) is optional reference material. We are testing the supplied open-model setting; do not assume the frontier-model result transfers.

## Questions

Record each **A answer before running or viewing its B results**, using [PREDICTIONS.md](PREDICTIONS.md). Spend roughly five minutes per prediction; a few bullets, usually **100–150 words or fewer per question**, are enough. This is guidance, not a minimum or a strict word limit. Preserve the original wording when your view changes.

### Q1 — What difference does visible reasoning make?

**A.** Predict how the same model will perform when **visible reasoning is permitted** versus when **a direct answer without visible working is requested**, including dependence on difficulty. Explain your reasoning and uncertainty.

**B.** Investigate the comparison. What pattern do you find, and how confident should we be in it? Inspect examples as well as aggregate results. Check whether grading reflects the responses and whether responses follow the condition instructions; explain any issue that materially affects your conclusion. **There is no required hidden bug to find.** A brief, justified check is enough if the measurement looks sound.

### Q2 — What explains your result?

**A.** Choose an explanation for an important Q1 result and identify a plausible alternative. Propose **one tractable follow-up** that could help distinguish them. Say what you will change, what you will hold fixed, and what outcomes would favor each explanation. Record your prediction before running it.

**B.** Run the experiment and update your explanation. What does the evidence support, what remains unresolved, and how—if at all—does it change your view of using visible reasoning for oversight?

One well-chosen follow-up is enough; you do not need an exhaustive sweep or a definitive mechanism. Choose your own intervention, controls, and analysis. A failed or inconclusive experiment can support a strong answer if you diagnose it carefully and limit your claims. You may modify the setup or introduce a different task if the comparison is justified and feasible within the time limit.

## Presentation and submission

Send **one small ZIP and an unlisted YouTube link**. No separate written report is required.

Record a **1–2 minute screen recording with your spoken explanation**, using the [two-slide template](slides_template/README.md) and **one or two graphs total**. Use one slide per question: prediction, finding, and update. About three short bullets or **40–70 words per slide**, alongside the figure, is plenty; no minimum or script is required. Explain your key uncertainty and Q2's implications for oversight in your own words. One graph may cover both questions.

Clear audio and readable graphs are enough. A webcam is optional; production polish and flawless delivery are not assessed. Upload as **Unlisted**, check playback while signed out, and send the URL with the ZIP. Also put it in `AI_LOGS.md`. [YouTube visibility instructions](https://support.google.com/youtube/answer/157177?co=GENIE.Platform%3DDesktop&hl=en).

Use this file map for the ZIP; **write each piece once**:

| File or folder | Include |
| --- | --- |
| `PREDICTIONS.md` | Original Q1A and Q2A, with timestamps |
| `PILOT_FEEDBACK.md` | Actual timing, unfinished work, and brief feedback; fill in after stopping |
| `AI_LOGS.md` and `ai_logs/` | Recording URL, file index, and complete task-related AI-assistance exports; see [AI_LOGGING.md](AI_LOGGING.md) |
| Reproduction code and configurations | Scripts/notebooks, dependency versions, seeds, and brief commands to reproduce experiments and graphs |
| `runs/` and `analysis/` | Small raw outputs from fresh research runs, adjacent metadata/source snapshots, summaries, and plotted figures |
| `slides_template/` | The slides and linked images already used for your recording |

Identify reused supplied results by filename and SHA-256 from `MANIFEST.json`; you need not bundle the supplied baseline again. Include fresh experimental results so claims can be checked without rerunning GPU inference. Exclude model weights, model/download caches, virtual environments, dependency folders, bulky downloaded assets, and the video file. If a necessary result is too large to bundle, state the omission and how to retrieve or reproduce it. Check the archive before sending.

AI assistance is allowed for coding, discussion, and analysis. Preserve complete task-related conversations and available tool traces, including branches/subagents; the organizer will review them, including with AI agents, to understand the workflow and improve the exercise. If you use no AI assistance, say so in `AI_LOGS.md`.

## Scoring rubric

| Category | Weight |
| --- | --- |
| Communication | 20% |
| Research answers | 70% — 35% each for Q1 and Q2 |
| Steering and judgment | 10% |

**Communication:** Explain comparisons and evidence clearly and faithfully, in your own words. Graphs need legible labels, sample sizes, and appropriate uncertainty estimates. Claims should be traceable to the submitted evidence. Appearance and editing are not graded.

**Research answers:** Present each question's prediction, finding, and update in the slides/recording. Only answers presented there receive research-answer credit; extra results in the ZIP support verification. We assess:

- Justified predictions recorded before seeing results, regardless of whether they prove right.
- Correct experiments and analysis, including relevant measurement checks and confounders.
- Informative tests of explanations: causal claims need suitable interventions, not just correlations.
- Interpretation and belief updates, with confidence and scope that match the evidence.

**Steering and judgment:** Choose informative directions, allocate time sensibly, and check your work and AI assistance. Elaborate agent orchestration is unnecessary. Honest confusion and basic questions are welcome; logs are not used to penalize asking for help. Without AI assistance, your experimental choices and reasoning provide the evidence.

## Suggested pacing

| Minutes | Activity |
| --- | --- |
| 0–20 | Read, understand the task, and record Q1A |
| 20–45 | Run or inspect the baseline and answer Q1B |
| 45–85 | Record Q2A, run one focused follow-up, and interpret it |
| 85–105 | Select graphs and complete the two slides |
| 105–120 | Record 1–2 minutes and check audio/legibility |

Use minutes 20, 45, and 85 as checkpoints. If behind, narrow the investigation and state what remains unresolved. **Protect the final 35 minutes for communicating the work.**

Stop research and presentation work at **120 minutes**. Record actual start/finish times, elapsed time, interruptions, and any overrun in the feedback form. Installation, download, logging setup, and recording checks happen before the clock. Exporting logs, packaging/transferring the ZIP, uploading/sharing the video, and completing feedback may happen afterward; report that administrative time separately. Do not continue research or revise the presentation after the timer.
