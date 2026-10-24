# Toy abstracts — good vs bad

All three papers are **invented**. Every number is **illustrative only** and marked
`[ill.]`; none comes from a real measurement. Citations like [A23] are placeholders,
and system names such as ToyLookup, ToyProver or ToyFRI-SNARK do not exist.

---

## T1 — A lookup argument with table-independent prover cost (protocol / theory)

### Bad

> Zero-knowledge proofs are a very important and novel technology. In this paper we
> propose a novel and efficient lookup argument. Our scheme is secure and
> post-quantum. We implemented it and it is significantly faster than previous
> methods, up to 9.1× [ill.]. Code is available at
> https://github.com/<real-username>/toylookup.

What is wrong: no bottleneck, no prior routes, no open question; "novel",
"significantly" without scope; "secure" names neither soundness notion nor model;
"post-quantum" without the assumption (and the toy scheme uses a pairing-based PCS);
the ratio has no baseline, no security level, no machine; the link de-anonymises the
submission.

### Good

> Lookup arguments let a prover show that every entry of a committed vector lies in a
> public table, and they dominate the cost of range checks and non-native arithmetic
> in Plonkish circuits. Existing arguments either pay prover work linear in the table
> size [A23] (CRYPTO'23) or require a circuit-specific preprocessing of the table
> [B24] (EUROCRYPT'24). Whether a lookup argument can have prover work independent of
> the table size without per-table preprocessing has remained open.
>
> We present ToyLookup, which views a lookup as a sum-check over the logarithmic
> derivative of the looked-up multiset. We show that the prover only commits to
> values proportional to the number of lookups m, and that the table enters solely
> through one evaluation that the verifier computes in O(log N) time for structured
> tables. The lookup of [A23] is the case k = 1 of our construction. We prove
> knowledge soundness in the algebraic group model and the ROM, with a universal
> setup.
>
> For m = 2^{20} [ill.] lookups into a table of size N = 2^{32} [ill.], at 128-bit
> soundness (proven) the prover is 2.1–3.4× [ill.] faster than [A23] on the same
> machine, and proofs grow by 0.6 kB [ill.]. Our implementation is publicly
> available.\footnote{anonymous link}

---

## T2 — Memory-bounded FRI prover (system / implementation)

### Bad

> We build a fast STARK prover. It uses GPUs and is the fastest prover. It is
> post-quantum and has 128-bit security.

Wrong: no workload; "fastest" without comparison; "128-bit security" does not say
whether soundness is proven or conjectured; "post-quantum" without the assumption;
nothing about what the timing includes (witness generation? trace commitment?).

### Good

> FRI-based provers are bottlenecked by memory traffic during trace commitment: for
> traces beyond device memory, existing GPU provers fall back to the CPU [C22] or
> stream the trace several times [D23]. Whether the low-degree extension can be
> committed in a single streaming pass with bounded memory has remained open.
>
> We present ToyProver, which reorders the NTT and Merkle-hashing passes so that each
> column of the extended trace is hashed as soon as it is produced. We show that the
> peak memory is O(√n) columns [ill.] instead of O(n), with no change to the proof.
> The setup is transparent and soundness relies only on collision-resistant hashing
> in the ROM, which makes the system plausibly post-quantum.
>
> On 5 [ill.] zkVM traces of 2^{22}–2^{26} [ill.] rows at the same FRI parameters
> as the baseline (100-bit proven, 128-bit conjectured soundness [ill.]), end-to-end
> proving time excluding witness generation drops by 1.4–1.9× [ill.] and peak memory
> by 5.2× [ill.] versus [D23] on the same GPU. Our implementation and scripts are
> available.\footnote{anonymous link}

---

## T3 — Range-checked credential circuit (application / circuit)

### Bad

> Privacy matters. We give a ZK circuit for anonymous credentials which uses fewer
> constraints than all other circuits.

Wrong: no statement of what is proved, no proof system, "all other circuits" is
unfalsifiable, constraint counts are not comparable across arithmetizations, no
numbers.

### Good

> Anonymous credentials with attribute predicates (e.g. "age ≥ 18") are commonly
> proved with Groth16 over R1CS, where range checks by bit decomposition account for
> most constraints [E21] (CCS'21). Lookup-based range checks reduce this cost in
> Plonkish systems [F22], but no credential circuit has combined them with
> in-circuit signature verification over a non-native curve.
>
> We present a Plonkish circuit for credential presentation that replaces every
> bit-decomposition range check by a lookup into a 2^{16}-entry [ill.] table and
> verifies the issuer signature with limb-wise non-native arithmetic. Every gadget
> is checked for under-constraint by exhaustive witness enumeration over a toy field.
>
> For a credential with 8 [ill.] attributes, the circuit has 2^{17} [ill.] rows
> versus 2^{19} [ill.] rows for a bit-decomposition variant of the same statement in
> the same proof system, and proving takes 1.3 s [ill.] on a laptop, including
> witness generation. The setup is universal. Circuits and test vectors are
> provided.\footnote{anonymous link}
