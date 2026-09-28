# Superseded: control_wholesale under the 2400-character schema ceiling

These partial cells had the budget SENTENCE removed from the prompt but still carried
`SUMMARY_SCHEMA`'s `maxLength: 2400` — a hard cap on the wholesale arm's entire memory for
the whole month, with no equivalent on the claim store. A "no length limit" arm capped at
about twenty lines with nothing in its prompt saying so is worse than an openly capped one,
because the constraint is invisible. Relaunched with the ceiling at 24000 characters and
`max_tokens` at 6000. Nothing deleted. See ../THE_WRITING_PROMPTS_WERE_NOT_THE_SAME.md
