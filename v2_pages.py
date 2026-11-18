"""2025 research UI. Preserves V1 unmodified in separate navigation."""
import json
import pandas as pd
import streamlit as st
from pathlib import Path
from v2_data import WORKBOOK, load_sheet, validate, filter_rows, export_excel

LABELS={'CN14-24B':'范围1温室气体排放','CN14-24C':'范围2温室气体排放','CN14-50':'员工人数研究子维度','CN14-12':'治理机构研究子维度'}

def grid(df, height=380):
    if df.empty: st.info('当前筛选条件下没有记录。')
    else: st.dataframe(df,hide_index=True,use_container_width=True,height=height)

def selectors(df, prefix, keys=('企业','指标编号')):
    chosen={}
    cols=st.columns(len(keys))
    for i,k in enumerate(keys):
        if k in df.columns:
            options=sorted(df[k].dropna().astype(str).unique().tolist())
            chosen[k]=cols[i].multiselect(k,options,key=f'{prefix}_{k}')
    return chosen

def dump(label, key, frame, filename):
    st.download_button(label,export_excel({key:frame}),filename,
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',key=filename)

def show_score_detail(company,indicator):
    detail=load_sheet('detail'); audit=load_sheet('audit'); evidence=load_sheet('evidence')
    selected=detail[(detail['企业']==company)&(detail['指标编号']==indicator)]
    if selected.empty:st.error('本项评分详情缺失，无法展示评分依据。');return
    r=selected.iloc[0]
    st.markdown(f'**{company} · {LABELS.get(indicator,indicator)} · {float(r["限定细项得分"]):g} / {float(r["有效分母"]):g}**')
    for field in ('研究范围','正式条款范围','核验判断','统计边界','原页','未评分要件','评分状态'):
        val=r.get(field)
        if pd.notna(val):st.write(f'**{field}：** {val}')
    audit_items=audit[(audit['企业']==company)&(audit['指标编号']==indicator)]
    st.markdown('**逐要件评分、权重和原页摘录**')
    grid(audit_items[['评分要件','要件操作定义','权重','人工判断','折算得分','证据页码','证据ID','核验摘录','复核结论']],340)
    ids=set()
    for val in audit_items['证据ID'].fillna(''):
        ids.update(x.strip() for x in str(val).replace('、',',').replace('；',',').replace(';',',').split(',') if x.strip())
    ev=evidence[evidence['id'].astype(str).isin(ids)]
    st.markdown('**报告原文证据（摘录，不是PDF页面链接）**')
    grid(ev[['id','file','sha256','pdf_page','excerpt','status','evidence_audit']],280)
    st.caption('证据文本、页码和哈希均直接来自 V6 工作簿；网页未托管原始 PDF。')

def render():
    st.markdown('##### 2025 · 中国汽车企业双报告研究 / V2.0')
    st.title('ESG Intelligence Lab · 正式研究')
    st.caption('上汽集团 · 广汽集团 · 长城汽车｜独立于2023年奔驰、宝马、大众历史样本｜限定研究细项评分，不是企业综合ESG评级')
    if not WORKBOOK.exists():
        st.error(f'2025年正式工作簿未找到：{WORKBOOK.name}。请将 data_2025 目录连同代码上传。')
        st.stop()
    try: problems=validate()
    except Exception as e:st.error(f'数据读取失败：{e}');st.stop()
    if problems:
        st.error('V6工作簿完整性检查未通过，暂不展示可能误导的评分。')
        with st.expander('查看具体错误'):st.write(problems[:30])
        st.stop()
    pages=['项目总览','E/S/G限定评分','原始证据追溯','双报告交叉验证','敏感性分析','研究数据导出','研究局限']
    page=st.radio('2025研究页面',pages,horizontal=True,label_visibility='collapsed')
    if page=='项目总览':
        st.markdown('以**上海证券交易所《上市公司自律监管指引第14号——可持续发展报告（试行）》**为研究参照，对三家汽车企业2025年年报和可持续发展报告开展双报告交叉验证。研究指标编号为教学研究自定义编号，不代表交易所官方指标编号。')
        cols=st.columns(5)
        for c,(label,val) in zip(cols,[('样本企业','3 家'),('正式报告','6 份'),('研究指标','17 项'),('企业×指标','51 位'),('限定评分','12 项')]):c.metric(label,val)
        st.info('完整同口径双报告比较项目数：0。不得据此计算一致性百分比；未检索到不代表企业未披露。')
        report = Path(__file__).resolve().parent/'research_docs'/'2025中国汽车企业双报告研究_正式报告.pdf'
        if report.exists():
            st.download_button('下载2025年正式研究报告 PDF',report.read_bytes(),file_name=report.name,mime='application/pdf')
        st.subheader('正式报告来源及文件摘要')
        src=load_sheet('sources')
        grid(src[['企业','报告类别','报告年度','本地文件名','页数_PDF','SHA256','正式文件链接']],330)
        st.caption('正式研究的12项评分仅评价限定研究细项。第12条、第50条的正式条款全部要件尚未完成评价。')
    elif page=='E/S/G限定评分':
        df=load_sheet('scores');df['研究细项']=df['指标编号'].map(LABELS)
        st.warning('此处展示工作簿中的既定限定细项分数。不合成为企业总分，不做企业排名，也不推断实际ESG绩效。')
        grid(df[['企业','维度','指标编号','研究细项','限定细项得分','有效分母','正式条款其余要件','双报告完整同口径比较']],440)
        companies=sorted(df['企业'].unique().tolist()); company=st.selectbox('查看某个评分的完整依据：企业',companies)
        item=st.selectbox('指标编号',df[df['企业']==company]['指标编号'].tolist(),format_func=lambda x:f'{x}｜{LABELS.get(x,x)}')
        show_score_detail(company,item)
        with st.expander('评分公开规则（原表）'):grid(load_sheet('rules'),280)
    elif page=='原始证据追溯':
        source=st.selectbox('选择证据层级',['原页证据30条','人工判断输入12条','证据及评分12项','V6逐要件审查60项'])
        key={'原页证据30条':'evidence','人工判断输入12条':'judgment','证据及评分12项':'detail','V6逐要件审查60项':'audit'}[source]
        df=load_sheet(key)
        st.caption('原始PDF未托管：仅显示Excel中已保存的报告文件名、PDF页码、原文摘录与哈希；没有PDF直达功能。')
        lookup={'company':'企业','indicator':'指标编号','file':'报告文件','pdf_page':'PDF页码'}
        company_col='企业' if '企业' in df else 'company'
        id_col='指标编号' if '指标编号' in df else 'indicator'
        options=selectors(df,'ev_'+key,(company_col,id_col))
        report_col='file' if 'file' in df.columns else ('报告文件' if '报告文件' in df.columns else None)
        page_col='pdf_page' if 'pdf_page' in df.columns else ('证据页码' if '证据页码' in df.columns else ('原页' if '原页' in df.columns else None))
        c_report,c_page=st.columns(2)
        if report_col:
            report_options=sorted(df[report_col].dropna().astype(str).unique().tolist())
            options[report_col]=c_report.multiselect('正式报告文件',report_options,key='ev_report_'+key)
        else:
            c_report.caption('此数据表没有单独的报告文件字段，可通过全文检索。')
        page_query=c_page.text_input('PDF页码筛选（按文本包含查找）',key='ev_page_'+key)
        q=st.text_input('全文搜索（企业、指标、证据文本等）',key='ev_search')
        filtered=filter_rows(df,options,q)
        if page_query.strip() and page_col:
            filtered=filtered[filtered[page_col].astype(str).str.contains(page_query.strip(),regex=False,na=False)]
        st.write(f'匹配 {len(filtered)} 条／原表 {len(df)} 条')
        grid(filtered,470)
        dump('下载当前筛选证据',source,filtered,'ESG_V2_证据筛选.xlsx')
    elif page=='双报告交叉验证':
        st.error('完整同口径双报告比较项目：0 项。没有有效一致性百分比分母。')
        cross=load_sheet('cross');choices=selectors(cross,'cross',('企业','议题'))
        filtered=filter_rows(cross,choices)
        st.subheader('有限事实案例：员工、治理、排放与边界')
        grid(filtered,460)
        st.caption('局部事实相近不等于完整同口径一致；未检索到不等于选择性披露。')
        with st.expander('长城汽车治理机构人数时间线'):
            grid(load_sheet('timeline'),240)
            st.warning('治理委员会人数差异尚未解释，不将其直接认定为矛盾披露。')
    elif page=='敏感性分析':
        st.caption('54个收尾敏感性情景均来自正式V6工作簿；情景分数不替换正式基准分数。')
        df=load_sheet('sensitivity');st.write(f'情景数量：{len(df)}')
        grid(df,400)
        st.markdown('**基准分与情景分对照**')
        candidates=df['企业'].dropna().unique().tolist()
        co=st.selectbox('选择敏感性企业',candidates)
        sub=df[df['企业']==co].copy()
        if {'基准分','情景分','指标编号','要件'}.issubset(sub.columns):
            sub['情景标签']=sub['指标编号'].astype(str)+' · '+sub['要件'].astype(str)+' · '+sub['替代系数'].astype(str)
            chart_df=sub[['情景标签','基准分','情景分']].copy()
            chart_df['基准分']=pd.to_numeric(chart_df['基准分'],errors='coerce')
            chart_df['情景分']=pd.to_numeric(chart_df['情景分'],errors='coerce')
            st.line_chart(chart_df.set_index('情景标签'))
            st.caption('每一组情景仅改变指定条件；图中两条线分别为原基准分与替代情景分。')
        st.markdown('**情景与正式评分须同时查看**')
        st.dataframe(load_sheet('scores')[['企业','指标编号','限定细项得分']],hide_index=True,use_container_width=True)
        num=df.select_dtypes(include='number').columns.tolist()
        if len(num)>=1:
            st.caption('数值型情景指标仅供观察敏感性，不用于研究结论替代。')
        dump('导出敏感性分析','评分敏感性收尾',df,'ESG_V2_敏感性分析.xlsx')
    elif page=='研究数据导出':
        options=[('12项限定评分','scores'),('证据核验30条','evidence'),('证据及评分12项','detail'),('逐要件审查60项','audit'),('双报告有限案例','cross'),('54个敏感性情景','sensitivity')]
        for name,key in options:
            dump(f'下载{name}',name,load_sheet(key),f'ESG_V2_{key}.xlsx')
        st.download_button('下载完整V6研究工作簿',WORKBOOK.read_bytes(),WORKBOOK.name,mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        st.subheader('研究范围和必须保留的局限')
        st.write('第12条与第50条：只完成限定研究细项，正式条款全部要件尚未评价。')
        st.write('30条定向原页核验：不等于全部自动提取记录的总体准确率。')
        st.write('员工人数：年报与ESG报告统计定义、组织范围仍有未确认事项。')
        st.write('长城汽车：治理委员会人数时间线存在尚未解释的差异。')
        st.write('完整同口径双报告比较有效分母为0，因此不计算一致性百分比。')
        st.write('不得将未检索到的信息直接解释为企业选择性披露或ESG表现较差。')
        st.write('未部署原始六份PDF，因此证据溯源仅限经核验文本、文件哈希与页码，不能直接打开PDF页面。')
        with st.expander('工作簿中的定稿门槛与复核结论'):grid(load_sheet('limits'),220)
