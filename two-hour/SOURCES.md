# Public sources and reuse

These are supporting resources, not an additional reading assignment. The participant README identifies the short required reading.

## Primary starting point

Neel Nanda, [Astra can do a concerning amount with no chain of thought](https://www.lesswrong.com/posts/eRmzz8J8Qkzqvzrgg/astra-can-do-a-concerning-amount-with-no-chain-of-thought), 2026.

[Published code](https://github.com/neelnanda-io/nocot-bench) includes synthetic task generators and independent solvers. The planned exercise adapts the `brew` color-transition generator to fresh instances and compares elicitation conditions on an open-weight model. It is not a replication of the complete benchmark or its headline score.

Source inspection is pinned to commit `9b8ba4ac4229597b902bc540de6ddf111a4360cc`. The repository's [MIT license and scope statement](https://github.com/neelnanda-io/nocot-bench/blob/9b8ba4ac4229597b902bc540de6ddf111a4360cc/LICENSE) cover its own code and generated tasks, with separate caveats for third-party datasets. Only the original synthetic generators are proposed here. A distributed code subset must retain the license notice.

## Optional direction: filler tokens

Dylan Xu, Sebastian Prasanna, and Alek Westover, [Astra is much better at reasoning with filler tokens than previous models](https://www.lesswrong.com/posts/uvhuZHFtrgk8kNiZc/astra-is-much-better-at-reasoning-with-filler-tokens-than), 2026. [Code](https://github.com/redwoodresearch/astra-filler-tokens), inspected at commit `20d8ef1a8f99f5b138281b76f53e3a7ee957f688`, is MIT-licensed. The prompts and token/parse audits offer useful references; its API runner is not a ready-made local Qwen runner. An effect on its models does not guarantee an effect here.

Jacob Pfau et al., [Let's Think Dot by Dot: Hidden Computation in Transformer Language Models](https://arxiv.org/abs/2404.15758), 2024. [Code](https://github.com/JacobPfau/fillerTokens). The paper motivates the distinction between meaningful text and computation at additional token positions. Its trained synthetic-task models are a different setting from prompting an off-the-shelf instruction model. No explicit repository license was found in the inspected revision `cb39af6458b7476ba07f25e89a9c8fd339c1e229`; this design cites the paper without copying that implementation.

## What has actually been reused so far

The package vendors an unchanged subset of Nanda’s generator source in `vendor/nocot_bench`, with its license. Our wrapper selects four colors, 1–3 transformations, 24 items per level, fresh seeds, and no few-shot demonstrations. It replaces the upstream no-reasoning instruction with condition-specific instructions and adds optional table formatting. These are adaptations of the task, not the original benchmark protocol.

`starter.py` supplies local Qwen inference, exact grading, raw-output inspection, and paired analysis. The baseline configuration pins the model revision. The cached baseline includes raw outputs, metadata, and the exact runner source. Generator, grading, formatting, and actual GPU runs have been checked; the first participant timing trial led to the current two-hour revision, whose pacing still needs a fresh trial.
