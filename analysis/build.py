"""Run the HR attrition analysis and write the website to site/index.html.

    python -m analysis.build
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import data, drivers
from .report import AXIS, BLUE, GRID, INK_2, MUTED, ORANGE, SERIES, Report, money, style, to_json

REPO = "Scarface96/HR-Analysis-Dashboard"
GREY = "#b9b8b1"


def bar_ci(fig, t, x, row=None, col=None, color=BLUE, name=None, showlegend=False):
    kw = dict(row=row, col=col) if row else {}
    fig.add_bar(
        x=t[x].astype(str), y=t["rate"], marker_color=color, name=name, showlegend=showlegend,
        error_y=dict(type="data", symmetric=False, array=t["high"] - t["rate"], arrayminus=t["rate"] - t["low"], color=MUTED, thickness=1.2, width=3),
        customdata=np.stack([t["left"], t["employees"], t["low"], t["high"]], axis=1),
        hovertemplate="%{x}<br>%{y:.0%} left (%{customdata[0]} of %{customdata[1]})<br>95% range %{customdata[2]:.0%}–%{customdata[3]:.0%}<extra>" + (name or "") + "</extra>",
        **kw,
    )


def segments_figure(df, overall):
    panels = [("Department", "Department"), ("Age", "age_band"), ("Overtime", "Over Time"), ("Business travel", "travel")]
    fig = make_subplots(rows=1, cols=4, subplot_titles=[p[0] for p in panels], shared_yaxes=True, horizontal_spacing=0.04)
    out = []
    for i, (title, col) in enumerate(panels, 1):
        t = data.rates(df, col)
        if col == "travel":
            t = t.set_index("travel").loc[["Never", "Rarely", "Frequently"]].reset_index()
        bar_ci(fig, t, col, 1, i)
        fig.add_hline(y=overall, line=dict(color=MUTED, width=1, dash="dot"), row=1, col=i)
        out.append(t.rename(columns={col: "group"}).assign(factor=title))
    style(fig, height=380)
    fig.update_annotations(font=dict(size=14, color=INK_2))
    fig.update_yaxes(tickformat=".0%", rangemode="tozero")
    fig.update_xaxes(tickfont=dict(size=11))
    t = pd.concat(out)[["factor", "group", "employees", "left", "rate"]]
    t["rate"] = (t["rate"] * 100).round(1)
    return fig, t.rename(columns={"rate": "attrition %"})


def overtime_figure(df):
    t = data.rates(df, ["Job Level", "Over Time"])
    fig = go.Figure()
    for ot, color, name in [("No", BLUE, "No overtime"), ("Yes", ORANGE, "Works overtime")]:
        g = t[t["Over Time"] == ot]
        bar_ci(fig, g.assign(level="Level " + g["Job Level"].astype(str)), "level", color=color, name=name, showlegend=True)
    style(fig, height=400)
    fig.update_layout(barmode="group")
    fig.update_yaxes(tickformat=".0%", title="Share who left")
    fig.update_xaxes(title="Job level (1 = entry level, 5 = most senior)")
    t["rate"] = (t["rate"] * 100).round(1)
    return fig, t[["Job Level", "Over Time", "employees", "left", "rate"]].rename(columns={"rate": "attrition %"})


def drivers_figure(t):
    colors = [ORANGE if (s and o > 1) else BLUE if s else GREY for s, o in zip(t["significant"], t["odds_ratio"])]
    fig = go.Figure(go.Scatter(
        x=t["odds_ratio"], y=t["label"], mode="markers",
        marker=dict(color=colors, size=11, line=dict(color="#fcfcfb", width=2)),
        error_x=dict(type="data", symmetric=False, array=t["high"] - t["odds_ratio"], arrayminus=t["odds_ratio"] - t["low"], color=MUTED, thickness=1.5, width=0),
        customdata=np.stack([t["low"], t["high"], t["p_value"]], axis=1),
        hovertemplate="%{y}<br>Odds of leaving ×%{x:.2f}<br>95% range ×%{customdata[0]:.2f} to ×%{customdata[1]:.2f}<extra></extra>",
    ))
    fig.add_vline(x=1, line=dict(color=AXIS, width=1.5))
    style(fig, height=560, legend=False)
    fig.update_xaxes(type="log", tickvals=[0.5, 0.75, 1, 1.5, 2, 3, 5, 8], ticktext=["×0.5", "×0.75", "×1", "×1.5", "×2", "×3", "×5", "×8"],
                     showgrid=True, gridcolor=GRID, title="Change in the odds of leaving, other factors held equal")
    fig.update_yaxes(showgrid=False, tickfont=dict(size=12))
    return fig


def tenure_figure(df, overall):
    t = data.rates(df, "tenure_band")
    fig = go.Figure()
    bar_ci(fig, t, "tenure_band")
    fig.add_hline(y=overall, line=dict(color=MUTED, width=1, dash="dot"), annotation_text=f"Company {overall:.0%}", annotation_position="top right", annotation_font_color=MUTED)
    style(fig, height=340)
    fig.update_yaxes(tickformat=".0%")
    fig.update_xaxes(title="Time at the company")
    return fig, t


def satisfaction_figure(df, overall):
    panels = [("Job satisfaction", "Job Satisfaction"), ("Environment satisfaction", "Environment Satisfaction"), ("Work-life balance", "Work Life Balance")]
    fig = make_subplots(rows=1, cols=3, subplot_titles=[p[0] for p in panels], shared_yaxes=True, horizontal_spacing=0.05)
    for i, (_, col) in enumerate(panels, 1):
        t = data.rates(df, col)
        t["level"] = t[col].map(data.SATISFACTION)
        bar_ci(fig, t, "level", 1, i)
        fig.add_hline(y=overall, line=dict(color=MUTED, width=1, dash="dot"), row=1, col=i)
    style(fig, height=340)
    fig.update_annotations(font=dict(size=14, color=INK_2))
    fig.update_yaxes(tickformat=".0%", rangemode="tozero")
    return fig


EXPLORER = """
<form class="controls" id="seg" onsubmit="return false">
  <label>Department<select name="d"><option value="">All</option></select></label>
  <label>Overtime<select name="o"><option value="">All</option></select></label>
  <label>Job level<select name="l"><option value="">All</option></select></label>
  <label>Age<select name="a"><option value="">All</option></select></label>
  <label>Travel<select name="t"><option value="">All</option></select></label>
  <label>Stock options<select name="s"><option value="">All</option><option value="0">None</option><option value="1">Some</option></select></label>
