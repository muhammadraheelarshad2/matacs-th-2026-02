# MATACS-TH-2026-02: AI Proposal Triage Design

- **Name:** Muhammad Rahil Arshad
- **Reference:** MATACS-TH-2026-02
- **Role:** Associate Software Developer
- **Time actually spent:** almost 1 hour

## Files
- [WRITEUP.md](WRITEUP.md): answers to the five questions (under 1,000 words)
- [diagram/process-flow.png](diagram/process-flow.png): flow from upload to ranked output (AI, rule and human steps)
- [PROMPTS.md](PROMPTS.md): the extraction prompt, retry prompt and optional reason prompt
- [ranking.json](ranking.json): expected ranking of proposals A-E
- [prototype/score.py](prototype/score.py): optional script for the scoring step (plain code, no AI, no API key needed)
- [prototype/sample_extractions.json](prototype/sample_extractions.json): numbers and yes/no facts per proposal letter, no proposal text

Run the optional script with `python prototype/score.py` (Python 3, no packages needed).

## How I used AI tools
I used Claude to help draft the process design, the extraction prompt, the scoring formulas and the write-up, and I reviewed the result before submitting.

**Where I disagreed with or corrected the AI:** Claude only mentioned C's "since 2020" install count in the assumptions section of the write-up. I decided it should also appear in C's flag reason in `ranking.json`, because the reviewer sees that file first and installs older than 5 years should not count towards experience.

## Notes
- Proposals are referred to by letter only; no brief or proposal text is copied here.
- No API keys are used or stored, so no `.env.example` is needed.
