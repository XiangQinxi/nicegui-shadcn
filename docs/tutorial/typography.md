# 排版

排版这一组都是**纯带样式的文本元素**：它们没有 `.vue` 模板、没有任何客户端状态，本质上只是
一个写好了 Tailwind 类的 `<h1>` / `<p>` / `<blockquote>`。因此它们可以和任何其它元素自由
混用，也不会有交互成本。

因为全部继承自 NiceGUI 的 `TextElement`，每一个都支持 `.text`、`.bind_text_from(...)` 与
`set_text(...)`，这也是它们最主要的用法：把文案挂到数据上。

## 标题：`h1` / `h2` / `h3` / `h4` 与 `heading`

```python
shadcn.h1('Getting started')
shadcn.h2('Installation')
shadcn.h3('Requirements')
shadcn.h4('Notes')
shadcn.heading('Same as h3', level=3)
```

| 工厂函数 | 渲染为 | 等效写法 |
| --- | --- | --- |
| `shadcn.h1` | `<h1>` | `shadcn.heading(text, level=1)` |
| `shadcn.h2` | `<h2>` | `shadcn.heading(text, level=2)` |
| `shadcn.h3` | `<h3>` | `shadcn.heading(text, level=3)` |
| `shadcn.h4` | `<h4>` | `shadcn.heading(text, level=4)` |

`h1` ~ `h4` 是 `heading(text, level=…)` 的四个快捷入口，四个函数都是
`h1(text: str = '', **kwargs) -> Heading`，返回的都是同一个 `Heading` 类。`level` 只接受
`1`–`4`，每一级对应 shadcn/ui 为该级准备的字号与字重。

`heading` 的签名是 `heading(text: str = '', *, level: int = 1, **kwargs)`，也就是说 `text`
可以按位置传，`level` 只能按关键字传：

```python
shadcn.heading('Notes', level=4)      # 正确
```

## 段落与强调

```python
shadcn.paragraph('一段普通的正文，行高与字号按 shadcn/ui 的 body 设定。')
shadcn.lead('一段引言式的导语，比正文更大、颜色更淡。')
shadcn.large('稍大的一行，适合卡片标题下方的摘要。')
shadcn.small('小号说明文字。')
shadcn.muted('弱化文字，颜色为 text-muted-foreground。')
```

| 工厂函数 | 渲染为 | 自带样式要点 |
| --- | --- | --- |
| `shadcn.paragraph` | `<p>` | 正文行高与字号 |
| `shadcn.lead` | `<p>` | `text-xl text-muted-foreground` |
| `shadcn.large` | `<div>` | `text-lg font-semibold` |
| `shadcn.small` | `<small>` | `text-sm leading-none font-medium` |
| `shadcn.muted` | `<p>` | `text-sm text-muted-foreground` |

它们都是「给一段文字套样式」的语法糖。注意 `large` 与 `small` 的语义：shadcn/ui 把
`Large` 当作标题级的强调，把 `Small` 当作辅助说明，所以 `small` 自带 `font-medium` 而不是
更细的字重。

## 引用、列表与内联代码

```python
shadcn.blockquote('After all, you can only keep what you give away.')
with shadcn.bullet_list():
    ui.label('随包分发的预编译样式')
    ui.label('不需要构建步骤')
shadcn.inline_code('pip install nicegui-shadcn')
```

| 工厂函数 | 渲染为 | 说明 |
| --- | --- | --- |
| `shadcn.blockquote` | `<blockquote>` | 左侧竖线 + 斜体 |
| `shadcn.bullet_list` | `<ul>` | 自带 `ml-6 list-disc [&>li]:mt-2`，子元素请用 `ui.label` 或 `ui.html` 给出 `<li>` |
| `shadcn.inline_code` | `<code>` | 行内代码，带 `bg-muted` 底与圆角 |

`blockquote` 与 `inline_code` 都接受一个位置参数作为文本；`bullet_list` **没有**位置参数，
它只负责 `<ul>` 本身，列表项由你在 `with` 块里提供。

## 组合成一个内容区块

排版组件最常见的用法不是单独出现，而是拼成一个文档区块：

```python
from nicegui import ui
from nicegui_shadcn import shadcn

with shadcn.card():
    with shadcn.card_header():
        shadcn.h2('Release notes')
        shadcn.card_description('2026-01 版本的主要变化。')
    with shadcn.card_content():
        shadcn.lead('这是一个以稳定为主的小版本。')
        with shadcn.bullet_list():
            ui.label('排版组件全部开放')
            ui.label('图标数量增加到 39 个')
        shadcn.blockquote('升级前请先阅读迁移说明。')
```

## 与 `ui.label` 的关系

`ui.label` 是 NiceGUI 原生的文本元素，样式来自 Quasar；`shadcn` 的排版组件走的是
Tailwind 工具类。两者可以互相替换，但**不要期待它们的默认外观一致**。想让原生文本也带上
shadcn 的字色，用语义化的 class 即可：

```python
ui.label('使用 shadcn 的字色').classes('text-sm text-muted-foreground')
```

## 下一步

- {doc}`layout` —— 把这些文本放进 card 家族里。
- {doc}`display` —— 表格与徽章，另一种“把数据变成文字”的方式。
- {doc}`components` —— 全部工厂函数与参数的一句话索引。
