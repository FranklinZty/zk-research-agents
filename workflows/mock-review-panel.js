export const meta = {
  name: 'cra-mock-review',
  description: 'Venue-calibrated mock review by three reviewer personas, then meta-review with prioritised action items',
  whenToUse: 'Phase P8 before submission, and after each major revision',
  phases: [{ title: 'Review' }, { title: 'Meta' }],
}
// args: { project: "/abs/path", venue: "EUROCRYPT" , pdf: "paper/main.pdf" }
const P = args.project, V = args.venue, PDF = args.pdf || 'paper/main.pdf'
const REVIEW = { type: 'object', properties: { score: { type: 'number' }, confidence: { type: 'number' },
  strengths: { type: 'array', items: { type: 'string' } }, weaknesses: { type: 'array', items: { type: 'string' } },
  questions: { type: 'array', items: { type: 'string' } } }, required: ['score', 'weaknesses'] }
const PERSONAS = ['soundness reviewer (proofs and Fiat–Shamir) from skills/mock-review', 'implementation-and-benchmark reviewer from skills/mock-review', 'application-and-industry-relevance reviewer from skills/mock-review']
phase('Review')
const reviews = (await parallel(PERSONAS.map(p => () => agent(
  `Review ${P}/${PDF} for ${V} as a ${p}. Use skills/venue-calibration for the scoring scale. Check claims against ${P}/CLAIMS.md and ${P}/EVIDENCE.md.`,
  { agentType: 'reviewer-sim', phase: 'Review', label: p, schema: REVIEW })))).filter(Boolean)
phase('Meta')
return await agent(`Write a meta-review into ${P}/REVIEWS.md (new round) from these reviews, then list action items each routed to an agent (writer/experimenter/theorist/figure-artist/lit-scout).\n${JSON.stringify(reviews)}`,
  { agentType: 'reviewer-sim', label: 'meta-review' })
