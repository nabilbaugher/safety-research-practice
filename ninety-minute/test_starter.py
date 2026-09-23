"""CPU checks for grading, paired analysis, and task transformations."""
import unittest
import copy
import re
import contextlib
import io
import json
import tempfile
from pathlib import Path
import starter


class EvaluationTests(unittest.TestCase):
    def test_grade_final_not_reasoning(self):
        p=starter.parse_output('The color is blue.\n</think>\nAnswer: red',True)
        self.assertEqual(p['answer'],'red')
        self.assertFalse(p['direct_adherent'])
        self.assertIsNone(starter.parse_output('Answer: blue',True)['answer'])
        self.assertIsNone(starter.parse_output('Answer: blue',False,'length')['answer'])

    def test_invalid_and_noncompliant_are_distinct(self):
        for raw in ['blue','Answer: ultraviolet','Answer: red\nAnswer: blue','Answer: blue\nExplanation afterward']:
            self.assertIsNone(starter.parse_output(raw)['answer'])
        p=starter.parse_output('I calculate two steps.\nAnswer: blue')
        self.assertEqual(p['answer'],'blue')
        self.assertFalse(p['direct_adherent'])
        self.assertTrue(starter.parse_output('Answer: BLUE\n')['direct_adherent'])

    def test_generator_and_table_preserve_query(self):
        cfg=dict(task_seed=991,levels=[1,2,3,5],per_level=12,
                 arms=[dict(name='direct',thinking=False),dict(name='table',thinking=False,format='table')])
        rows=starter.prepare(cfg)
        self.assertEqual(len(rows),96)
        for a,b in zip(rows[::2],rows[1::2]):
            self.assertEqual(a['gold'],b['gold'])
            text=b['messages'][-1]['content']
            # Independent table reader, then execute its printed query.
            lines=text.splitlines()
            headers=lines[1].split(' | ')[1:]
            table={}
            for line in lines[2:12]:
                cells=line.split(' | ')
                table[cells[0]]=dict(zip(headers,cells[1:]))
            m=re.search(r'The potion starts out (\w+)\. You stir in, one at a time: (.+)\.',text)
            state=m[1]
            for ing in m[2].split(', then '):state=table[state][ing]
            self.assertEqual(state,a['gold'])
            self.assertNotIn('No explanation, no reasoning',a['messages'][-1]['content'])
        self.assertEqual(rows,starter.prepare(cfg))
        cfg.update(colors=['red','blue','green','gold'],levels=[1,2,3],per_level=24)
        small=starter.prepare(cfg)
        self.assertEqual(len(small),144)
        self.assertTrue(all(r['gold'] in cfg['colors'] for r in small))
        cfg['levels']=[10]
        with self.assertRaises(ValueError):starter.prepare(cfg)

    def test_paired_interval_and_mismatch(self):
        a={str(k):dict(correct=True,gold='blue',difficulty=1) for k in range(12)}
        b=copy.deepcopy(a)
        self.assertEqual(starter.paired_interval(a,b),[0,0])
        for r in b.values():r['correct']=False
        self.assertEqual(starter.paired_interval(a,b),[1,1])
        b.pop('0')
        with self.assertRaises(ValueError):starter.paired_interval(a,b)

    def test_wilson_interval_including_boundary_accuracy(self):
        # Standard 95% score interval for 12 successes out of 24.
        lo,hi=starter.wilson_interval(12,24)
        self.assertAlmostEqual(lo,0.314274,places=5)
        self.assertAlmostEqual(hi,0.685726,places=5)
        zero=starter.wilson_interval(0,24)
        perfect=starter.wilson_interval(24,24)
        self.assertAlmostEqual(zero[0],0)
        self.assertAlmostEqual(zero[1],0.137976,places=5)
        self.assertAlmostEqual(perfect[0],1-zero[1])
        self.assertAlmostEqual(perfect[1],1)
        for correct,n in [(0,0),(-1,24),(25,24)]:
            with self.assertRaises(ValueError):starter.wilson_interval(correct,n)

    def test_analysis_reports_uncertainty_without_dropping_failures(self):
        rows=[]
        for arm in ['direct','followup']:
            for k in range(4):
                raw='Answer: blue' if arm=='followup' or k==0 else 'unfinished'
                finish='length' if arm=='direct' and k==3 else 'stop'
                parsed=starter.parse_output(raw,False,finish)
                rows.append(dict(id=f'{k}-{arm}',item_id=str(k),arm=arm,difficulty=1,
                    gold='blue',raw=raw,thinking=False,finish_reason=finish,
                    correct=parsed['answer']=='blue',output_tokens=5,**parsed))
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'results.jsonl'
            path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
            with contextlib.redirect_stdout(io.StringIO()):
                starter.analyze(path,Path(tmp)/'analysis')
            summary=json.loads((Path(tmp)/'analysis/summary.json').read_text())
            direct=summary['counts']['direct']['1']
            self.assertEqual((direct['n'],direct['correct'],direct['valid'],direct['truncated']),(4,1,1,1))
            self.assertLess(direct['wilson_95'][0],.25)
            self.assertGreater(direct['wilson_95'][1],.25)
            self.assertLess(summary['counts']['followup']['1']['wilson_95'][0],1)
            self.assertEqual(summary['paired_contrasts']['followup minus direct']['delta'],.75)
            markdown=(Path(tmp)/'analysis/SUMMARY.md').read_text()
            self.assertIn('1/4',markdown)
            self.assertIn('followup minus direct',markdown)

if __name__=='__main__':unittest.main()
