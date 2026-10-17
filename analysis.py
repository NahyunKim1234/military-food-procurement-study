"""Reproduce the exploratory paper from the included curated tables.
Run: python analysis.py. No API key or network access is required.
"""
import csv
import json
import math
from collections import Counter
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_UP
from pathlib import Path
import numpy as np
from scipy.stats import rankdata, spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
def read(name):
    with (ROOT/'data'/name).open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))
def corr(x,y):return float(spearmanr(x,y).statistic)
def partial(events,metric):
    # Rank-residual method; association only, not a causal estimator.
    z=np.column_stack([np.ones(len(events)),[e['agency']=='HCM' for e in events],
       [e['agency']=='MCS' for e in events],[e['floor']==87.995 for e in events],
       rankdata([e['base'] for e in events]),[e['year']=='2025' for e in events]])
    a=rankdata([e['n'] for e in events]);b=rankdata([e[metric] for e in events])
    a=a-z@np.linalg.lstsq(z,a,rcond=None)[0]
    b=b-z@np.linalg.lstsq(z,b,rcond=None)[0]
    return float(np.corrcoef(a,b)[0,1])

def main():
    tenders=read('tenders.csv');bids=read('bids.csv')
    assert len(tenders)==35 and len(bids)==5458
    assert len({t['event_id'] for t in tenders})==35
    assert len({b['bidder_id'] for b in bids})==845
    by_event={t['event_id']:[] for t in tenders}
    for b in bids:
        assert b['event_id'] in by_event
        by_event[b['event_id']].append(b)
    events=[]
    for t in tenders:
        rows=by_event[t['event_id']]
        assert len(rows)==int(t['record_count'])
        assert len({b['bidder_id'] for b in rows})==len(rows)
        p=Decimal(t['selected_price_mean_before_rounding_krw']).to_integral_value(rounding=ROUND_FLOOR)
        floor=Decimal(t['award_floor_pct'])
        gaps=np.array([float(Decimal(b['amount_krw'])/p*100-floor) for b in rows])
        kept=np.array([b['ranked_nonexcluded']=='1' for b in rows])
        awarded=[b for b in rows if b['awarded']=='1']
        assert len(awarded)==1
        assert Decimal(awarded[0]['amount_krw'])==Decimal(t['award_amount_krw'])
        assert np.any(kept)
        q1,q3=np.quantile(gaps,[.25,.75],method='linear')
        award=float(Decimal(t['award_amount_krw'])/p*100-floor)
        minimum_amount=min(Decimal(b['amount_krw']) for b in rows if b['ranked_nonexcluded']=='1')
        noninvalid=[g for b,g in zip(rows,gaps) if b['status']!='invalid']
        events.append({'event_id':t['event_id'],'announcement_id':t['announcement_id'],
          'agency':t['agency'],'year':t['opening_date'][:4],'floor':float(floor),
          'base':float(t['base_amount_krw']),'n':len(rows),'n_ranked':int(sum(kept)),
          'award_gap':award,'median_all':float(np.median(gaps)),
          'median_noninvalid':float(np.median(noninvalid)),
          'median_ranked':float(np.median(gaps[kept])), 'minimum_ranked':float(min(gaps[kept])),
          'q25_all':float(q1),'q75_all':float(q3),'iqr_all':float(q3-q1),
          'award_is_minimum_ranked':Decimal(t['award_amount_krw'])==minimum_amount,
          'selection_difference_krw':int(Decimal(t['award_amount_krw'])-minimum_amount),
          'ranked_gaps':gaps[kept].tolist()})
    metrics={}
    for metric in ['award_gap','minimum_ranked','median_all','median_noninvalid','median_ranked','q25_all','q75_all','iqr_all']:
        metrics[metric]={'spearman':corr([e['n'] for e in events],[e[metric] for e in events]),
                         'partial_rank':partial(events,metric)}
    low=[e for e in events if e['n']<20];high=[e for e in events if e['n']>=20]
    groups={'below_20':{'count':len(low),'median_award_gap':float(np.median([e['award_gap'] for e in low]))},
            'at_least_20':{'count':len(high),'median_award_gap':float(np.median([e['award_gap'] for e in high]))}}
    subsets=[]
    for m in [2,5,10]:
        sample=[e for e in events if e['n_ranked']>=m]
        expected=[]
        for e in sample:
            values=sorted(e['ranked_gaps']);N=len(values)
            expectation=sum(values[j]*math.comb(N-j-1,m-1)/math.comb(N,m) for j in range(N-m+1))
            expected.append(expectation)
        subsets.append({'m':m,'tenders':len(sample),
          'actual_award_rho_vs_ranked_count':corr([e['n_ranked'] for e in sample],[e['award_gap'] for e in sample]),
          'expected_minimum_rho_vs_ranked_count':corr([e['n_ranked'] for e in sample],expected)})
    same=[e for e in events if e['award_is_minimum_ranked']]
    loo=[corr([e['n'] for j,e in enumerate(events) if j!=i],
              [e['award_gap'] for j,e in enumerate(events) if j!=i]) for i in range(len(events))]
    rounding={}
    for label,mode in [('unrounded',None),('floor',ROUND_FLOOR),('ceiling',ROUND_CEILING),('nearest',ROUND_HALF_UP)]:
        values=[]
        for t in tenders:
            p=Decimal(t['selected_price_mean_before_rounding_krw'])
            if mode:p=p.to_integral_value(rounding=mode)
            values.append(float(Decimal(t['award_amount_krw'])/p*100-Decimal(t['award_floor_pct'])))
        rounding[label]=corr([e['n'] for e in events],values)
    summary={'sample':{'tenders':len(tenders),'bid_records':len(bids),'unique_bidder_labels':845,
         'opening_years':dict(Counter(e['year'] for e in events)),
         'agencies':dict(Counter(e['agency'] for e in events)),
         'status_counts':dict(Counter(b['status'] for b in bids)),
         'ranked_nonexcluded_records':sum(e['n_ranked'] for e in events)},
       'metrics':metrics,'descriptive_threshold_groups':groups,'fixed_subset_diagnostics':subsets,
       'award_equals_minimum_subset':{'tenders':len(same),
          'spearman':corr([e['n'] for e in same],[e['award_gap'] for e in same]),
          'partial_rank':partial(same,'award_gap')},
       'leave_one_out_rho_range':[min(loo),max(loo)],'rounding_rho':rounding,
       'selection_cases':[{k:v for k,v in e.items() if k!='ranked_gaps'} for e in events if not e['award_is_minimum_ranked']]}
    assert math.isclose(metrics['award_gap']['spearman'],-0.7088005597841261,abs_tol=1e-12)
    assert math.isclose(metrics['median_all']['partial_rank'],-0.1523426950669912,abs_tol=1e-12)
    assert len(same)==30 and summary['sample']['ranked_nonexcluded_records']==2853
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    public_events=[{k:v for k,v in e.items() if k!='ranked_gaps'} for e in events]
    with (ROOT/'results/tender_metrics.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(public_events[0]));w.writeheader();w.writerows(public_events)
    plot(events)
    print('Verified: 35 tenders, 5,458 bids, 845 bidder labels. Results and figures reproduced.')
    print(json.dumps(metrics,indent=2))

def plot(events):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,
       'axes.spines.right':False,'axes.labelcolor':'#283848','text.color':'#172735',
       'xtick.color':'#45535e','ytick.color':'#45535e','savefig.dpi':220})
    colors={'SCP':'#246b8e','HCM':'#d38b31','MCS':'#748455'}
    fig,axes=plt.subplots(1,2,figsize=(7.2,2.7))
    for ag,color in colors.items():
        es=[e for e in events if e['agency']==ag]
        for ax,metric in zip(axes,['award_gap','median_all']):
            ax.scatter([e['n'] for e in es],[e[metric] for e in es],s=31,color=color,
               alpha=.85,edgecolors='white',linewidth=.5,label=ag)
            ax.set_xscale('log');ax.set_xticks([2,10,100,400],['2','10','100','400'])
            ax.grid(True,alpha=.15);ax.set_axisbelow(True)
            ax.set_xlabel('Participating firms (log scale)')
    axes[0].set_yscale('log');axes[0].set_title('A. Award price',loc='left',fontweight='bold')
    axes[0].set_ylabel('Above award floor (pp; log scale)')
    axes[1].set_title('B. Median submitted bid',loc='left',fontweight='bold')
    axes[1].set_ylabel('Relative to award floor (pp)')
    axes[1].axhline(0,color='#7b8994',lw=.8,ls='--')
    handles,labels=axes[1].get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper center',ncol=3,frameon=False,bbox_to_anchor=(.55,1.02))
    fig.tight_layout(rect=(0,0,1,.95))
    (ROOT/'figures').mkdir(exist_ok=True)
    fig.savefig(ROOT/'figures/participation_prices.png',bbox_inches='tight')
    plt.close(fig)

if __name__=='__main__':main()
