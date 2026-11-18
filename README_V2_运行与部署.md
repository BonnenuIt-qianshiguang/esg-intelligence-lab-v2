# ESG Intelligence Lab V2.0 — 2025年正式研究接入

## 项目结构和隔离
- `app.py`：保留 V1.0 原始页面主体，通过侧边栏选择“2025正式研究”或“2023历史演示”。
- `v2_pages.py`：V2.0 的七个研究页面；不重新评分，仅展示正式 Excel 的分数和引用记录。
- `v2_data.py`：V6 工作簿只读读取、校验、筛选、导出。
- `data_2025/三企业V6双报告与评分收尾核验.xlsx`：正式2025年研究数据，**不替换原表中的值**。
- `esg_v01_backend.py`、`esg_batch_pilot.py`、`已核实样本_15条.xlsx`：原 V1 2023 年历史演示、PDF 文本提取及下载代码与样本。
- `.streamlit/config.toml`：保留旧配置（单个上传文件 50 MB）。

## 本地运行（Windows 零基础）
1. 安装 Python 3.12（或使用已有兼容环境）并解压 ZIP。
2. 打开解压后包含 `app.py` 的文件夹，在地址栏输入 `cmd`，按回车。
3. 输入 `python -m pip install -r requirements.txt`，完成后输入 `python -m streamlit run app.py`。
4. 浏览器打开终端提示的本机地址（通常 http://localhost:8501）。若因 SSL 无法安装，可跳过本地运行，直接按下面的云端部署办法处理。
5. 核查自动化数据：`python test_v2.py`；核查 V1：`python smoke_test.py`。

## GitHub 更新（目前尚未替你更新）
推荐先保留现有 V1 公网应用：**在 GitHub 新建 `esg-intelligence-lab-v2` 仓库**，把 ZIP 解压后文件夹里面的全部内容上传到仓库根目录，**不是上传 ZIP 本身**。务必包括 `app.py`、`v2_data.py`、`v2_pages.py`、`data_2025` 文件夹及原有 V1 后端和 Excel。不要上传任何账户密码或密钥。

如果选择升级原仓库，请先用 GitHub 的 Download ZIP 备份当前版本；覆盖同名文件前确认有回滚版本。建议优先新建 V2 仓库，以免影响老师已知的 V1 链接。

## Streamlit Community Cloud
1. 登录 https://share.streamlit.io/（可使用 GitHub 登录）。
2. 选择创建应用，从 GitHub 中选择 V2 仓库；Branch 填 `main`；Main file path 填 `app.py`。
3. 高级设置：选择 Python 3.12；不需填任何 Secrets。
4. 部署后实际点击侧边栏两种版本，并逐项验证数据页、V1 样本、V1 PDF 提取、Excel 下载。
5. 2025 年源工作簿应在 `data_2025` 文件夹，六份报告 PDF 不需要上传 GitHub。

## 研究边界
- V2 显示的 12 个分数来自 `V6限定评分摘要`，不自动计算企业总ESG分或排名。
- `V6逐要件审查60项` 包含原文摘录、PDF 页码、权重、判断、折算得分及证据 ID。
- 2025 年的17项研究指标和51项历史核验位置是总体研究范围，不等于51项全部得分。
- 30项定向核验 ≠ 总体自动提取准确率。所有跨报告完整同口径比较分母为0。
- 原始PDF未包含在部署包，证据页面没有模拟不存在的原PDF跳转。
- V1 上传其他PDF仅产生待人工复核的候选线索。

## 依赖与检查
`requirements.txt` 延用 V1 已知依赖版本。实际 Streamlit Community Cloud 安装成功与否需要部署日志及公网操作验证，不能从离线代码检查推断。
