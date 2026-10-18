"""No statement tested: targeted regression mutants for the eight priority framework builds.

Each mutant removes one promised guard or exemption. The unmutated tests must pass;
the named regression must then fail. Copies contain source and the selected tests.
"""

PATHS = ["tools", "compute.sh", "AGENTS.md", ".gitignore", ".claude/agents/medium-reviewer.md"]

COMMIT = "tools/tests/test_commit_message_checks.py::SuiteAfterTest::test_agents_only_accepts_scope_run_but_mixed_shared_code_requires_suite"
RUNNER = "tools/tests/test_run.py::SuiteTimeLimit::test_scope_run_stamps_only_completed_successful_module"
QUEUE = "tools/tests/test_lead_queue.py::LeadQueueTest::test_user_dictation_needs_no_agent_attempt_and_only_quotes_are_exempt"
SAVED = "tools/tests/test_lead_queue.py::LeadQueueTest::test_measurement_refusal_accepts_its_advertised_unsaved_disposition"
SPELL = "tools/tests/test_lead_queue.py::LeadQueueTest::test_narrowed_extension_compares_spell_start_and_has_review_confirmation"
PARTS = "tools/tests/test_draft_claim_sentences.py::DraftClaimSentences::test_lettered_baseline_citation_asks_each_other_part"
LABEL = "tools/tests/test_goal_progress.py::GoalProgressTest::test_narrowed_requires_proved_claim_removed_and_remaining_parts"
UNDER = "tools/tests/test_goal_progress.py::GoalProgressTest::test_unchanged_with_proof_explains_untouched_part_and_reason"
SEARCH = "tools/tests/test_stop_checks.py::RecordSearchBlockTest::test_unbuilt_untried_unexplored_and_open_claims_require_actual_search"
OUTPUT = "tools/tests/test_stop_checks.py::RecordSearchBlockTest::test_search_matches_are_printed_and_failed_or_previous_turn_searches_do_not_count"
REVIEW = "tools/tests/test_stop_checks_meta.py::UnreviewedLabelTest::test_report_does_not_clear_later_mathematics_or_another_paragraph"
READ = "tools/tests/test_refusal_gate.py::RefusalGateTest::test_copy_edit_and_quoted_read_verbs_do_not_clear_the_gate"
RELABEL = "tools/tests/test_notebook_append.py::NotebookAppendTests::test_progress_relabel_preserves_original_and_rejects_stale_or_unproved_changes"
PATHS_RULES = "tools/tests/test_math_link_permissions.py::LinkPermissionsTest::test_every_registered_path_and_both_shared_files_are_covered"
SETTINGS = "tools/tests/test_math_link_permissions.py::LinkPermissionsTest::test_merge_preserves_settings_mode_original_backup_and_is_idempotent"
TESTS = [COMMIT, RUNNER, QUEUE, SAVED, SPELL, PARTS, LABEL, UNDER, SEARCH, OUTPUT, REVIEW, READ, RELABEL, PATHS_RULES, SETTINGS]

MUTANTS = {
    "agents rule omitted": ("tools/commit_message_checks.py", "if 'AGENTS.md' in paths and (top / 'AGENTS.md').exists():", "if False:", [COMMIT]),
    "stale scope stamp accepted": ("tools/commit_message_checks.py", "if (top / 'AGENTS.md').stat().st_mtime > passed:", "if False:", [COMMIT]),
    "scope run not stamped": ("tools/tests/run.py", "if not failed and not slow and args.modules:", "if False:", [RUNNER]),
    "user dictation still needs attempts": ("tools/lead_queue.py", "dictated = bool(USER_SOURCE_RE.search(argv[5]))", "dictated = False", [QUEUE]),
    "user quote still checked as agent figure": ("tools/lead_queue.py", "if user_source:", "if False:", [QUEUE]),
    "advertised unsaved disposition rejected": ("tools/lead_queue.py", "if re.search(r'\\b(?:the )?figure was not saved\\b', text, re.I):", "if False:", [SAVED]),
    "narrowed spell guard omitted": ("tools/lead_queue.py", "if 'data-goal-progress=\"narrowed\"' in tag:", "if False:", [SPELL]),
    "other lemma parts omitted": ("tools/draft_claim_sentences.py", "others = {letter: summaries[cid] for letter in sorted(parts) if letter != selected.group(1).lower()}", "others = {}", [PARTS]),
    "all parts accepted unanswered": ("tools/draft_claim_sentences.py", "if any(len(tried.get(letter, '').split()) < ANSWER_WORDS for letter in row[3]):", "if False:", [PARTS]),
    "narrowed labels not required": ("tools/finish-turn.py", "if state == 'narrowed':", "if False:", [LABEL]),
    "understatement guard omitted": ("tools/finish-turn.py", "if state == 'unchanged' and supporting and statuses is not None:", "if False:", [UNDER]),
    "quoted search command accepted": ("tools/hooks/stop_checks.py", "if Path(program).name != 'search-claims.py':", "if False:", [SEARCH]),
    "failed search accepted": ("tools/hooks/stop_checks.py", "if not block.get('is_error') and output.strip() and not re.search(r'Exit code [1-9]|Traceback', output):", "if output.strip():", [OUTPUT]),
    "new mathematics cleared by old review": ("tools/hooks/stop_checks.py", "reports = [p for p in reports if re.sub(r'\\s+', ' ', p).casefold() not in drafted]", "reports = []", [REVIEW]),
    "failed code read accepted": ("tools/hooks/refusal_gate.py", "if call.get('error'):", "if False:", [READ]),
    "copy command counted as reader": ("tools/hooks/refusal_gate.py", "if verb not in ('grep', 'rg', 'sed', 'cat', 'head', 'awk'):", "if False:", [READ]),
    "historical stale relabel accepted": ("tools/notebook-append.py", "if old not in tag:", "if False:", [RELABEL]),
    "shell control transfer accepted": ("tools/shell_commands.py", "if effective and effective[0] in SHELL_CONTROL:", "if False:", [READ]),
    "pending spell confirmation accepted": ("tools/lead_queue.py", "if label == 'Reviewer confirmation':", "if False:", [SPELL]),
    "skipped scope assertions stamped": ("tools/tests/run.py", "for r in results) and not any(\n                        r[5] for r in results if r[0].startswith('test_agents_scope.')):", "for r in results):", [RUNNER]),
    "sibling worktrees omitted": ("tools/math_link_permissions.py", "for root in roots for name in SHARED_FILES", "for root in roots[:1] for name in SHARED_FILES", [PATHS_RULES]),
    "existing user settings discarded": ("tools/math_link_permissions.py", "settings = json.loads(original)", "settings = {}", [SETTINGS]),
    "original permission backup overwritten": ("tools/math_link_permissions.py", "if not backup.exists():", "if True:", [SETTINGS]),
    "settings symlink replaced": ("tools/math_link_permissions.py", "if path.is_symlink():\n        path = path.resolve(strict=True)", "if False:\n        path = path.resolve(strict=True)", [SETTINGS]),
}
