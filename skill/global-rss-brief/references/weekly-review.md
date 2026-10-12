# 每周复盘：从人工校正中学习筛选规则

目标：把用户的人工反转（含理由）转化为 `config/filter_rules.yaml` 的具体修改建议。

## 输入

`state/overrides_log.jsonl`，每行：

```json
{"ts": 1791817567, "key": "原文链接", "action": "include|exclude|clear", "reason": "用户填的理由（可能为空）", "title": "条目标题", "source": "域名"}
```

`reason` 快捷标签含义：主题不符 / 太短·快讯 / 信源不喜 / 重要漏选。

## 流程

1. **读取**最近 7 天的日志（`ts` 为 epoch 秒）。`clear` 动作表示撤销，只用于抵消同 key 的前一条。
2. **归因分类**：
   - `exclude + 主题不符` → 标题里的特征词考虑加入 `exclude`，或该条命中了某个过宽的主题词（考虑从 `topics` 删除/收窄）
   - `exclude + 太短/快讯` → 考虑新增 `flash_patterns` 正则，或调整 `thresholds`
   - `exclude + 信源不喜` → 建议用户直接在信源管理里停用该源，不改词表
   - `include + 重要漏选` → 标题特征词考虑加入对应 `topics`；若是被政军排除误杀，加入 `keep_even_if_excluded`
   - 理由为空的：自己读标题推断类别，标注「理由缺失，推断」
3. **控制灵敏度**：同一规律至少出现 2 次才提议改规则；单次操作只记录不改。
4. **输出 diff 报告**给用户确认，格式：

```markdown
## 筛选规则复盘（YYYY-MM-DD）
本周人工操作 N 次：排除 X / 入选 Y / 撤销 Z

### 建议修改（config/filter_rules.yaml）
1. topics.tech 增加词："xxx"（依据：2 次人工入选，标题均含该词，如《...》）
2. exclude 增加词："yyy"（依据：...）
3. thresholds.flash_news_max_len: 300 → 350（依据：...）

### 仅记录不修改
- 单次操作：...
```

5. **用户确认后**才用编辑工具改 `filter_rules.yaml`；改完可重跑 `python scripts/filter.py` 验证漏斗变化。
6. 修改记录追加到 `state/rules_changelog.md`（日期、改动、依据、确认人），便于回滚。

## 红线

- 不自动写回，必须人工确认
- 不删除用户手动加过的词（changelog 里标注为人工添加的）
- 词表改动保持精确：短语优于单词，避免误伤（如 " ai " 带空格防误中）
