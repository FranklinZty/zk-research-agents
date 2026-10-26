# 01 Title

The title is the first positioning statement. Decide it together with the abstract's
second paragraph: both must name the same object.

## Patterns that work

| pattern | shape | toy example (invented) |
|---|---|---|
| Object + effect | "<Object>: <effect> for <setting>" | "ToyLookup: Lookup Arguments with Table-Independent Prover Cost" |
| Framework + scope | "A <unified/graded> view of <problem>" | "A Unified View of Logarithmic-Derivative Lookups and Grand Products" |
| Result as claim | "<Setting> with <quantity> <comparative>" | "FRI Proving with Memory Sublinear in the Trace Length" |
| System name + mechanism | "<System>: <mechanism> for <workload>" | "ToyProver: Streaming Trace Commitment for Memory-Bounded STARK Proving" |
| "and Beyond" suffix | scope extender when a section generalises the core technique to neighbouring schemes | "... for Plonkish Arithmetization and Beyond" |

## Rules

1. **Name the structural idea, not the parameter.** A title about "folding factor 16"
   or "a 2^16 table" reads as a parameter tweak; a title about the mechanism
   (packing, grading, batching) reads as a method.
2. **Fit on two lines in the class's title font.** If one word spills onto its own
   line, rephrase (e.g. move a qualifier into a subtitle) rather than shrink fonts.
3. **If the paper unifies prior lines of work, say "unified"/"framework" in the title
   only if the body proves at least one statement that specialises to each prior
   work.** Otherwise the word will be attacked.
4. **Avoid:** "novel", "efficient" as the only adjective, "towards", question titles
   for non-survey work, acronyms not known to a general cryptographer, and titles
   longer than ~15 words.
5. A suffix such as "and Beyond" is justified only by an actual section applying the
   technique beyond the main setting (see `05_technique_overview.md`, "scope
   extender" note). It can raise perceived significance at low page cost.

## Process

Produce 5–8 candidates in `paper/TITLES.md`, each with a one-line rationale and the
risk a reviewer might see. Discuss with the human author; they choose.

## Bad → better (toy)

- Bad: "On the Efficient Design of a Novel Post-Quantum Lookup Argument for
  Zero-Knowledge Succinct Non-Interactive Arguments of Knowledge over Plonkish
  Arithmetizations" (long, "novel", "efficient", "post-quantum" unsupported, no claim).
- Better: "ToyLookup: Lookup Arguments with Table-Independent Prover Cost".
- Watch the words "SNARK", "zkSNARK", "post-quantum", "transparent": each is a
  claim (succinctness, ZK, the assumption, the setup) the body must prove.
