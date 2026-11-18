"""Read-only 2025 V6 research workbook access. No scores or evidence are synthesized."""
from __future__ import annotations
from pathlib import Path
from io import BytesIO
import pandas as pd

ROOT = Path(__file__).resolve().parent
WORKBOOK = ROOT / 'data_2025' / '三企业V6双报告与评分收尾核验.xlsx'
SHEETS = {
    'scores':'V6限定评分摘要', 'detail':'证据及评分12项',
    'evidence':'原页证据30条', 'judgment':'人工判断输入12条',
    'rules':'评分公开规则', 'audit':'V6逐要件审查60项',
    'cross':'双报告有限案例', 'timeline':'长城治理人数时间线',
    'sensitivity':'评分敏感性收尾', 'sensitivity_old':'敏感性情景',
    'sources':'六份正式报告来源', 'dictionary':'17项原词典',
    'coverage':'51项历史核验', 'pending':'尚未完整评分',
    'limits':'复核结论与定稿门槛',
}
REQUIRED = ('scores','detail','evidence','judgment','rules','audit','cross','timeline','sensitivity','sources')

def load_sheet(name: str, workbook: Path | None = None) -> pd.DataFrame:
    if name not in SHEETS:
        raise ValueError('Unknown research worksheet')
    target = workbook or WORKBOOK
    if not target.is_file():
        raise FileNotFoundError(f'正式研究工作簿缺失：{target.name}。请确认 data_2025 文件夹已上传。')
    result = pd.read_excel(target, sheet_name=SHEETS[name], engine='openpyxl', dtype=object)
    result = result.dropna(how='all').reset_index(drop=True)
    return result

def validate(workbook: Path | None = None):
    from math import isclose
    issues=[]
    dfs={}
    for key in REQUIRED:
        try: dfs[key]=load_sheet(key,workbook)
        except Exception as exc: issues.append(f'{key}: {exc}')
    if issues: return issues
    expected={
        '上汽集团':{'CN14-24B':100,'CN14-24C':100,'CN14-50':92.5,'CN14-12':82.5},
        '广汽集团':{'CN14-24B':92.5,'CN14-24C':92.5,'CN14-50':92.5,'CN14-12':92.5},
        '长城汽车':{'CN14-24B':100,'CN14-24C':100,'CN14-50':92.5,'CN14-12':92.5}}
    scores=dfs['scores'];detail=dfs['detail'];audit=dfs['audit'];ev=dfs['evidence']
    if len(scores)!=12: issues.append(f'评分摘要不是12行：{len(scores)}')
    if len(detail)!=12: issues.append(f'评分详情不是12行：{len(detail)}')
    if len(ev)!=30: issues.append(f'原页证据不是30行：{len(ev)}')
    if len(dfs['judgment'])!=12: issues.append('人工判断不是12行')
    if len(audit)!=60: issues.append(f'逐要件审查不是60行：{len(audit)}')
    if len(dfs['sensitivity'])!=54: issues.append(f'收尾敏感性情景不是54行：{len(dfs["sensitivity"])}')
    if len(dfs['sources'])!=6: issues.append('报告来源不是6行')
    if (dfs['cross']['整项一致性计分'].astype(str).str.contains('是：',regex=False)).any(): issues.append('发现疑似完整一致性计分')
    for company, items in expected.items():
        for indicator, value in items.items():
            a=scores[(scores['企业']==company)&(scores['指标编号']==indicator)]
            b=detail[(detail['企业']==company)&(detail['指标编号']==indicator)]
            if len(a)!=1 or len(b)!=1: issues.append(f'缺失/重复评分 {company} {indicator}');continue
            for df,col in ((a,'限定细项得分'),(b,'限定细项得分')):
                if not isclose(float(df.iloc[0][col]),value,abs_tol=1e-6):issues.append(f'分数不符 {company} {indicator}: {col}')
    evidence_ids=set(ev['id'].dropna().astype(str))
    for _, row in audit.iterrows():
        ids=str(row.get('证据ID') or '').replace('、',',').replace('；',',').replace(';',',').split(',')
        for evid in ids:
            if evid.strip() and evid.strip() not in evidence_ids:
                issues.append(f'审查证据ID无法定位 {evid.strip()}')
    return issues

def filter_rows(frame:pd.DataFrame,filters:dict[str,list[str]]|None=None, query:str='')->pd.DataFrame:
    df=frame.copy()
    for key, values in (filters or {}).items():
        if key in df.columns and values: df=df.loc[df[key].astype(str).isin(values)]
    if query.strip():
        mask=df.astype(str).replace('nan','').apply(lambda col:col.str.contains(query.strip(),case=False,regex=False)).any(axis=1)
        df=df.loc[mask]
    return df

def export_excel(frames:dict[str,pd.DataFrame])->bytes:
    data=BytesIO()
    with pd.ExcelWriter(data,engine='openpyxl') as writer:
        for name,frame in frames.items():frame.to_excel(writer,sheet_name=name[:31],index=False)
    return data.getvalue()
