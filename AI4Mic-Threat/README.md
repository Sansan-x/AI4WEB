# AI4Mic-Threat — Claude Code 送检即合规多 Agent

Java 微服务**服务级**威胁风险画像，映射安全排查基线与中间件送检用例，支撑「送检即合规」闭环。

## 架构

- **编排**：`compliance-coordinator`（唯一可 spawn 子 Agent）
- **Worker**：10 个专职 Subagent（context → applicability → signals → synthesize → mapping → gap → policy → evidence）
- **能力**：每个 Agent 预加载对应 `.claude/skills/*`
- **契约**：`compliance/schemas/` + `compliance/scripts/validate_artifact.py`

```text
/compliance-run  →  compliance-coordinator  →  workers  →  .claude/runs/{runId}/
```

## 快速开始

### 1. Golden 演示（无需 LLM）

```bash
python3 compliance/scripts/run_golden_pipeline.py
# 产物: .claude/runs/golden-demo/09-evidence/index.json
# 决策: Block（SQL 用例 FAIL + 开放 P1）
```

### 2. Claude Code 交互

```bash
cd AI4Mic-Threat
claude
/compliance-run --repo compliance/fixtures/demo-service --services order-service --middleware compliance/examples/middleware_cases.sample.json
```

### 3. CI / 自动化

```bash
claude --agent compliance-coordinator -p "Run compliance pipeline for repo compliance/fixtures/demo-service, services order-service, middleware compliance/examples/middleware_cases.sample.json"
```

## 目录

| 路径 | 说明 |
|------|------|
| `.claude/agents/compliance/` | 11 个 Subagent 定义 |
| `.claude/skills/` | 12 个 Skill（含 orchestrator 与 schemas） |
| `.claude/commands/compliance-run.md` | Slash 命令入口 |
| `compliance/taxonomy/` | 风险域、基线清单、策略门禁 |
| `compliance/schemas/` | JSON Schema |
| `compliance/scripts/` | init / merge / validate / golden |
| `compliance/fixtures/demo-service/` | 演示用 Java 微服务 |

## 自定义基线

编辑 [`compliance/taxonomy/baseline-catalog.yaml`](compliance/taxonomy/baseline-catalog.yaml)，重启 Claude Code 会话后生效。

## Middleware `targetService` 语义

- `targetService: "<service-name>"`：仅匹配该微服务。
- `targetService: "*"`：通配所有微服务，可作为覆盖兜底。
- 同一 baseline/domain 同时存在具体服务和 `*` 时，采用**具体服务优先**，`*` 仅用于未命中具体服务的情况。
- wildcard 命中会在 `06-mappings.json` 的解释字段体现，并参与 `07-gaps.json` 的状态判定（不会被误判为 `NoCaseMatched`）。

## 验收清单

- [ ] `claude agents` 列出 11 个 compliance agents
- [ ] `/skills` 列出 12 个 project skills
- [ ] `run_golden_pipeline.py` 退出码 0，且 `08-decision.json` 为 `Block`
- [ ] `order-service` 的 applicability 排除 CMDI/FILE
- [ ] `09-evidence/index.json` 含 `agentRunTrace`

## 约束

- Subagent **不能**嵌套 spawn；编排仅由 coordinator 完成。
- 输出颗粒度为 **RiskPoint / ServiceRiskProfile**，非逐行走读审计。
