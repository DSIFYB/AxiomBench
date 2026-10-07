"""Compare saved local reports without querying any model or executing its code."""
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from axiombench.comparison import compare_reports
from axiombench.core import overall_score


def main():
    parser=argparse.ArgumentParser();parser.add_argument('reports',nargs='+');args=parser.parse_args()
    if len(args.reports)<2:parser.error('Provide at least two .report.json files')
    reports=[json.loads(Path(p).read_text()) for p in args.reports]
    try:
        for report in reports[1:]:compare_reports(reports[0],report)
    except ValueError as error:
        parser.error(str(error))
    reports.sort(key=lambda r:overall_score(r['tasks'])['score'],reverse=True)
    print('Model | AxiomBench Score (same suite/profile/settings)')
    for report in reports:print(f"{report['run_metadata']['model']} | {overall_score(report['tasks'])['score']:.2f}/100")
    for report in reports[1:]:print(json.dumps(compare_reports(reports[0],report),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
