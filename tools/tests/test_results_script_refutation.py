"""The launcher's check that a script under research/results names an output that would refute it."""
import subprocess
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CS = SourceFileLoader('compute_sh', str(ROOT / 'compute.sh')).load_module()
BOTH = ('"""Statement.\nRefuted by: a rank above n in any of the nine cases.\n'
        'Possible because: the search for the rank does not use the bound.\n"""\n')


def script(folder, text, name='control.py', where=('research', 'results', 'run_01')):
    path = Path(folder).joinpath(*where, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def check(*paths):
    return dict(CS.scripts_without_refuting_outcome(['python3', *map(str, paths)]))


class LongRunPowerTest(unittest.TestCase):
    def test_a_long_run_script_states_its_power_and_parallel_use(self):
        with tempfile.TemporaryDirectory() as folder:
            bare = script(folder, BOTH + 'print(1)\n', 'a.py')
            found = dict(CS.long_scripts_without_power(['python3', str(bare)]))
            self.assertEqual(len(found[str(bare)]), 2)
            stated = script(folder, BOTH.replace('"""\n', 'Decisive at these sizes: the two outcomes differ by '
                                                 'ten times the seed spread.\nParallel use: one process per seed '
                                                 'over fourteen CPUs.\n"""\n', 1) + 'print(1)\n', 'b.py')
            self.assertEqual(dict(CS.long_scripts_without_power(['python3', str(stated)])), {})


class PositiveControlTest(unittest.TestCase):
    def test_a_declared_control_needs_a_positive_one_or_a_reason(self):
        # 16 October 2026: a null control could not show a positive excess would be seen.
        with tempfile.TemporaryDirectory() as folder:
            null = script(folder, BOTH.replace('"""\n', 'Control: at K=1 the excess must be zero as recorded.\n"""\n',
                                               1), 'a.py')
            self.assertEqual(CS.scripts_without_positive_control(['python3', str(null)]), [str(null)])
            positive = script(folder, BOTH.replace('"""\n', 'Control: at K=1 the excess must be zero as recorded.\n'
                                                   'Positive control: the recorded instance with a linear axiom '
                                                   'gives excess one.\n"""\n', 1), 'b.py')
            reason = script(folder, BOTH.replace('"""\n', 'Control: the count must match the record.\n'
                                                 'No positive control: the quantity is a count with no effect to '
                                                 'detect.\n"""\n', 1), 'c.py')
            plain = script(folder, BOTH + 'print(1)\n', 'd.py')       # no control declared
            self.assertEqual(CS.scripts_without_positive_control(['python3', str(positive), str(reason),
                                                                  str(plain)]), [])


class ForcedByCountsTest(unittest.TestCase):
    def test_a_declared_control_states_what_its_counts_force(self):
        # 17 October 2026: two rank controls had fewer rows than the rank they were to miss.
        with tempfile.TemporaryDirectory() as folder:
            bare = script(folder, BOTH.replace('"""\n', 'Control: dropping one set must lower the rank.\n"""\n', 1),
                          'a.py')
            self.assertEqual(CS.scripts_without_forced_counts(['python3', str(bare)]), [str(bare)])
            counted = script(folder, BOTH.replace('"""\n', 'Control: dropping one set must lower the rank.\n'
                                                  'Forced by counts: nothing, the remaining rows number 20 against '
                                                  'rank 11.\n"""\n', 1), 'b.py')
            plain = script(folder, BOTH + 'print(1)\n', 'c.py')       # no control declared
            self.assertEqual(CS.scripts_without_forced_counts(['python3', str(counted), str(plain)]), [])


class ProcessPoolThreadsTest(unittest.TestCase):
    def test_scripts_that_start_worker_processes_are_found(self):
        # 17 October 2026: 14 workers at --threads 14 timed out at more than three times their estimate.
        with tempfile.TemporaryDirectory() as folder:
            pooled = script(folder, 'from concurrent.futures import ProcessPoolExecutor\n'
                                    'with ProcessPoolExecutor(max_workers=14) as pool:\n    pass\n', 'p.py')
            mp = script(folder, 'import multiprocessing\nmultiprocessing.Pool(4)\n', 'm.py')
            plain = script(folder, 'import numpy\nprint(numpy.ones(3).sum())\n', 'n.py')
            named = script(folder, '"""Mentions ProcessPoolExecutor only in prose."""\nprint(1)\n', 'q.py')
            self.assertEqual(CS.scripts_with_process_pool(['python3', str(pooled)]), [str(pooled)])
            self.assertEqual(CS.scripts_with_process_pool(['python3', str(mp)]), [str(mp)])
            bare = script(folder, 'from multiprocessing import Pool\nPool(4).map(abs, [1])\n', 'b.py')
            self.assertEqual(CS.scripts_with_process_pool(['python3', str(bare)]), [str(bare)])
            other = script(folder, '"""Unlike multiprocessing, this uses a thread pool."""\n'
                                   'from mylib import Pool\nPool(4)\n', 'o.py')
            self.assertEqual(CS.scripts_with_process_pool(['python3', str(plain), str(named), str(other)]), [])

    def test_the_admission_of_threads_and_declared_workers(self):
        with tempfile.TemporaryDirectory() as folder:
            pooled = script(folder, 'from concurrent.futures import ProcessPoolExecutor\n'
                                    'with ProcessPoolExecutor(max_workers=7) as pool:\n    pass\n', 'p.py')
            plain = script(folder, 'print(1)\n', 'n.py')
            cmd = ['python3', str(pooled)]
            self.assertIsNone(CS.pool_admission_error(cmd, 1, 0))           # one thread per worker
            self.assertIsNone(CS.pool_admission_error(cmd, 2, 7))           # 7 x 2 = 14
            self.assertIsNotNone(CS.pool_admission_error(cmd, 3, 7))        # 21 > 14
            self.assertIsNotNone(CS.pool_admission_error(cmd, 4, 0))        # no declaration
            # The reviewer's way around: declaring fewer workers than the script writes.
            self.assertIn('7 workers', CS.pool_admission_error(cmd, 14, 1))
            self.assertIsNone(CS.pool_admission_error(['python3', str(plain)], 14, 0))
            keyword = script(folder, 'import multiprocessing\nmultiprocessing.Pool(processes=8)\n', 'k.py')
            self.assertIn('8 workers', CS.pool_admission_error(['python3', str(keyword)], 14, 1))

    def test_a_long_pooled_run_with_one_thread_per_worker_is_not_serial(self):
        # 17 October 2026: --threads 1 --pool-workers 14, as the admission check asks, was refused as serial
        self.assertFalse(CS.serial_reason_needed(1400, 1, 14, ''))
        self.assertTrue(CS.serial_reason_needed(1400, 1, 0, ''))         # one thread, no pool: serial
        self.assertTrue(CS.serial_reason_needed(1400, 1, 2, ''))         # two CPUs in all
        self.assertFalse(CS.serial_reason_needed(1400, 1, 0, 'one elimination, which does not split'))
        self.assertFalse(CS.serial_reason_needed(300, 1, 0, ''))         # short runs need no reason


class BaselineTest(unittest.TestCase):
    def test_a_tested_statement_needs_a_baseline_line(self):
        # 16 October 2026: a strip computation's expectation followed from the bare point count.
        with tempfile.TemporaryDirectory() as folder:
            bare = script(folder, BOTH + 'print(1)\n', 'a.py')
            self.assertEqual(CS.scripts_without_baseline(['python3', str(bare)]), [str(bare)])
            based = script(folder, BOTH.replace('"""\n', 'Baseline: the bare point count gives at most q '
                                                'sqrt N, which does not fix the growth in N.\n"""\n', 1), 'b.py')
            exempt = script(folder, '"""No statement tested: it converts the archived table to JSON.\n"""\n', 'c.py')
            passing = script(folder, '"""Our baseline: the count.\nRefuted by: a rank above n in any case.\n'
                                     'Possible because: the search for the rank does not use the bound.\n"""\n',
                             'd.py')
            self.assertEqual(CS.scripts_without_baseline(['python3', str(based), str(exempt)]), [])
            self.assertEqual(CS.scripts_without_baseline(['python3', str(passing)]), [str(passing)])

    def test_a_tested_statement_needs_a_record_check_line(self):
        # 16 October 2026: a review's test was decided by three recorded lemmas, found after the run.
        import os
        with tempfile.TemporaryDirectory() as folder:
            bare = script(folder, BOTH + 'print(1)\n', 'a.py')
            self.assertEqual(CS.scripts_without_record_check(['python3', str(bare)]), [str(bare)])
            read = script(folder, BOTH.replace('"""\n', 'Record checked: lem:top-degree-killer-transfer and '
                                               'lem:cylinder-killer-degree do not decide the sum case.\n"""\n', 1),
                          'b.py')
            exempt = script(folder, '"""No statement tested: it converts the archived table to JSON.\n"""\n', 'c.py')
            self.assertEqual(CS.scripts_without_record_check(['python3', str(read), str(exempt)]), [])
            os.utime(bare, (1000, 1000))                       # written before the rule
            self.assertEqual(CS.scripts_without_record_check(['python3', str(bare)]), [])

    def test_the_prompting_script_is_refused(self):
        strip = ROOT / 'research/results/ultimate_matching_review4_20261016/strip_dp.py'
        self.assertEqual(CS.scripts_without_baseline(['python3', str(strip)]), [str(strip)])


class ResultsScriptRefutationTest(unittest.TestCase):
    def test_both_labelled_lines_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(check(script(folder, BOTH + 'print(1)\n')), {})

    def test_each_missing_line_is_named(self):
        with tempfile.TemporaryDirectory() as folder:
            neither = script(folder, '"""Expectation: the value is 3."""\nprint(1)\n', 'a.py')
            no_reason = script(folder, '"""Refuted by: a value of four in any case.\n"""\nprint(1)\n', 'b.py')
            found = check(neither, no_reason)
            self.assertEqual(len(found[str(neither)]), 2)
            self.assertEqual(len(found[str(no_reason)]), 1)
            self.assertIn('Possible because:', found[str(no_reason)][0])

    def test_the_subjects_own_words_in_passing_do_not_count(self):
        with tempfile.TemporaryDirectory() as folder:
            passing = script(folder, '"""The refutation degree of H; every refutation of H is replayed.\n'
                                     'Which of the possible values occur?  A degree above six would refute it."""\n')
            self.assertEqual(len(check(passing)[str(passing)]), 2)

    def test_a_label_needs_five_words(self):
        with tempfile.TemporaryDirectory() as folder:
            short = script(folder, '"""Refuted by: failure.\nPossible because: yes.\n"""\n')
            self.assertEqual(len(check(short)[str(short)]), 2)

    def test_a_label_inside_a_line_does_not_count(self):
        with tempfile.TemporaryDirectory() as folder:
            quoted = script(folder, 'print("Refuted by: a rank above n in any case")\n'
                                    'x = "see Possible because: the search does not use it"\n')
            self.assertEqual(len(check(quoted)[str(quoted)]), 2)
            comment = script(folder, '# Refuted by: a rank above n in any case.\n'
                                     '#   Possible because: the search does not use the bound.\n', 'd.py')
            self.assertEqual(check(comment), {})

    def test_a_script_that_tests_nothing_says_so(self):
        with tempfile.TemporaryDirectory() as folder:
            table = script(folder, '"""No statement tested: this script tabulates saved output for the entry.\n"""\n')
            self.assertEqual(check(table), {})
            bare = script(folder, '"""No statement tested: tables.\n"""\n', 'c.py')
            self.assertIn(str(bare), check(bare))

    def test_lines_far_below_the_head_do_not_count(self):
        with tempfile.TemporaryDirectory() as folder:
            late = script(folder, '"""Expectation."""\n' + 'x = 1\n' * CS.REFUTATION_HEAD_LINES + BOTH)
            self.assertEqual(len(check(late)), 1)

    def test_sources_drivers_data_and_scripts_elsewhere_are_not_checked(self):
        with tempfile.TemporaryDirectory() as folder:
            others = [script(folder, 'print(1)\n', where=('scratch',)), script(folder, '{}\n', 'table.json'),
                      script(folder, 'int main(){}\n', 'kernel.c'), script(folder, 'int main(){}\n', 'kernel.cpp'),
                      script(folder, 'echo 1\n', 'drive.sh')]
            self.assertEqual(check(*others), {})

    def test_the_launcher_itself_refuses_the_run(self):
        with tempfile.TemporaryDirectory() as folder:
            path = script(folder, '"""Expectation: the value is 3."""\nprint(1)\n')
            for args in (['git', 'init', '-q'], ['git', 'add', '-A'],
                         ['git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 's']):
                subprocess.run(args, cwd=folder, check=True, capture_output=True)
            refused = subprocess.run([str(ROOT / 'compute.sh'), '--timeout', '20', 'python3', str(path)],
                                     capture_output=True, text=True)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn('Refuted by:', refused.stderr)
            self.assertIn('No statement tested:', refused.stderr)


if __name__ == '__main__':
    unittest.main()
