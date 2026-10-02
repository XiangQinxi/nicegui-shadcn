# 布局

布局这一组由三样东西构成：**card 家族**（容器与页头页脚）、`separator`（分隔线）、
`skeleton`（加载占位）。它们全部是纯粹的带样式的 `div`，没有任何 `.vue` 模板，因此不存在
客户端交互成本 —— 组合方式完全由你决定。

## card 家族

| 工厂函数 | 渲染为 | 自带样式要点 |
| --- | --- | --- |
| `shadcn.card` | `<div>` | `flex flex-col gap-6 rounded-xl border bg-card py-6 text-card-foreground shadow-sm` |
| `shadcn.card_header` | `<div>` | `grid auto-rows-min items-start gap-1.5 px-6` |
| `shadcn.card_title` | `<div>` | `leading-none font-semibold` |
| `shadcn.card_description` | `<div>` | `text-sm text-muted-foreground` |
| `shadcn.card_content` | `<div>` | `px-6` |
| `shadcn.card_footer` | `<div>` | `flex items-center px-6` |

`card_title` 与 `card_description` 接受一个位置参数作为文本；其余四个只接受关键字参数。
标准组合：

```python
with shadcn.card():
    with shadcn.card_header():
        shadcn.card_title('Title')
        shadcn.card_description('Description')
    with shadcn.card_content():
        shadcn.input(placeholder='Name')
    with shadcn.card_footer():
        shadcn.button('Cancel', variant='outline')
        shadcn.button('Save')
```

`card_header` 是 grid 容器，所以标题与描述会自动上下堆叠，无需额外包裹。

:::{tip}
`card` 自带 `gap-6`。如果你希望内容区与头部的间距变小，请用
`shadcn.card().with_classes('gap-2')`，而不是 `.classes('gap-2')` —— 原因见 {doc}`usage`
里的追加陷阱。
:::

## separator

```python
shadcn.separator()                       # 水平，1px 高，占满宽度
shadcn.separator(orientation='vertical') # 垂直，1px 宽，占满高度
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `orientation` | `'horizontal'` | `'horizontal'` 或 `'vertical'` |
| `decorative` | `True` | 装饰性时为 `role="none"`；置为 `False` 则变为 `role="separator"` 并带上 `aria-orientation` |

`decorative=True` 是默认值，因为绝大多数分隔线只是视觉分隔，不应该被屏幕阅读器读出来。
只有当它确实承担语义分隔时才传 `decorative=False`。

:::{note}
垂直分隔线需要一个有确定高度的父容器，否则 `h-full` 无高度可继承，线会消失。
:::

## skeleton

```python
shadcn.skeleton()                                    # 一个默认尺寸的脉冲方块
shadcn.skeleton(width='8rem', height='1rem')          # 内联宽高
shadcn.skeleton().with_classes('size-10 rounded-full')  # 头像占位
```

`width` / `height` 会写成内联样式（`style="width: …; height: …"`），所以它们能接受任何
CSS 长度单位，不受预编译 class 词汇表的限制 —— 这是绕开 {doc}`limitations` 里
“`classes=` 有边界”的一个实用出口。

`skeleton` 自带 `animate-pulse rounded-md bg-accent`，用作头像占位时用
`.with_classes('rounded-full')` 把圆角改成圆形。

## 与 NiceGUI 的 row / column / grid 配合

shadcn 没有自己的栅格系统。把 shadcn 组件放进 NiceGUI 原生的布局容器即可，两者混用没有
任何限制：

```python
# 水平排列，自动换行
with ui.row().classes('flex-wrap items-center gap-3'):
    shadcn.badge('Default')
    shadcn.badge('Secondary', variant='secondary')
    shadcn.button('Refresh', variant='outline')

# 垂直排列
with ui.column().classes('gap-1'):
    shadcn.card_title('Dimensions')
    shadcn.card_description('Set the layout dimensions.')

# 网格：直接用一个原生 div
with ui.element('div').classes('grid grid-cols-3 gap-3'):
    for label in ('One', 'Two', 'Three'):
        shadcn.badge(label)
```

也可以直接用 Tailwind 的 grid 工具类把 `card_content` 变成网格 —— 这是构建产物里已经生成
的词汇，不需要重新编译：

```python
with shadcn.card_content().classes('grid gap-4'):
    shadcn.input(placeholder='Name')
    shadcn.input(placeholder='Email')
```

:::{warning}
`ui.grid(columns=3)` 也能用，但它是 NiceGUI 自带的 `nicegui-grid` 实现（带自己的
`nicegui-grid` class 与内联的 `grid-template-columns`），不是 Tailwind 工具类，两套列宽与
间距规则混用时不容易预测。想要可预测的结果，优先用
`ui.element('div').classes('grid grid-cols-3 gap-3')` 这种纯 Tailwind 写法。
:::

## button_group

`button_group` 把一排按钮缝成一体，并自动处理相邻按钮的圆角与描边：

```python
with shadcn.button_group():
    shadcn.button('Day', variant='outline')
    shadcn.button('Week', variant='outline')
    shadcn.button('Month', variant='outline')
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `vertical` | `False` | 置为 `True` 时上下堆叠，而不是左右并排 |

