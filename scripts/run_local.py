"""One command: preflight, collect local model answers, grade, openable HTML report."""
import argparse
import datetime
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from axiombench.cli import main as cli_main, model_ids
from axiombench.core import docker_image_id


def call(arguments):
    sys.argv=['axiombench',*arguments]
    return cli_main()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--base-url',default='http://127.0.0.1:1234/v1')
    parser.add_argument('--model')
    parser.add_argument('--profile',choices=['quick','full'],default='quick')
    parser.add_argument('--track',choices=['all','general','math','cpp'],default='all')
    parser.add_argument('--max-tokens',type=int,default=4096)
    parser.add_argument('--image',default='gcc:14')
    parser.add_argument('--answers',help='Choose a persistent answer file, particularly for --resume')
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args()
    if args.resume and not args.answers:parser.error('--resume requires --answers pointing at the interrupted attempt')
    try:
        ids=model_ids(args.base_url)
        if not args.model:
            if len(ids)!=1:raise ValueError('Specify --model from this list: '+', '.join(ids))
            args.model=ids[0]
        elif args.model not in ids:raise ValueError('Model not advertised by /models: '+args.model)
        if args.track in ('all','cpp'):docker_image_id(args.image)
    except Exception as exc:
        print('Preflight failed: '+str(exc),file=sys.stderr)
        return 1
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    answers=Path(args.answers).resolve() if args.answers else ROOT/'results'/f'{stamp}-{args.profile}-{args.track}.jsonl'
    common=['--suite',str(ROOT/'benchmarks/extended-v0.2/tasks.jsonl.gz'),'--profile',args.profile,'--track',args.track]
    run_args=[*common,'run','--base-url',args.base_url,'--model',args.model,'--max-tokens',str(args.max_tokens),'--output',str(answers)]
    if args.resume:run_args+=['--resume']
    result=call(run_args)
    if result==1:return result
    report=answers.with_suffix('.report.json')
    graded=call([*common,'grade','--predictions',str(answers),'--output',str(report),'--image',args.image])
    print('Open results: '+str(report.with_suffix('.html')))
    return graded or result


if __name__=='__main__':sys.exit(main())
