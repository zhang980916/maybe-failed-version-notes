# OpenClaw A 股研究实验室

[English](README.md)

这是一个从本地 OpenClaw 量化研究工作区中整理出来的 **脱敏版研究脚手架**。它保留了可复用的系统结构：因子注册、实验记录、组合评估、数据桥和只读看板；同时移除了私人数据、真实持仓、本机路径、消息凭证、交易输出和生产策略文件。

![Dashboard 预览](docs/assets/dashboard-preview.png)

## 适合用来做什么

- 记录因子元数据：名称、类别、窗口、定义、状态和最近 IC。
- 记录研究实验：回测、walk-forward CV、参数和关键指标。
- 评估因子组合：用一个透明的 mock 评分器演示组合排序流程。
- 生成看板数据：把 mock 候选、实验记录和因子注册表合成一个 dashboard JSON。
- 展示研究结果：静态只读 dashboard，不连接券商，不下单。

## 目录结构

```text
src/openclaw_a_share_research_lab/
  registry.py          # 因子注册和实验记录
  gladiator.py         # 因子组合评估
  dashboard_bridge.py  # dashboard 数据桥
dashboard/
  index.html           # 静态只读展示页
examples/mock_data/
  factors.csv
  candidates.json
  experiments.jsonl
docs/
  architecture.md
```

## 不包含什么

- 不包含实盘交易代码。
- 不包含账户、持仓、委托或成交数据。
- 不包含私有行情库、模型文件或大数据文件。
- 不包含硬编码本机路径或 OpenClaw 运行目录。
- 不包含 cookies、token、credentials、memory logs 或消息平台状态。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python scripts\build_demo.py
python -m pytest
```

预览 dashboard：

```powershell
python -m http.server 8123
```

然后打开：

```text
http://127.0.0.1:8123/dashboard/
```

## 常用命令

生成因子注册表：

```powershell
python -m openclaw_a_share_research_lab.registry build --factors examples\mock_data\factors.csv --out data\factor_registry.json
```

追加实验记录：

```powershell
python -m openclaw_a_share_research_lab.registry log-experiment --manifest examples\mock_data\experiment_manifest.json --out data\experiments.jsonl
```

运行因子组合评估：

```powershell
python -m openclaw_a_share_research_lab.gladiator --factors examples\mock_data\factors.csv --out data\gladiator_rankings.json
```

生成 dashboard 数据：

```powershell
python -m openclaw_a_share_research_lab.dashboard_bridge --mock-dir examples\mock_data --out dashboard\dashboard_data.json
```

## 安全边界

这个仓库只用于研究、演示和可视化，不构成投资建议，也不会下单。任何真实交易系统都应该把执行代码、券商配置、账户凭证、真实持仓和私有行情数据保存在仓库之外。

当前版本建议先作为私有仓库使用。公开前建议再做一次人工审阅，确认没有加入真实数据、策略细节或个人工作流痕迹。
