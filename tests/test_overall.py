import tempfile
import unittest
from pathlib import Path

from axiombench.core import aggregate, overall_score
from axiombench.report import write_html


def example_rows():
    rows = []
    for track, mode, passed, total in [('general', None, 186, 300),
                                      ('math', None, 144, 300),
                                      ('cpp', 'generation', 69, 150),
                                      ('cpp', 'repair', 84, 150)]:
        for i in range(total):
            rows.append(dict(id=f'{track}-{mode}-{i}', track=track, mode=mode,
                             category='example', difficulty='basic',
                             passed=i < passed, status='pass' if i < passed else 'wrong_answer'))
    return rows


class OverallTests(unittest.TestCase):
    def test_equal_weights_despite_unequal_task_counts(self):
        score = overall_score(example_rows())
        self.assertEqual(score['score'], 53)
        self.assertEqual(score['display_score'], 53)
        self.assertTrue(score['comparable'])

    def test_partial_track_does_not_get_overall_score(self):
        for rows in ([], [r for r in example_rows() if r['track'] == 'math']):
            score = overall_score(rows)
            self.assertIsNone(score['score'])
            self.assertEqual(score['status'], 'unavailable')
            self.assertFalse(score['comparable'])

    def test_incomplete_run_remains_in_denominator_and_provisional(self):
        rows = example_rows()
        rows[0].update(passed=False, status='missing')
        rows[1].update(passed=False, status='api_error')
        score = overall_score(rows)
        self.assertEqual(score['score'], 52.83)
        self.assertEqual(score['incomplete_tasks'], 2)
        self.assertEqual(score['status'], 'provisional')
        self.assertFalse(score['comparable'])

    def test_integer_rounding_and_precise_score(self):
        rows = [dict(track=track, mode=mode, passed=passed, status='pass' if passed else 'wrong_answer')
                for track, mode, total, correct in [('general', None, 100, 50),
                    ('math', None, 100, 50), ('cpp', 'generation', 100, 50), ('cpp', 'repair', 100, 52)]
                for passed in [True]*correct + [False]*(total-correct)]
        self.assertEqual(overall_score(rows)['score'], 50.5)
        self.assertEqual(overall_score(rows)['display_score'], 51)

    def test_html_overall_and_escaped_model(self):
        rows = example_rows()
        report = dict(tasks=rows, summary=aggregate(rows), suite_sha256='fixture',
                      run_metadata={'model': '<script>bad</script>'},
                      cpp_modes={mode: aggregate([r for r in rows if r['mode'] == mode])['cpp']
                                 for mode in ('generation', 'repair')}, overall=overall_score(rows))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'report.html'
            write_html(path, report)
            text = path.read_text()
            self.assertIn('53 / 100', text)
            self.assertIn('Точный балл: 53.00', text)
            self.assertNotIn('<script>bad</script>', text)


if __name__ == '__main__':
    unittest.main()
