# 11 Conclusion

Two to three sentences, no new information, at most half a page.

## Template

> We presented <framework/construction> in which <structural statement>, so that
> <prior works> become special cases of <one cost formula / one family>.
> More importantly, <structure> yields <new construction> for <coverage>, and
> <algorithm> accelerates <stage> by <range> over <strongest baseline>.
> [Optional] <One or two open problems / invitation for third-party analysis.>

## Rules

- Same numbers, scope and wording as the abstract. No claim that the abstract lacks.
- System papers: name the regime (proven or conjectured soundness) of the headline
  numbers again, and publish the benchmark scripts.
- Theory papers: one or two precise open problems are welcome.
- If pages are tight, the optional third sentence is the first thing to go; the
  conclusion must still end on the last allowed body page.
- Do not "summarise the sections" ("In Section 3 we ...").

## Toy (T2, illustrative)

> We showed that interleaving the low-degree extension with Merkle hashing lets an
> FRI-based prover commit to a trace with peak memory O(√n) columns, without changing
> the proof. On zkVM traces of 2^{22}–2^{26} rows at 100-bit proven soundness, proving
> is 1.4–1.9× faster [illustrative] than the strongest streaming baseline on the same
> GPU. Extending the schedule to multilinear commitments is left open.
