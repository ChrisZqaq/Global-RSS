# 简报格式与翻译规范

## 输入

`output/filtered_*.jsonl`，每行一个 JSON：`{source, via, title, link, published, ts, summary, topics}`。

## 产出

`output/brief_content.json`，数组，每项：

```json
{
  "source": "信源显示名（英文原名即可，如 Reuters）",
  "zh_title": "中文标题",
  "author": "作者（原文有则填，没有则空字符串）",
  "link": "原文链接",
  "date": "M月D日",
  "paragraphs": ["段落1", "段落2"]
}
```

然后 `python scripts/generate.py output/brief_content.json` 出 docx。

## 翻译/总结要求（逐条遵守）

1. **标题**：忠实翻译成中文，保留专有名词原文（公司名、产品名、人名第一次出现可中英并列）。不加评论性词汇。
2. **正文总结**：2–4 个自然段，每段 2–4 句。第一段必须以「信源名 M月D日报道」开头。
3. **保留**：所有关键数字（金额、百分比、日期）、人名职务、直接引语的核心含义、因果逻辑。
4. **不做**：不翻译全文、不添加原文没有的信息、不写「小编认为」类评论、不遗漏原文的重要限定条件（如"可能""预计"）。
5. **summary 不够时**：feed 摘要过短（<100 字）导致无法写出 2 段总结，可用 FetchURL 抓原文正文再总结；抓不到就写一段并缩短。
6. 单条失败：保留原标题，`zh_title` 用原标题，`paragraphs` 写「[本条翻译失败，请阅读原文]」，继续处理下一条。

## docx 渲染效果（generate.py 已实现）

- 标题行：`【信源】中文标题（作者：XXX）` 加粗
- 「信源链接：」+ URL 单独成段
- 正文段落，首段带「信源名 M月D日报道」前缀
- 全文宋体/Times New Roman 11pt，条间空行
