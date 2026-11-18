"""Run: python test_v2.py; no Streamlit dependency needed for data-layer tests."""
from pathlib import Path
import ast, io, zipfile
import pandas as pd
from v2_data import load_sheet, validate, filter_rows, export_excel, WORKBOOK

assert not validate(),validate()
for name in ('app.py','v2_data.py','v2_pages.py','esg_v01_backend.py','esg_batch_pilot.py'):
    ast.parse(Path(name).read_text(encoding='utf-8'))
print('PASS Python syntax 5 files')
scores=load_sheet('scores')
assert len(scores)==12 and scores['企业'].nunique()==3
assert all(scores['有效分母'].astype(float)==100)
print('PASS exact 12 expected scores / effective denominator')
evidence=load_sheet('evidence')
assert len(evidence)==30 and evidence['pdf_page'].notna().all()
assert evidence['excerpt'].notna().all()
assert evidence['sha256'].astype(str).str.len().eq(64).all()
assert len(filter_rows(evidence,{'company':['上汽集团']}))>0
assert len(filter_rows(evidence,{},'CN14-24B'))>0
assert filter_rows(evidence,{},'NO_SUCH_EVIDENCE_ABCDEFGHIJKLMNOPQRSTUVWXYZ').empty
print('PASS evidence search, report page / excerpts / SHA256')
case=load_sheet('cross'); assert len(case)==12
assert set(case['整项一致性计分'].dropna().astype(str).str[:1])=={'否'}
assert case['有限事实状态'].notna().all()
assert len(load_sheet('timeline'))==4
print('PASS cross-report limited facts / zero full comparable claims')
sens=load_sheet('sensitivity');assert len(sens)==54
assert {'基准分','情景分','变化'}.issubset(sens.columns)
print('PASS 54 sensitivity scenarios')
for name,key in [('scores','scores'),('evidence','evidence'),('cross','cross'),('sensitivity','sensitivity')]:
    frame=load_sheet(key)
    content=export_excel({name:frame})
    assert zipfile.is_zipfile(io.BytesIO(content))
    restored=pd.read_excel(io.BytesIO(content))
    assert len(restored)==len(frame)
    print('PASS Excel export',name,len(frame))
assert zipfile.is_zipfile(WORKBOOK)
assert Path('已核实样本_15条.xlsx').exists()
source=Path('app.py').read_text()
assert 'view = st.sidebar.radio' in source and 'render_2025()' in source
assert '载入15条保存样本' in source and 'process_files(' in source
assert not any(x in Path('v2_pages.py').read_text() for x in ('企业综合分','一致性百分比 =','企业总排名'))
print('PASS V1 historical entry/code maintained, forbidden aggregate calculation absent')
print('PASS V2 data and integration tests')
