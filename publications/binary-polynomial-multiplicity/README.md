# A note on binary polynomial multiplicities

**Preprint, version 1 (20 September 2026), not yet circulated.** A short source-based observation:
the bound in the published Question 4.3 of Bishnoi–Boyadzhiyska–Das–Mészáros
follows immediately from Dvir–Kopparty–Saraf–Sudan's multiplicity
Schwartz–Zippel lemma, without the question's threshold on k.

The contribution is identifying this implication, not a new multiplicity theorem.
This draft is not externally peer reviewed or formally verified. Whether the
connection was already known or a stronger question was intended remains for
clarification. No author contact or arXiv submission has been made for this note.

- [PDF](whitepaper.pdf) and [main TeX source](whitepaper.tex)
- [Argument](sections) and [bibliography](references.tex)
- [Readiness audit](READINESS_AUDIT.md) and [publication prerequisites](PUBLICATION_PREREQUISITES.md)
- [Feedback checklist](FEEDBACK.md) and [development history](DEVELOPMENT_HISTORY.md)
- [Paper-specific self-review checklist](CHECKLIST.md)
- [Reviewed source/PDF hashes](reviewed-files.json)

Author: Kamil Braun, with substantial assistance from GPT-6 Astra in Codex.
The paper contains its own definitions, statement, deduction, references and
assistance disclosure; this README is repository documentation, not a supplement
needed to read the note.

## Build

From the repository root, with the computation controls active:

```sh
./publications/binary-polynomial-multiplicity/build.sh
# Attach a build to an existing research clock:
./publications/binary-polynomial-multiplicity/build.sh --session TURN
```

Three pdflatex passes run inside `compute.sh`, with shell escape disabled and
separate pass logs. The script installs nothing. Original manuscript material
is CC BY 4.0; the build script is MIT under the root repository license.
Third-party results retain their attribution and rights.

Version 1 is being updated in place before circulation, as directed by the author.
Local editing checkpoints do not increment the paper's public version number.
