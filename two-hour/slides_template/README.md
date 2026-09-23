# Two slides for a 1–2 minute video

The template uses the same local Markdown-to-HTML workflow and plain 16:9 theme as the reference take-home. It contains fresh blank prompts, with no reference questions, answers, or figures. It works offline and needs no slide software or additional Python packages.

1. Put your one or two graph images in `figures/`.
2. Edit `slides.md`. Keep the two slides, one for Q1 and one for Q2. Replace the graph placeholder with an image tag as shown in the file. Use short notes that support your spoken explanation: about three short bullets or 40–70 words per slide is plenty, with no minimum or strict word limit.
3. From this folder, run `python build.py`, then open `slides.html` in a browser. Refresh after rebuilding. Arrow keys change slides, and `f` toggles fullscreen.
4. Record your screen and voice for **1–2 minutes**. Play it back once to check audio and readable graph labels, then upload it to YouTube as Unlisted and check that anyone with the link can watch. Send the unlisted video URL alongside the ZIP; [submission details](../README.md).

For roughly the first half, explain Q1's prediction, the comparison, the result, and your update. For the second half, do the same for Q2, including why you chose that follow-up, the most important limitation, and any implication for oversight. Use your own words. Brief bullet notes are fine; there is no need to write a script or edit the recording.

The prediction line on each slide should summarize what you actually recorded before the experiment. Keep your original `PREDICTIONS.md` entries unchanged. Keep graph axes, conditions, and sample sizes legible, and show uncertainty where it affects interpretation. One graph may cover both questions; the other slide can then use a small table or short explanation.

Bundle the slides and their linked images in the same ZIP as your reproduction code, results, and logs; no separate report or slide upload is required. Send the unlisted YouTube link alongside it and leave the video file out of the ZIP.

## Template/runtime attribution

The theme and build workflow adapt the supplied reference template; all assessment content has been replaced. The embedded slide renderer identifies itself as remark 0.14.1. Its upstream MIT notice is included in `REMARK_LICENSE.txt`; see [remark](https://github.com/gnab/remark). We preserved the existing embedded runtime rather than introducing a hosted dependency.
