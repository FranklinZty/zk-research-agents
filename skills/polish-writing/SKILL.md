---
name: polish-writing
description: Use for a final language pass on a paper section, or when translating a Chinese draft into English academic prose. Removes AI-sounding phrasing, tightens sentences, enforces consistent notation and terminology, and never changes numbers, claims or LaTeX semantics.
---

# Polish writing

## Invariants (never violate)

- Do not change numbers, theorem statements, hypotheses, citations, labels or math.
- Do not strengthen claims ("shows" → "proves", "up to" → "always").
- Keep LaTeX commands intact; do not introduce packages.
- In the last 24 hours before a deadline: no style passes at all, only error fixes.
- Output: revised text + a short modification log (what and why) so the author can
  accept/reject each change.
- **ZK term-protection list.** The pairs below name different technical notions. Never
  merge, swap or "unify" them for consistency, and never shorten one into the other:

  | do not interchange | why |
  |---|---|
  | proof ↔ argument | statistical vs computational soundness |
  | zero-knowledge ↔ honest-verifier ZK | malicious vs honest verifier |
  | soundness ↔ knowledge soundness | existence vs extraction of a witness |
  | SNARK ↔ zkSNARK ↔ SNARG | knowledge and/or ZK may not be claimed |
  | succinct ↔ short | succinct also bounds verifier time |
  | transparent ↔ universal setup | no trusted setup vs one reusable trusted setup |
  | proven ↔ conjectured (soundness, proximity) | theorem vs conjecture regime |
  | statistical ↔ computational ZK | different simulator guarantees |

  Any edit that touches a word from this list (including deleting a qualifier such as
  "honest-verifier" or "conjectured") is logged with the tag
  `needs author confirmation` and is not applied silently. Swapping "argument" for
  "proof", or dropping "honest-verifier", strengthens the claim and is covered by the
  previous invariant as well.

## Pass 1 — de-AI

Replace or delete:

| avoid | prefer |
|---|---|
| leverage, utilize | use |
| delve into, explore (as a result) | examine, study (or state the result) |
| pivotal, crucial, paramount | important, key (or delete) |
| underscore, highlight (as filler) | show |
| tapestry, landscape, realm | (delete; name the area) |
| seamless(ly), robust (without a metric) | (delete or quantify) |
| "It is worth noting that", "Notably," | (delete; state the fact) |
| "In this paper, we aim to" | "We ..." |
| "First and foremost", "Last but not least" | (delete) |
| "plays a crucial role in" | "determines", "dominates" (be specific) |
| "novel" about own work | (delete; let the reader judge) |
| "significantly" without numbers | the number |
| "obviously", "it is easy to see" | give the one-line reason, or delete |

Also: convert `itemize` inside running text into connected prose when the items are
reasoning steps (keep lists for contributions/parameters); avoid three connectives
in a row; vary sentence openings; no rhetorical questions in the body.

## Pass 2 — concision

- One idea per sentence; aim for ≤ 30 words.
- Remove throat-clearing openers and doubled phrases ("in order to" → "to",
  "the fact that" → "that", "a number of" → "several"/the number).
- Prefer verbs over nominalisations ("perform an evaluation of" → "evaluate").
- Active voice for what *we* did; passive is fine for standard facts.
- Avoid dashes as sentence punctuation (use commas, colons, or split sentences).

## Pass 3 — consistency

- Terminology: one name per concept (framework name, stage names, baseline names).
  Build a term list from the notation table and `grep` for variants
  (e.g. "lookup"/"lookup argument", "sumcheck"/"sum-check", "PCS"/"polynomial
  commitment"). Do not resolve variants that hit the ZK term-protection list; log
  them for the author instead.
- Notation: symbols match the notation table; no symbol reused with two meanings;
  vectors/matrices consistently bold or not.
- Spelling variety: pick US or UK and stay with it.
- Capitalisation of references: `Section~\ref`, `Table~\ref`, or `\Cref` consistently;
  non-breaking spaces before `\cite` and `\ref`.
- Numbers: consistent units and precision (e.g. 2 significant digits for ratios);
  `\times` spacing consistent; thin space before units.

## Pass 4 — Chinese → English (for drafts written in Chinese)

1. Translate meaning, not word order: Chinese topic-comment sentences often become
   English subject-verb sentences with the conclusion first.
2. Split long Chinese sentences joined by commas (一逗到底) into several English
   sentences.
3. Watch for common calques: "has important significance" → "matters because ...";
   "realize/achieve an algorithm" → "implement"; "the proposed scheme" repeated →
   name it once, then "our scheme"/its name; "in recent years" as an opener → delete or
   give the year range; "greatly improve" → the number.
4. Articles: every singular countable noun needs a/the; "the" for things already
   introduced or unique ("the sum-check protocol of [X]").
5. Tense: present for facts and what the paper does; past for what prior work did
   or for experiments that were run.
6. Produce three parts: `[LaTeX]` English text, `[Back-translation]` literal Chinese
   of the English (so the author can check meaning), `[Log]` list of changes.
   Translation choices between protected terms (e.g. 证明 → "proof" or "argument",
   零知识 → "zero-knowledge" or "honest-verifier zero-knowledge") are always logged
   as `needs author confirmation`.

## Pass 5 — read-aloud check

Read the abstract and the first page aloud (or via TTS). Any sentence that needs a
second breath gets split.
