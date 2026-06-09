# AI4Mic-Threat — 送检即合规多 Agent

Java 微服务**服务级**威胁风险画像，映射安全排查基线与中间件送检用例，支撑「送检即合规」闭环。

支持 **Claude Code** 与 **OpenCode** 双轨运行。

## 架构

- **编排**：`compliance-coordinator`（唯一可调度子 Agent）
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
# 产物（三场景）:
#   golden-demo-soft      → ConditionalPass（domain 匹配，深度不足仅审计）
#   golden-demo-hard      → ConditionalPass（SQL 服务级 FAIL + wildcard PASS，大项仍匹配）
#   golden-demo-unmatched → Block（SQLI 无同 domain 用例）
# 策略: policy-gate v1.2，policyMode=lenient；Pass/ConditionalPass 即送检即合规
# 日后将 policy-gate.yaml 中 policyMode 改为 strict 可恢复 v1.1 严格判定
```

### 2. Claude Code 交互

```bash
cd AI4Mic-Threat
claude
/compliance-run --repo compliance/fixtures/demo-service --services order-service --middleware compliance/examples/middleware_cases.sample.json
```

### 3. OpenCode 交互

```bash
cd AI4Mic-Threat
export OPENCODE_MODEL="<provider>/<model-id>"   # 运行 opencode models 查看可用 ID
export OPENCODE_SMALL_MODEL="<provider>/<small-model-id>"  # 可选
opencode
/compliance-run --repo compliance/fixtures/demo-service --services order-service --middleware compliance/examples/middleware_cases.sample.json
```

首次使用请复制 [`.env.example`](.env.example) 中的变量说明。OpenCode 通过 [`opencode.json`](opencode.json) 加载权限与默认 Agent。`.opencode/agents/*.md` 不要使用 Claude 的 `color: green` 等非法值；`compliance-coordinator` 的 `task` 白名单在 [`.opencode/agents/compliance-coordinator.md`](.opencode/agents/compliance-coordinator.md) 的 frontmatter 中配置。

### 4. CI / 自动化

```bash
claude --agent compliance-coordinator -p "Run compliance pipeline for repo compliance/fixtures/demo-service, services order-service, middleware compliance/examples/middleware_cases.sample.json"
```

## 目录

| 路径 | 说明 |
|------|------|
| `.claude/agents/compliance/` | Claude Code：11 个 Subagent 定义 |
| `.opencode/agents/` | OpenCode：11 个扁平 Agent 定义 |
| `.claude/skills/` | 12 个 Skill（Claude + OpenCode 共用） |
| `.claude/commands/compliance-run.md` | Claude Code Slash 命令 |
| `.opencode/commands/compliance-run.md` | OpenCode Slash 命令 |
| `opencode.json` | OpenCode 项目配置（权限、默认 Agent、插件） |
| `AGENTS.md` | 项目规则（OpenCode 优先读取） |
| `compliance/taxonomy/` | 风险域、基线清单、策略门禁 |
| `compliance/schemas/` | JSON Schema |
| `compliance/scripts/` | init / merge / validate / golden |
| `compliance/fixtures/demo-service/` | 演示用 Java 微服务 |

## 自定义基线

编辑 [`compliance/taxonomy/baseline-catalog.yaml`](compliance/taxonomy/baseline-catalog.yaml)，重启会话后生效。

## 公开产品安全排查基线

公开基线与中间件送检用例独立维护；服务标识**不使用 `targetService`**，统一通过 `rules[].datas[].service` 匹配与统计。

| 文件 | 用途 |
|------|------|
| [`compliance/examples/public_baseline.template.json`](compliance/examples/public_baseline.template.json) | 31 条规则模板（14 类），`datas` 为空 |
| [`compliance/examples/public_baseline.import.sample.json`](compliance/examples/public_baseline.import.sample.json) | 真实测试数据导入样例（一条规则可含多个 `service`） |
| [`compliance/examples/public_baseline.merged.sample.json`](compliance/examples/public_baseline.merged.sample.json) | 合并后的完整产品测试基线（golden 样例） |

合并导入数据：

```bash
python3 compliance/scripts/import_public_baseline.py \
  --template compliance/examples/public_baseline.template.json \
  --import compliance/examples/public_baseline.import.sample.json \
  --output compliance/examples/public_baseline.merged.sample.json

python3 compliance/scripts/validate_artifact.py \
  --schema public-baseline \
  --file compliance/examples/public_baseline.merged.sample.json
```

覆盖判定：`datas` 中某 `service` 的 `status === "已完成"` 表示该规则在该服务上已覆盖测试；`selectResult` 仅记录测试结论（通过/不通过/待测）。可选 `--service <name>` 过滤单服务视图。

## Middleware `targetService` 语义

- `targetService: "<service-name>"`：仅匹配该微服务。
- `targetService: "*"`：通配所有微服务，可作为覆盖兜底。
- 同一 baseline/domain 同时存在具体服务和 `*` 时，采用**具体服务优先**，`*` 仅用于未命中具体服务的情况。
- wildcard 命中会在 `06-mappings.json` 的解释字段体现，并参与 `07-gaps.json` 的状态判定（不会被误判为 `NoCaseMatched`）。

## 验收清单

### Claude Code

- [ ] `claude agents` 列出 11 个 compliance agents
- [ ] `/skills` 列出 12 个 project skills
- [ ] `run_golden_pipeline.py` 退出码 0，且 `08-decision.json` 为 `Block`
- [ ] `order-service` 的 applicability 排除 CMDI/FILE
- [ ] `09-evidence/index.json` 含 `agentRunTrace`

### OpenCode

- [ ] `opencode` 启动无 `ProviderInitError`（已设置 `OPENCODE_MODEL`）
- [ ] Agent 列表含 `compliance-coordinator` 及 10 个 worker
- [ ] `/skills` 或 skill 工具可见 12 个 skills
- [ ] `run_golden_pipeline.py` 退出码 0
- [ ] `/compliance-run` 产出 `.claude/runs/{runId}/08-decision.json`

## 故障排查（OpenCode）

- 日志：`opencode --print-logs` 或 `~/.local/share/opencode/log/`
- 模型：运行 `opencode models`，确认 `OPENCODE_MODEL` 为 `provider/model-id` 格式
- Agent 启动失败：检查 `.opencode/agents/*.md` 是否含非法 `color:`（仅允许 `#hex` 或 `primary`/`info` 等主题名）；勿在 `opencode.json` 与同名 md 重复定义 coordinator
- 未安装 `opencode-claude-hooks` 时保持 `"plugin": []`；需 PostToolUse 校验再安装插件并启用
- 改 Agent 提示词时需同步 `.claude/agents/compliance/` 与 `.opencode/agents/`
- OpenCode Agent **不要**在 frontmatter 使用 `skills:`；在正文用 `skill({ name: "..." })` 显式加载（见各 `.opencode/agents/*.md`）

## 约束

- Subagent **不能**嵌套 spawn；编排仅由 coordinator 完成。
- Claude Code 使用 **Agent** 工具；OpenCode 使用 **task** 工具调用同名 worker。
- 输出颗粒度为 **RiskPoint / ServiceRiskProfile**，非逐行走读审计。