</form>
<div class="readout" aria-live="polite">
  <div><b id="seg-n">–</b><span>employees in this group</span></div>
  <div><b id="seg-rate">–</b><span id="seg-rate-l">have left</span></div>
  <div><b id="seg-ci">–</b><span>likely true range (95%)</span></div>
  <div><b id="seg-vs">–</b><span>vs the company</span></div>
</div>
<figure class="chart"><div id="seg-roles" style="height:340px"></div></figure>
"""


def explorer_js(df: pd.DataFrame, overall: float) -> str:
    rows = df.assign(level=df["Job Level"].astype(str), stock=(df["Stock Option Level"] > 0).astype(int).astype(str), age=df["age_band"].astype(str))[
        ["Department", "Over Time", "level", "age", "travel", "stock", "Job Role", "left"]].values.tolist()
    return f"""
(function(){{
const R={to_json(rows)}, AVG={overall};
const COL={{d:0,o:1,l:2,a:3,t:4,s:5}};
const f=document.getElementById('seg');
const order={{a:{to_json(data.AGE_ORDER)},t:['Never','Rarely','Frequently']}};
for(const [k,i] of Object.entries(COL)){{ if(k==='s') continue;
  const vals=order[k]||[...new Set(R.map(r=>r[i]))].sort();
  vals.forEach(v=>f.elements[k].add(new Option(k==='l'?'Level '+v:v,v)));
}}
function wilson(k,n){{const z=1.96,p=k/n,d=1+z*z/n,c=(p+z*z/(2*n))/d,h=z*Math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return [c-h,c+h];}}
const pct=v=>(v*100).toFixed(0)+'%';
function run(){{
  const sel=Object.entries(COL).filter(([k])=>f.elements[k].value!=='').map(([k,i])=>[i,f.elements[k].value]);
  const g=R.filter(r=>sel.every(([i,v])=>r[i]===v));
  const n=g.length, k=g.reduce((s,r)=>s+r[7],0);
  document.getElementById('seg-n').textContent=n.toLocaleString();
  if(!n){{['seg-rate','seg-ci','seg-vs'].forEach(id=>document.getElementById(id).textContent='–'); Plotly.purge('seg-roles'); return;}}
  const [lo,hi]=wilson(k,n), p=k/n;
  document.getElementById('seg-rate').textContent=pct(p);
  document.getElementById('seg-rate-l').textContent='have left ('+k+' people)';
  document.getElementById('seg-ci').textContent=pct(lo)+'–'+pct(hi);
  document.getElementById('seg-vs').textContent=lo>AVG?'Higher':hi<AVG?'Lower':'Similar';
  const roles={{}}; g.forEach(r=>{{(roles[r[6]]=roles[r[6]]||[0,0]); roles[r[6]][0]++; roles[r[6]][1]+=r[7];}});
  const rs=Object.entries(roles).filter(([,v])=>v[0]>=5).map(([name,[n,k]])=>({{name,n,k,p:k/n}})).sort((a,b)=>a.p-b.p);
  Plotly.react('seg-roles',[{{type:'bar',orientation:'h',y:rs.map(r=>r.name),x:rs.map(r=>r.p),marker:{{color:'{BLUE}'}},
     customdata:rs.map(r=>[r.k,r.n]),hovertemplate:'%{{y}}<br>%{{x:.0%}} left (%{{customdata[0]}} of %{{customdata[1]}})<extra></extra>'}}],
    {{height:340,margin:{{l:8,r:16,t:28,b:8}},paper_bgcolor:'#fcfcfb',plot_bgcolor:'#fcfcfb',font:{{family:'"Public Sans",system-ui,sans-serif',size:13,color:'{INK_2}'}},
     title:{{text:'Attrition by job role in this group (roles with 5+ people)',font:{{size:14}},x:0,xanchor:'left'}},
     xaxis:{{tickformat:'.0%',gridcolor:'{GRID}',rangemode:'tozero',automargin:true}},yaxis:{{automargin:true}},
     shapes:[{{type:'line',x0:AVG,x1:AVG,y0:0,y1:1,yref:'paper',line:{{color:'{MUTED}',dash:'dot',width:1}}}}]}},{{displaylogo:false,responsive:true}});
}}
f.addEventListener('input',run); run();
}})();
"""


def main(out="site/index.html"):
    df = data.load()
    overall = df["left"].mean()
    ors = drivers.odds_ratios(df)
    auc = drivers.cv_auc(df)
    cost = data.replacement_cost(df)
    ot = data.rates(df, ["Job Level", "Over Time"]).set_index(["Job Level", "Over Time"])
    hot = ot.loc[(1, "Yes")]
    o = ors.set_index("feature")
    seg_fig, seg_t = segments_figure(df, overall)
    ot_fig, ot_t = overtime_figure(df)
    ten_fig, ten = tenure_figure(df, overall)
    ten = ten.set_index("tenure_band")
    early = df[df["Years At Company"] <= 2]
    inc = data.rates(df, "income_band").set_index("income_band")

    r = Report(
        title=f"Half of entry-level employees who work overtime have left",
        project="HR Attrition Analysis",
        summary=(
            f"{int(df['left'].sum())} of {len(df):,} employees ({overall:.0%}) have left. Overtime and junior roles are the two strongest "
            f"signals, and together they're explosive: {hot['rate']:.0%} of level-1 staff working overtime are gone. Several factors that "
            "look risky on their own, like being single or lower pay, fade once these are taken into account."
        ),
        repo=REPO,
        accent=SERIES[4],
        source="HR Data.xlsx: 1,470 employees with 39 attributes covering role, pay, tenure, satisfaction and whether they left (the IBM HR analytics sample).",
        method=(
            "pandas for preparation; attrition rates carry 95% Wilson confidence ranges. The drivers model is a statsmodels logistic "
            f"regression on 14 factors, reported as odds ratios; the same factors rank leavers with a cross-validated ROC AUC of {auc:.2f} "
            "in scikit-learn. Replacement cost assumes half a year's salary per leaver, a cautious middle of published estimates."
        ),
    )
    r.kpis([
        (f"{overall:.0%}", "attrition", f"{int(df['left'].sum())} of {len(df):,} employees"),
        (f"{hot['rate']:.0%}", "entry-level staff on overtime who left"),
        (f"{early['left'].mean():.0%}", "attrition among staff with two years or less", f"{early['left'].sum() / df['left'].sum():.0%} of all leavers"),
        (money(cost), "estimated replacement cost", "at half a year's salary each"),
    ])

    r.section(
        "Who leaves?",
        "<p>Attrition is far from even. <b>Overtime triples it</b> (31% vs 10%). Under-25s leave at 39%, and frequent travellers at 25%. "
        "R&amp;D is the steadiest department. Whiskers show each group's likely range, so small groups with wide whiskers deserve caution.</p>",
        fig=seg_fig, table=seg_t, note="Dotted line: company average.",
    )
    r.section(
        "Overtime hits junior staff hardest",
        f"<p>Split by seniority, overtime matters most at the bottom: <b>{hot['rate']:.0%} of entry-level employees who work overtime have left</b> "
        f"({int(hot['left'])} of {int(hot['employees'])}), against {ot.loc[(1, 'No'), 'rate']:.0%} of their peers without overtime. "
        "For the 156 people in that group, workload is the obvious first lever.</p>",
        fig=ot_fig, table=ot_t,
    )
    r.section(
        "Which factors still matter when everything else is equal?",
        f"<p>Many risk factors overlap: young employees are more often junior, single, lower paid and without stock options. "
        f"A logistic regression separates them. <b>Overtime multiplies the odds of leaving by {o.loc['overtime', 'odds_ratio']:.1f}</b>, "
        f"an entry-level role by {o.loc['job_level_1', 'odds_ratio']:.1f}, poor work-life balance by {o.loc['poor_balance', 'odds_ratio']:.1f}, "
        f"and having no stock options by {o.loc['no_stock', 'odds_ratio']:.1f}.</p>"
        "<p>Two popular explanations drop out. Being single and monthly income are no longer significant once role level and stock "
        "options are accounted for, so a pay rise alone is unlikely to fix attrition.</p>",
        fig=drivers_figure(ors),
        table=ors.assign(odds_ratio=ors["odds_ratio"].round(2), low=ors["low"].round(2), high=ors["high"].round(2), p_value=ors["p_value"].round(4))[["label", "odds_ratio", "low", "high", "p_value"]].iloc[::-1]
        .rename(columns={"label": "factor", "odds_ratio": "odds ratio", "low": "95% low", "high": "95% high", "p_value": "p-value"}),
        note=f"Orange: raises the odds of leaving. Blue: lowers them. Grey: not distinguishable from no effect. Pseudo R² {ors.attrs['pseudo_r2']:.2f}; cross-validated ROC AUC {auc:.2f}.",
    )
    ten_t = ten.reset_index()
    ten_t["rate"] = (ten_t["rate"] * 100).round(1)
    r.section(
        "When do people leave?",
        f"<p>Early. <b>{ten.loc['Under 1 year', 'rate']:.0%} of people in their first year</b> and {ten.loc['1–2 years', 'rate']:.0%} in years one to two "
        f"have left, compared with {ten.loc['Over 10 years', 'rate']:.0%} after ten years. Employees with two years or less make up "
        f"{len(early) / len(df):.0%} of the workforce but {early['left'].sum() / df['left'].sum():.0%} of leavers, which points to onboarding and early career support.</p>",
        fig=ten_fig, table=ten_t[["tenure_band", "employees", "left", "rate"]].rename(columns={"tenure_band": "time at company", "rate": "attrition %"}),
    )
    r.section(
        "Does satisfaction show up in who leaves?",
        f"<p>Yes, at the low end. Employees rating their work-life balance as low leave at {data.rates(df, 'Work Life Balance').set_index('Work Life Balance').loc[1, 'rate']:.0%}, "
        f"and those with low environment satisfaction at {data.rates(df, 'Environment Satisfaction').set_index('Environment Satisfaction').loc[1, 'rate']:.0%}. "
        "Above the lowest rating the differences shrink, so surveys are most useful for spotting the unhappiest group early.</p>",
        fig=satisfaction_figure(df, overall),
        note=f"Pay follows the same pattern: the lowest-paid quarter leaves at {inc.loc['Lowest 25%', 'rate']:.0%}, the other three at {inc.loc['Top 25%', 'rate']:.0%}–{inc.loc['Second 25%', 'rate']:.0%}, but that gap mostly reflects seniority.",
    )
    r.section(
        "Explore any group",
        "<p>Combine filters to see how many people are in a group, how many have left, and whether that's genuinely different from the "
        "company average once group size is taken into account. The chart breaks the group down by job role.</p>",
        html=EXPLORER,
    )
    r.script(explorer_js(df, overall))

    path = r.write(out)
    print(f"Wrote {path} ({path.stat().st_size / 1024:.0f} KB). CV AUC {auc:.3f}.")
    return r


if __name__ == "__main__":
    main()
