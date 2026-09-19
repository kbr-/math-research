# Interactive claim-graph implementation plan

Plan for [IDEAS.md item 8](../../IDEAS.md). Split from the broader checklist
on 19 September 2026; existing pending tasks remain pending.

Build graph visualization and graph-specific exports on the reviewed relationship
data produced by INDEX_MIGRATION.md. Populating and validating relationships is index
curation; UI, layout, visual navigation and Pages integration belong here.

This plan is separate from [index migration and curation](INDEX_MIGRATION.md).
Follow the workspace rules when implementing it; planning alone does not start
research, formalization, parallel agents, installations, or publication.

## Tasks

- [ ] Design the graph around the populated, reviewed data; start with a selected
      claim and its neighborhood, and keep complete-graph views readable.
- [ ] Select the visualization implementation and obtain any dependency approval
      required by COMPUTATION_RULES.md. Treat CDN libraries as dependencies too;
      document licensing and pin/vendor assets if offline use is supported.
- [ ] Implement zoom/pan, selection, a statement/scope/source side panel, notebook
      and Lean links, and distinct visual treatment of claims, obstructions and
      finite checks. Display review and partial-formalization status accurately.
- [ ] Implement topic/status/date/formalization filters, ancestor/descendant
      highlighting, current-working-context route view, and correction-impact views.
- [ ] Provide grouping/collapsing or an alternative date/topic layout to avoid a
      whole-graph tangle. Treat degree/citation counts as navigation signals, not
      automatic measures of significance or formalization priority.
- [ ] Show edge types, evidence, uncertainty and incomplete coverage; disconnected
      branches are not automatically worthless or dead research.
- [ ] Provide accessible textual navigation and a useful empty/partial-data state.
- [ ] Add GraphML or DOT export for external tools, with stable IDs and documented
      direction/type semantics, alongside the existing JSON export.
- [ ] Integrate the graph and permitted data/assets into the minimal Pages build
      and local live mode, preserving project-relative links and update behavior.
- [ ] Test navigation, filtering, source links, rendering performance and offline
      behavior where promised; publish only under a separate valid push authorization.

## Acceptance and integration

- [ ] Demonstrate a newly indexed result and a corrected claim in the graph,
      with source links, uncertainty and review scope visible throughout navigation.
- [ ] Verify local and published asset/link behavior, correction-impact traversal,
      accessible fallbacks and incomplete-data states without claiming the graph is
      a proof certificate.
- [ ] Document operation and validation evidence; use only approved dependencies
      and publish only with a valid separate authorization.