注意参数名是 `vertical: bool`，**没有** `orientation`。想在组里插入文字或分隔线，用
`button_group_text` 与 `button_group_separator`：

```python
with shadcn.button_group():
    shadcn.button_group_text('Pages')
    shadcn.button_group_separator()
    shadcn.button('Previous', variant='outline')
    shadcn.button('Next', variant='outline')
```

`button_group_text(text, ...)` 接受一个位置参数作为文本，通常用来放组前面的标签；
`button_group_separator(vertical=False)` 是一条 1px 竖线，`vertical=True` 时变成横线，要和
`button_group(vertical=True)` 保持一致。

## breadcrumb

面包屑是一套组合结构，七个工厂函数各自渲染一个 `<li>` / `<a>` / `<nav>`：

```python
with shadcn.breadcrumb():
    with shadcn.breadcrumb_list():
        with shadcn.breadcrumb_item():
            shadcn.breadcrumb_link('Home', href='/')
        shadcn.breadcrumb_separator()
        with shadcn.breadcrumb_item():
            shadcn.breadcrumb_link('Components', href='/components')
        shadcn.breadcrumb_separator()
        with shadcn.breadcrumb_item():
            shadcn.breadcrumb_page('Breadcrumb')
```

| 工厂函数 | 渲染为 | 位置参数 | 关键字参数 |
| --- | --- | --- | --- |
| `shadcn.breadcrumb` | `<nav aria-label="breadcrumb">` | — | — |
| `shadcn.breadcrumb_list` | `<ol>` | — | — |
| `shadcn.breadcrumb_item` | `<li>` | — | — |
| `shadcn.breadcrumb_link` | `<a>` | `text` | `href` |
| `shadcn.breadcrumb_page` | `<span aria-current="page">` | `text` | — |
| `shadcn.breadcrumb_separator` | `<li role="presentation">` | — | `icon` |
| `shadcn.breadcrumb_ellipsis` | `<span>` + `…` | — | — |

`breadcrumb_link` 的 `href` 省略时不渲染 `<a>` 的可聚焦行为 —— 源码里明确要求「给它一个
`href`」，所以静态链接也建议写上。`breadcrumb_separator(icon='chevron-right')` 默认画一个
右尖括号图标，传 `icon=None` 会得到一个空的 `<li>`，方便你自己塞内容。

路径过长时用省略号收尾，再配一个下拉菜单是最常见的做法：

```python
with shadcn.breadcrumb():
    with shadcn.breadcrumb_list():
        with shadcn.breadcrumb_item():
            shadcn.breadcrumb_ellipsis()
        shadcn.breadcrumb_separator()
        with shadcn.breadcrumb_item():
            shadcn.breadcrumb_page('Current page')
```

## pagination

```python
shadcn.pagination(page=1, total=10)
shadcn.pagination(page=5, total=20, siblings=2)
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `page` | `1` | 当前页，从 1 开始计数 |
| `total` | `1` | 总页数 |
| `siblings` | `1` | 当前页左右各保留几个页码 |
| `on_change` | `None` | 换页时回调，值是新的页码 |

`pagination` 是 `ValueElement`，所以 `.value` 可读可写，也能 `.bind_value(...)`。页码跳转
通常这样接：

```python
pager = shadcn.pagination(page=1, total=12, siblings=1,
                          on_change=lambda e: ui.notify(f'第 {e.value} 页'))
pager.value = 3
```

## scroll_area

`scroll_area` 是给内容加一层**细滚动条**的容器，适用于长列表、日志面板与侧边栏：

```python
with shadcn.scroll_area(type_='hover').classes('h-32 w-full rounded-md border p-3'):
    for i in range(40):
        ui.label(f'第 {i + 1} 行')
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `type_` | `'hover'` | 滚动条何时可见：`hover` / `scroll` / `auto` / `always` |
| `scroll_hide_delay` | `600` | 停止滚动后滚动条保留多少毫秒 |

参数名带下划线是因为 `type` 是 Python 内建名：`type_='always'` 表示常驻滚动条，
`'scroll'` 只在滚动时出现，`'auto'` 交给浏览器判断。

:::{note}
`scroll_area` 本身不设高度，`h-32` 这类尺寸要写在它自己身上（如上例的 `.classes(...)`），
否则容器会跟着内容一起长高，永远不出现滚动条。
:::

## direction

`direction` 是 reka-ui 的方向上下文提供者，用来让内部的浮层、滑块等原语知道当前是
从左到右还是从右到左：

```python
with shadcn.direction('rtl'):
    with shadcn.popover():
        shadcn.popover_trigger('打开面板')
        with shadcn.popover_content():
            ui.label('这里的浮层会按 RTL 方向对齐。')
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `direction` | `'ltr'` | `'ltr'` 或 `'rtl'`，另外这是唯一的位置参数 |
| `inline` | `False` | 置为 `True` 时渲染 `<span>` 而不是 `<div>`，方便嵌在行内文本里 |

## 下一步

- {doc}`display` —— 表格家族，本质上也是一种布局。
- {doc}`forms` —— 放进 `card_content` 里的表单控件。
- {doc}`typography` —— 标题、段落与引用等纯文本组件。
