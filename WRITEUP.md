# Write-up: AI Proposal Triage (MATACS-TH-2026-02)

Diagram: `diagram/process-flow.png`. Prompts: `PROMPTS.md`. Expected ranking: `ranking.json`.

## Design in short
Upload -> PDF to text -> safety scan -> **AI extracts facts with quotes** -> code validates, checks mandatory
criteria and scores -> ranked list with reasons -> **person reviews and decides**.

## 1. AI vs. rules
**AI (one step only):** reading messy proposal text and turning it into structured facts (price, weeks,
install count, warranty years, licence statement, team items), each with a quote. Proposals are free text
written in different styles, so this is where AI adds real value.

**Plain code or rules:** loading the criteria, the safety scan, validating the AI output, pass/fail mandatory
checks, scoring, sorting, building the reason text, logging.

**Why the line is here:** extraction needs language understanding; scoring needs to be exact, identical every
time and easy to defend in front of a bidder. Arithmetic on weights is something code does better than AI.
The AI also never sees the weights, so it cannot lean towards a result.

**Scoring rules (per category, from the admin's weights):**
- Experience 30: installs of 100 kW+ divided by the highest count among eligible bids.
- Price 25: lowest eligible price divided by this price (must be within the ceiling).
- Timeline 15: fastest stated weeks divided by this bid's weeks (must be 16 or less).
- Warranty 15: half panel years (capped at 25), half workmanship years relative to the best.
- Team 15: four items (named lead, crew stated, safety plan, monitoring plan), equal share each.

## 2. Consistency and explainability
- AI runs at temperature 0, with a pinned model version and a strict JSON schema; the extraction is saved,
  so a re-run uses the saved facts unless someone deliberately re-extracts.
- Scoring is code on those saved facts, so the same facts always give the same score.
- **Would two runs give the same result?** The scoring and ranking: yes, always. The extraction: almost
  always, but not guaranteed, because language models can vary slightly. That is why every fact needs a
  quote, code checks the quote exists in the source text, and the extraction is stored and reused.
- **Why a proposal ranked where it did:** the reviewer sees a score breakdown per criterion, the extracted
  value, and the exact quote from the proposal, next to a link to the page of the original PDF.
- Known weak point: best-in-set formulas make a score depend on the other bids; the set is logged.

## 3. Human in the loop
- **Flags to resolve:** missing or unclear data, safety-scan hits, quotes not found, unreadable files. These are
  never auto-ranked.
- **Override:** the reviewer can change any extracted value (with the quote beside it) or move a proposal, but
  must type a reason. Code recalculates, so the change is visible in the score.
- **Ineligible bids** are listed with the failing check so a person can question them.
- **Final award is always a person's decision**; the tool only recommends an order.
- **Audit log:** criteria version, file hashes, prompt version, model and settings, raw AI output, validation
  results, scores, flags, every override (who, when, old value, new value, reason), and the final decision.

## 4. Changing criteria
Criteria are saved as numbered versions. Every scoring run records the version it used.
- Old results are **never silently changed**; they stay tied to their version and are labelled "scored under v2".
- When the admin saves v3, the system shows which categories have scored proposals and offers **"Re-score"**.
  Saved facts make re-scoring code-only, unless a criterion needs a new fact (then only that extraction re-runs).
- Re-scored rankings are shown side by side with the old one, and any change needs reviewer confirmation.
- If the award decision is already made, the criteria version is locked for that project.

## 5. Risks
| Risk | Safeguard |
|---|---|
| **Wrong extraction** (misread a number or date) | Every fact needs a quote; code checks the quote is in the text and numbers are consistent; reviewer sees quotes next to values; failure -> flag. |
| **Made-up facts** | Prompt allows only stated facts and `null` when unsure; "to be confirmed" counts as not stated. |
| **Manipulation / prompt injection** (text telling the AI to rank a bid first) | Proposal text is treated as data; safety scan plus an AI field for embedded instructions; the AI never produces scores; flagged for human review. |
| **Bias** (big firms, writing style) | Scores use only the admin's measurable criteria, never company name or writing quality; vague wording is flagged, not rewarded. |
| **Cost** | One AI call per proposal; scoring is free; extraction is cached; re-scoring does not call AI. |
| **Over-trust in the ranking** | Final decision stays with a person; flags and ineligible bids stay visible. |

## Sample set (how the design ranks A-E)
- **A ranked 1 (98.0)** and **E ranked 2 (84.8)**: full eligibility; A leads on experience, schedule and team.
- **B ineligible:** electrical work is subcontracted and the licence holder is "to be confirmed", so the
  mandatory licence check fails despite the lowest price.
- **C flagged:** it passes the mandatory checks (merit score about 77, third if cleared), but its text tries to
  force rank 1; that instruction is ignored, and a person decides.
- **D flagged:** no completion time, so the 16-week limit cannot be verified; ask the bidder to clarify
  (about 70 if the timeline were scored 0, up to about 85 if it matched the fastest bid).

## Assumptions
- "Since 2021" and "last 5 years" were treated as within the window; C's "since 2020" may partly be outside it,
  which a reviewer should check.
- "Named lead" means the proposal says a named lead exists. Formulas are my choices for the exercise.
