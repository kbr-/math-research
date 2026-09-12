# Affine defining extensions and the ordinary-degree audit

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-affine-extension-audit)
contains the full comparison arguments, explicit ENS product certificate,
characteristic-sensitive aggregate control, and unresolved simulation question.
This cycle follows the user's strategic question about PHP; it does not switch
the target or claim that a known short proof has been imported into ENS.

## Primary source and exact reading coverage

Russell Impagliazzo, Sasank Mouli, Toniann Pitassi,
The Surprising Power of Constant Depth Algebraic Proofs,
ECCC TR19-024, revision 2.

- [Version page](https://eccc.weizmann.ac.il/report/2019/024/revision/2/).
- [Public acquisition URL](https://eccc.weizmann.ac.il/report/2019/024/revision/2/download/).
- Acquired on 12 September 2026; the PDF header confirms revision 2.
- Read the introduction's extension descriptions and Theorems 1-4, printed
  pages 2-4; Definitions 6, 8, and 9, pages 7-9; the concluding extension-field
  question on page 25; and the Trinomial-PiSigma-PC definition/discussion on
  pages 28-29. The full simulation constructions were not read in this cycle.
- Local files: research/references/cache/IMP2019-rev2.pdf and
  research/references/extracted/IMP2019-rev2.txt. Both are explicitly ignored and
  listed as local-only in the reference redistribution metadata. Only source
  hashes, locators, our own arguments, and bounded summaries are checkpointed.

The degree comparisons in this entry are proved directly. The affine theorem
is an application of the notebook's existing substitution principle. The ENS
coefficient countermodel is over a satisfiable proper domain. The conjunction
identity uses every original companion at its actual degree; its lower bound
combines target degree and an all-zero model below companion activity.
The aggregate counting model is not a model of the full PHP base.

No new mathematical computation or historical numerical rerun was required.
No polynomial sparse-size bound is asserted for the expanded factorial
certificate, and no complete simulation result over our prime-field ENS system
is inferred from the external paper.

## Reproduction and timing scope

The protected acquisition and conversion commands were:

    ./compute.sh run TURN --threads 1 --category network_tool --timeout 90 -- \
      curl --fail --location --max-time 60 --output PDF-PATH \
      https://eccc.weizmann.ac.il/report/2019/024/revision/2/download/
    ./compute.sh run TURN --threads 1 --category local_processing --timeout 90 -- \
      pdftotext -layout PDF-PATH TEXT-PATH

Use fresh local-only paths when reproducing. The manifest preserves hashes of
the exact PDF and extraction used here.

The first browser PDF fetch timed out; the protected public download succeeded.
Conversion succeeded with eight PDF annotation-destination warnings, unrelated
to the text used. The initial cache-ignore assumption was incorrect: the
repository used per-paper exclusions, which were extended for this source before
any staging; both downloaded files are now confirmed ignored.
One notebook patch failed its context check before applying and was corrected.
These are acquisition/editing events, not failed mathematical claims.

A short initial outline was measured in the preceding cycle's final preparation.
This session records the targeted reading, new comparison proofs, source handling,
and checkpoint. The timing fragment and archived session preserve measured work;
full source text was read locally and is absent from the archived command output.
