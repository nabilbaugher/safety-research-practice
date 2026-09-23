"""Small, editable experiment harness. Python 3.11+; GPU dependencies only for run."""
from __future__ import annotations
import argparse
import collections
import dataclasses
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import re
import sys
import time

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'vendor' / 'nocot_bench'))
from datagen.banks import brew
from datagen.common import run_qc

MODEL = 'Qwen/Qwen3-8B'
REVISION = 'b968826d9c46dd6066d109eabc6255188de91218'  # audited cached Qwen3-8B revision


def read_rows(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def compact_table(problem):
    """Render exactly the same transitions as a table; retain query verbatim."""
    lines = problem.splitlines()
    rules = [brew._BREW_RULE.match(line) for line in lines]
    rules = [m for m in rules if m]
    assert len(rules) >= 3
    ingredients = [rules[0].group(i) for i in (3, 5, 7)]
    out = ['Each row gives the new color after adding one ingredient.',
           'Current color | ' + ' | '.join(ingredients)]
    for m in rules:
        assert [m.group(i) for i in (3, 5, 7)] == ingredients
        out.append(' | '.join(m.group(i) for i in (1, 2, 4, 6)))
    out.extend(lines[-2:])
    return '\n'.join(out)


def make_messages(problem, arm):
    if arm.get('format', 'prose') == 'table':
        problem = compact_table(problem)
    filler = int(arm.get('filler_dots', 0))
    if filler:
        problem += '\nFiller (ignore): ' + ' '.join(['.'] * filler)
    if arm['thinking']:
        instruction = 'Solve the problem. You may work through it, keeping your reasoning concise. Finish with exactly one line: Answer: COLOR, replacing COLOR with the final lowercase color.'
    else:
        instruction = 'Answer immediately. Do not explain or show any working. Output exactly one line: Answer: COLOR, replacing COLOR with the final lowercase color.'
    if 'instruction' in arm:
        instruction = arm['instruction']
    return [{'role': 'system', 'content': 'Follow the response instructions carefully.'},
            {'role': 'user', 'content': problem + '\n\n' + instruction}]


def prepare(config):
    levels = config['levels']
    n = config['per_level']
    colors = tuple(config.get('colors', brew.COLORS))
    if len(set(colors)) != len(colors) or len(colors)<3 or not set(colors)<=set(brew.COLORS):
        raise ValueError('Use at least three unique colors from the generator alphabet.')
    if len(set(levels)) != len(levels) or n < 1 or any(h < 1 or h >= len(colors) for h in levels):
        raise ValueError('Levels must be unique, positive, and smaller than the number of colors; per_level must be positive.')
    arms = config['arms']
    if len({a['name'] for a in arms}) != len(arms):
        raise ValueError('Arm names must be unique.')
    # Caps remain feasible as participants change sample sizes.
    cfg = brew.Config(rungs=tuple((f'h{h}', ((h, n),)) for h in levels), n_shots=0, colors=colors,
                      bank_gold_cap=max(7, math.ceil(n*len(levels)/len(colors))+2),
                      rung_gold_cap=max(2, math.ceil(n/len(colors))+1), chance=None)
    items = brew.generate(cfg, seed=config['task_seed'])
    report = run_qc('brew', items, solve=brew.solve)
    assert report.ok, report.summary()
    requests = []
    for item in items:
        item_id = f"s{config['task_seed']}-p{item.problem_number}"
        for arm in arms:
            requests.append(dict(id=item_id+'-'+arm['name'], item_id=item_id,
                difficulty=item.difficulty, gold=item.answer, problem=item.problem,
                arm=arm['name'], thinking=arm['thinking'], messages=make_messages(item.problem,arm),
                settings=dict(temperature=arm.get('temperature',0.6),top_p=arm.get('top_p',0.95),
                              top_k=arm.get('top_k',20),max_tokens=arm.get('max_tokens',3072 if arm['thinking'] else 256),
                              seed=arm.get('seed',1729))))
    return requests


def parse_output(raw, thinking=False, finish_reason='stop'):
    """Do not grade mentions inside reasoning; accept a unique final answer line."""
    closed = '</think>' in raw
    if closed:
        trace, final = raw.rsplit('</think>',1)
        trace = trace.replace('<think>','').strip()
    elif thinking:
        trace, final = raw, ''
    else:
        trace, final = '', raw
    matches = re.findall(r'^\s*Answer:\s*('+'|'.join(brew.COLORS)+r')\s*$', final, re.M|re.I)
    # Trailing explanations / multiple answer lines are malformed.
    last_line = final.strip().splitlines()[-1] if final.strip() else ''
    end = re.fullmatch(r'Answer:\s*('+'|'.join(brew.COLORS)+r')',last_line,re.I)
    answer = matches[0].lower() if len(matches)==1 and end else None
    truncated = finish_reason == 'length'
    if truncated:
        answer = None
    direct_adherent = not trace and bool(re.fullmatch(r'\s*Answer:\s*('+'|'.join(brew.COLORS)+r')\s*',final,re.I)) and not truncated
    return dict(answer=answer, valid=answer is not None, final=final.strip(), trace=trace,
                thought_closed=closed,truncated=truncated,direct_adherent=direct_adherent)


def run(config, output):
    import subprocess
    import torch
    import transformers
    import vllm
    from vllm import LLM, SamplingParams
    out = Path(output)
    if out.exists():
        raise FileExistsError('Choose a new output path to avoid mixing experiments.')
    out.parent.mkdir(parents=True, exist_ok=True)
    requests = prepare(config)
    started=time.time()
    llm=LLM(model=config.get('model',MODEL), revision=config.get('revision',REVISION),
            dtype='bfloat16',max_model_len=8192,gpu_memory_utilization=0.85,
            max_num_seqs=128,enforce_eager=True,enable_prefix_caching=True,seed=1729)
    tok=llm.get_tokenizer()
    loaded=time.time()
    meta=dict(config=config,load_seconds=loaded-started,started=started,
              python=platform.python_version(),torch=torch.__version__,transformers=transformers.__version__,vllm=vllm.__version__,
              gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,driver_version','--format=csv,noheader'],text=True).strip(),
              source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              request_sha256=hashlib.sha256(json.dumps(requests,sort_keys=True).encode()).hexdigest(),
              resolved_model_revision=config.get('revision',REVISION),
              fresh_completions=0)
    write_json(str(out)+'.meta.json',meta)
    Path(str(out)+'.source.py').write_bytes(Path(__file__).read_bytes())
    with out.open('x') as f:
        # Complete one arm per batch so per-arm generation time is interpretable.
        for arm in config['arms']:
            reqs=[r for r in requests if r['arm']==arm['name']]
            for offset in range(0,len(reqs),64):
                batch=reqs[offset:offset+64]
                prompts=[tok.apply_chat_template(r['messages'],tokenize=False,add_generation_prompt=True,enable_thinking=r['thinking']) for r in batch]
                params=[SamplingParams(**r['settings']) for r in batch]
                tick=time.time()
                outputs=llm.generate(prompts,params,use_tqdm=False)
                elapsed=time.time()-tick
                for r,o,prompt in zip(batch,outputs,prompts):
                    v=o.outputs[0]
                    parsed=parse_output(v.text,r['thinking'],v.finish_reason)
                    row=dict(r,raw=v.text,**parsed,correct=parsed['answer']==r['gold'],
                             rendered_prompt=prompt,input_tokens=len(o.prompt_token_ids),output_tokens=len(v.token_ids),
                             finish_reason=v.finish_reason,batch_seconds=elapsed,batch_id=f"{arm['name']}-{offset}",
                             generated_at=time.time())
                    f.write(json.dumps(row)+'\n')
                f.flush()
                meta['fresh_completions']+=len(batch)
                print(json.dumps({'arm':arm['name'],'completed':meta['fresh_completions'],'seconds':round(elapsed,2)}),flush=True)
    meta.update(finished=time.time(),inference_seconds=time.time()-loaded)
    write_json(str(out)+'.meta.json',meta)
    print(json.dumps(meta),flush=True)


def paired_interval(a,b,seed=91):
    """Stratified paired percentile bootstrap of accuracy difference a minus b."""
    if set(a)!=set(b):
        raise ValueError('Paired arms must contain identical problem IDs.')
    strata=collections.defaultdict(list)
    for k in sorted(a):
        assert a[k]['gold']==b[k]['gold'] and a[k]['difficulty']==b[k]['difficulty']
        strata[a[k]['difficulty']].append(int(a[k]['correct'])-int(b[k]['correct']))
    rng=random.Random(seed)
    vals=[]
    for _ in range(2000):
        vals.append(sum(sum(rng.choices(d,k=len(d))) for d in strata.values())/len(a))
    vals.sort()
    return [vals[49],vals[1949]]


def wilson_interval(correct, n):
    """Marginal 95% Wilson score interval for a binomial accuracy."""
    if n <= 0 or not 0 <= correct <= n:
        raise ValueError('Require n > 0 and 0 <= correct <= n.')
    z=1.959963984540054
    p=correct/n
    denominator=1+z*z/n
    center=(p+z*z/(2*n))/denominator
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denominator
    return [max(0.,center-half), min(1.,center+half)]


def analyze(path, output_dir, reference=None):
    rows=read_rows(path)
    if reference:
        rows=read_rows(reference)+rows
    if len({r['id'] for r in rows})!=len(rows):
        raise ValueError('Duplicate request IDs.')
    for r in rows:
        p=parse_output(r['raw'],r['thinking'],r['finish_reason'])
        if p['answer']!=r['answer'] or (p['answer']==r['gold'])!=r['correct']:
            raise ValueError('Saved grade disagrees with parser.')
    grouped=collections.defaultdict(list)
    for r in rows:
        grouped[r['arm']].append(r)
    summary={}
    for arm,rs in grouped.items():
        counts={}
        for level in ['all']+sorted({r['difficulty'] for r in rs}):
            sub=rs if level=='all' else [r for r in rs if r['difficulty']==level]
            counts[str(level)]=dict(n=len(sub),correct=sum(r['correct'] for r in sub),
               valid=sum(r['valid'] for r in sub),truncated=sum(r['truncated'] for r in sub),
               direct_adherent=sum(r['direct_adherent'] for r in sub),
               mean_output_tokens=round(sum(r['output_tokens'] for r in sub)/len(sub),1))
            if level != 'all':
                counts[str(level)]['wilson_95']=wilson_interval(counts[str(level)]['correct'],len(sub))
        summary[arm]=counts
    contrasts={}
    if 'direct' in grouped:
        base={r['item_id']:r for r in grouped['direct']}
        for arm,rs in grouped.items():
            if arm=='direct':continue
            a={r['item_id']:r for r in rs}
            if set(a)!=set(base):continue
            contrasts[arm+' minus direct']=dict(delta=sum(int(a[k]['correct'])-int(base[k]['correct']) for k in a)/len(a),
                                             bootstrap_95=paired_interval(a,base),n=len(a))
    result=dict(counts=summary,paired_contrasts=contrasts,
                note='Per-depth accuracy: marginal 95% Wilson intervals. Overall differences: 95% stratified paired bootstrap. '
                     'Exploratory sampling intervals, not model/prompt or distribution-shift uncertainty. '
                     'Marginal interval overlap is not a paired test; bootstrap intervals can collapse with uniform observed differences.')
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    write_json(out/'summary.json',result)
    lines=['# Results','', '| Arm | Correct / total | Valid | Truncated | Strict direct format | Mean output tokens |',
           '| --- | --- | --- | --- | --- | --- |']
    for arm,levels in summary.items():
        s=levels['all'];lines.append(f"| {arm} | {s['correct']}/{s['n']} | {s['valid']} | {s['truncated']} | {s['direct_adherent']} | {s['mean_output_tokens']} |")
    lines += ['', '## Accuracy by difficulty', '',
              '| Arm | Transformations | Correct / total | Accuracy | 95% Wilson interval |',
              '| --- | --- | --- | --- | --- |']
    for arm,levels in summary.items():
        for level,s in levels.items():
            if level=='all':continue
            lo,hi=s['wilson_95']
            lines.append(f"| {arm} | {level} | {s['correct']}/{s['n']} | {s['correct']/s['n']:.1%} | [{lo:.1%}, {hi:.1%}] |")
    lines += ['', '## Overall paired differences', '',
              '| Contrast | Matched problems | Difference (percentage points) | 95% paired bootstrap interval |',
              '| --- | --- | --- | --- |']
    for contrast,s in contrasts.items():
        lo,hi=s['bootstrap_95']
        lines.append(f"| {contrast} | {s['n']} | {100*s['delta']:+.1f} | [{100*lo:+.1f}, {100*hi:+.1f}] |")
    if not contrasts:
        lines += ['', 'No matched comparison against an arm named `direct` was available.']
    lines += ['', result['note']]
    (out/'SUMMARY.md').write_text('\n'.join(lines)+'\n')
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(7.8,4.8))
        for arm,ls in summary.items():
            xs=[int(k) for k in ls if k!='all'];ys=[ls[str(k)]['correct']/ls[str(k)]['n'] for k in xs]
            intervals=[ls[str(k)]['wilson_95'] for k in xs]
            errors=[[max(0.,y-ci[0]) for y,ci in zip(ys,intervals)],
                    [max(0.,ci[1]-y) for y,ci in zip(ys,intervals)]]
            sizes={ls[str(k)]['n'] for k in xs}
            label=f'{arm} (n={next(iter(sizes))} per depth)' if len(sizes)==1 else f'{arm} (n varies; see summary)'
            ax.errorbar(xs,ys,yerr=errors,marker='o',capsize=4,label=label)
        ax.set(xlabel='Number of transformations',ylabel='Accuracy',ylim=(-.03,1.03),title='Accuracy by condition and task depth')
        ax.set_xticks(sorted({r['difficulty'] for r in rows}))
        ax.legend();ax.grid(alpha=.2)
        fig.text(.5,.02,'95% Wilson intervals per condition; paired differences are reported in SUMMARY.md.',ha='center',fontsize=9)
        fig.tight_layout(rect=(0,.05,1,1));fig.savefig(out/'accuracy.png',dpi=170);plt.close(fig)
    except ImportError:
        print('Matplotlib unavailable; saved table and JSON.')
    print(json.dumps(result,indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ['prepare','run']:
        q=sub.add_parser(name);q.add_argument('--config',required=True);q.add_argument('--output',required=True)
    q=sub.add_parser('analyze');q.add_argument('results');q.add_argument('--output-dir',default='analysis');q.add_argument('--reference')
    q=sub.add_parser('inspect');q.add_argument('results');q.add_argument('--arm');q.add_argument('--item-id');q.add_argument('--limit',type=int,default=3)
    args=p.parse_args()
    if args.command=='analyze':analyze(args.results,args.output_dir,args.reference)
    elif args.command=='inspect':
        rows=[r for r in read_rows(args.results) if (not args.arm or r['arm']==args.arm) and (not args.item_id or r['item_id']==args.item_id)]
        for r in rows[:args.limit]:print(json.dumps({k:r[k] for k in ['item_id','arm','difficulty','gold','answer','correct','raw']},indent=2))
    else:
        cfg=json.loads(Path(args.config).read_text())
        if args.command=='run':run(cfg,args.output)
        else:
            rows=prepare(cfg);Path(args.output).parent.mkdir(parents=True,exist_ok=True)
            Path(args.output).write_text(''.join(json.dumps(r)+'\n' for r in rows))
            print(f'Prepared {len(rows)} requests; no inference.')

if __name__=='__main__': main()
