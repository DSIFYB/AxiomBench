import copy
import unittest
from axiombench.comparison import compare_reports


def report(passed):
    return dict(suite_sha256='fixture',profile='full',axiombench_version='0.3.0',docker_image_id='compiler',
                run_metadata=dict(model='fixture',selected_ids_sha256='ids',temperature=0,max_tokens=4096),
                tasks=[dict(id=f'{track}-{mode}-{family}-{variant}',family=f'{track}-{mode}-{family}',
                            track=track,mode=mode,passed=passed,status='pass' if passed else 'wrong_answer')
                       for track,mode in [('general',None),('math',None),('cpp','generation'),('cpp','repair')]
                       for family in range(3) for variant in range(2)])


class ComparisonTests(unittest.TestCase):
    def test_identical_results_have_zero_difference(self):
        result=compare_reports(report(True),report(True),resamples=100)
        self.assertEqual(result['family_bootstrap_95'],[0,0])
        self.assertFalse(result['interval_excludes_zero'])

    def test_clear_difference_and_incompatible_runs(self):
        result=compare_reports(report(True),report(False),resamples=100)
        self.assertEqual(result['delta_a_minus_b'],100)
        self.assertTrue(result['interval_excludes_zero'])
        for key in ['suite_sha256','profile','axiombench_version']:
            other=report(False);other[key]='different'
            with self.assertRaises(ValueError):compare_reports(report(True),other)
        other=report(False);other['run_metadata']['max_tokens']=2048
        with self.assertRaises(ValueError):compare_reports(report(True),other)

    def test_missing_answers_not_comparable(self):
        other=report(False);other['tasks'][0]['status']='missing'
        with self.assertRaises(ValueError):compare_reports(report(True),other)

    def test_shared_cpp_families_are_resampled_together(self):
        a,b=report(False),report(False)
        for left,right in zip(a['tasks'],b['tasks']):
            if left['track']!='cpp':continue
            family=int(left['id'].split('-')[-2])
            left['family']=right['family']=f'cpp-{family}'
            passed=(family%2==0)==(left['mode']=='generation')
            left.update(passed=passed,status='pass' if passed else 'wrong_answer')
            right.update(passed=not passed,status='wrong_answer' if passed else 'pass')
        result=compare_reports(a,b,resamples=100)
        self.assertEqual(result['family_bootstrap_95'],[0,0])
