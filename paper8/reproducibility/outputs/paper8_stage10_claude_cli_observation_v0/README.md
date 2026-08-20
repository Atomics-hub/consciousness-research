# Stage 10: Claude CLI control observation

This package freezes a sanitized local transcription of a bounded Claude Code
control/probe session performed on 2026-08-19. It is observation evidence, not
an authorization, provider receipt, billing certificate, or proof of raw HTTP
attempt count.

The CLI was Claude Code 2.1.231. Model-free status reported a logged-in
first-party `claude.ai` Max subscription. A safe-mode interactive session with
no tools and no user prompt exposed selectors for Opus 5 (1M), Fable 5,
Sonnet 5, and Haiku 4.5.

One subsequent no-tools, nonpersistent JSON probe requested Sonnet and asked
for the single word `READY`. It completed in one visible turn with no web
search, web fetch, permission denial, or tool surface. However, its
`modelUsage` contained both:

- requested `claude-sonnet-5`, canonical `claude-sonnet-5`, provider
  `firstParty`; and
- `claude-haiku-4-5-20251001`, canonical `claude-haiku-4-5`, provider
  `firstParty`.

This is direct evidence that one visible CLI turn does not establish one model
activation or one raw HTTP attempt. The Stage-9 transport blocker therefore
remains. The CLI-reported `$0.0113217` is retained as an accounting value only;
it does not prove a separately billed charge outside included Max usage.

No account email, organization identifier, OAuth data, session ID, request ID,
UUID, raw response stream, keychain material, or credential value is retained.

Local status: `OBSERVATION_RECORDED_NONAUTHENTICATING`.

External disposition: `NO_GO_MULTI_MODEL_USAGE_AND_RAW_HTTP_COUNT_UNRESOLVED`.
