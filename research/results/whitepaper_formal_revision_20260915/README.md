# Whitepaper revision from the completed formalization

The revised draft presents the generalized verified statements and follows the
human-readable proofs in the formalization research entries. All H01–H13
statements and proofs are included in the appendix. `statement-links.json`
records the numbered statements and their permanent Lean source targets.

The revision uses the residual cube proof, the dimension-free binary separator,
the primitive fixed-weight substitution proof (including unit spans), the finite
homological cover chain chase, and the uniform final parameter closure.
The telescoping statement retains upper bounds unless exact-degree hypotheses
are supplied. No new Lean proofs or optional generalization sweep were performed.

Validation: resource-controlled three-pass pdflatex build; numbered-statement
link coverage and local target existence checked. Existing formal verification
was reused. No PDF screenshots or visual inspection, at the user's request.
Build outputs and timing are retained by the session archive. Initial setup
and first reading preceded instrumentation. A sandboxed resource-status query
failed to reach user-systemd; the escalated status check and builds succeeded.
