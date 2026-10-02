# 展示

展示这一组负责把数据变成可读的界面：徽章、提示框、进度、头像，以及一套 shadcn 风格的表格
组合。

## badge

```python
shadcn.badge('Default')
shadcn.badge('Secondary', variant='secondary')
shadcn.badge('Overdue', variant='destructive')
shadcn.badge('Draft', variant='outline')
```

`badge(text, variant=…)` 渲染一个 `<span>`，`variant` 取 `default`、`secondary`、
`destructive`、`outline`。它带有 `TextElement`，所以 `.text` 可读可写，也能
`.bind_text_from(obj, 'status')`。

## alert

```python
shadcn.alert(title='Heads up!', description='You can add components using the CLI.')
shadcn.alert(title='Error', description='Your session has expired.', variant='destructive')
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `title` | `None` | 粗体标题行 |
| `description` | `None` | 次级说明文字 |
| `variant` | `'default'` | `default` 或 `destructive` |
| `icon` | `None` | 覆盖默认图标名 |

`alert` 的所有参数都是关键字参数，它没有位置参数。默认图标按 `variant` 决定：`default` 用
`info`，`destructive` 用 `triangle-alert`。渲染出来的根元素带 `role="alert"`。

也可以自己组合内部结构：

```python
with shadcn.alert(variant='destructive'):
    shadcn.alert_title('Error')
    shadcn.alert_description('Your session has expired. Please sign in again.')
```

`alert_title` 与 `alert_description` 接受一个位置参数作为文本，两者都位于图标的第二列
（`col-start-2`），因此单独使用时记得放在 `with shadcn.alert():` 里面。

## progress

```python
progress = shadcn.progress(60)
progress.set_value(80)
```

- `progress(value=0)`：`value` 是 0–100 的浮点数，超出范围会被**钳制**而不是报错。
- `set_value(value)`：运行时更新，同样钳制；同时刷新 `aria-valuenow`，并平移内部指示条。
- 根元素带 `role="progressbar"`。

与其它控件不同，进度条**不是** `ValueElement`：它没有 `bind_value`，也没有
`on_value_change`，只能通过 `set_value()` 驱动。要在数据变化时同步，就在更新数据的地方
直接调用：

```python
progress = shadcn.progress(0)

def refresh() -> None:
    progress.set_value(job.percent)

ui.timer(0.5, refresh)
```

## avatar

```python
shadcn.avatar(src='/photo.png', fallback='CN')
shadcn.avatar(fallback='AB', size='lg')
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `src` | `None` | 图片地址；给了就渲染一个 `<img>`，`alt` 取 `fallback`（缺省为 `'avatar'`） |
| `fallback` | `''` | 没有图片时显示的缩写 |
| `size` | `'default'` | `default`、`sm`、`lg`、`xl` |

所有参数都是关键字参数。`src` 与 `fallback` 可以同时给：图片可加载时显示图片，否则显示
首字母缩写。`fallback` 的文字挂在内部 `<span>` 上，因此 `size` 变化不会影响它。

:::{tip}
`src` 指向的图片无效时不会自动回退 —— 浏览器会显示一个破图标。需要严格回退逻辑时，请自己
判断后再决定传不传 `src`。
:::

## 表格家族

表格不是单个组件，而是一套 shadcn 的组合结构：

```python
with shadcn.table_container():
    with shadcn.table():
        shadcn.table_caption('最近 3 张发票')
        with shadcn.table_header():
            with shadcn.table_row():
                shadcn.table_head('Invoice')
                shadcn.table_head('Status')
                shadcn.table_head('Amount').classes('text-right')
        with shadcn.table_body():
            with shadcn.table_row():
                shadcn.table_cell('INV-001')
                shadcn.table_cell('Paid')
                shadcn.table_cell('$250.00').classes('text-right')
        with shadcn.table_footer():
            with shadcn.table_row():
                shadcn.table_cell('Total')
                shadcn.table_cell('')
                shadcn.table_cell('$250.00').classes('text-right')
```

| 工厂函数 | 渲染为 | 说明 |
| --- | --- | --- |
| `shadcn.table_container` | `<div>` | `relative w-full overflow-x-auto`，负责横向滚动 |
| `shadcn.table` | `<table>` | `w-full caption-bottom text-sm` |
| `shadcn.table_caption` | `<caption>` | 接受位置文本；`mt-4 text-sm text-muted-foreground` |
| `shadcn.table_header` | `<thead>` | 行底边框 |
| `shadcn.table_body` | `<tbody>` | 最后一行不画底边框 |
| `shadcn.table_footer` | `<tfoot>` | 顶部边框 + `bg-muted/50` |
| `shadcn.table_row` | `<tr>` | 底边框，悬停时 `hover:bg-muted/50` |
| `shadcn.table_head` | `<th>` | 接受位置文本；`h-10 … text-left font-medium` |
| `shadcn.table_cell` | `<td>` | 接受位置文本；`whitespace-nowrap p-2 align-middle` |

:::{note}
`table_container` 是**函数**而不是类 —— 它返回一个普通的 `ShadcnElement` 实例（`<div>`）。
它和 `shadcn.icon` 一样，是 130 个工厂函数里少数几个不对应组件类的成员。
:::

所有单元格都自带 `whitespace-nowrap`。要允许换行，用
`shadcn.table_cell('…').with_classes('whitespace-normal')`，而不是 `.classes(...)`。

用 `shadcn.badge(...)` 放在单元格里做状态标记是最常见的组合：

```python
shadcn.table_cell('')
with shadcn.table_cell():
    shadcn.badge('Paid', variant='secondary')
```

## kbd：键位提示

```python
with shadcn.paragraph().classes('flex items-center gap-1'):
    ui.label('按下')
    shadcn.kbd('Ctrl')
    shadcn.kbd('K')
    ui.label('打开命令面板')
```

`kbd(text)` 接受一个位置参数，渲染成一个带底纹与圆角的 `<kbd>`。它常用于文档、快捷键说明
与空状态里的操作提示。

## marker：状态圆点

`marker` 是一个「小圆点 + 文字」的状态标记，圆点的颜色由 `variant` 决定：

```python
shadcn.marker('Active')
shadcn.marker('Healthy', variant='success')
shadcn.marker('Degraded', variant='warning')
shadcn.marker('Down', variant='error')
shadcn.marker('Syncing', variant='info', pulse=True)
shadcn.marker('Verified', icon='circle-check')
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `text` | `''` | 位置参数，标记的文字 |
| `variant` | `'default'` | `default` / `success` / `warning` / `error` / `info` |
| `icon` | `None` | 用图标替换圆点，例如 `'circle-check'` |
| `pulse` | `False` | 圆点脉冲，表示进行中的状态 |

## spinner：加载指示器

```python
shadcn.spinner()
shadcn.spinner(size=24)
shadcn.spinner(size=12, label='正在同步')
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `size` | `16` | SVG 的宽高（像素） |
| `label` | `'Loading'` | 屏幕阅读器读出的名字 |

`spinner` 渲染的是一个内联 SVG，因此它的颜色跟随 `currentColor` ——
`shadcn.spinner().classes('text-destructive')` 就能把它染成危险色。

## aspect_ratio：固定宽高比

```python
with shadcn.aspect_ratio(16 / 9).classes('w-full overflow-hidden rounded-lg'):
    ui.image('/demo.png').classes('h-full w-full object-cover')
```

`aspect_ratio(ratio=1)` 渲染一个按比例占位的容器，`ratio` 是**宽除以高**，默认 `1`。它本身
不画任何东西，唯一的作用是给子元素一个稳定的盒子，避免图片加载完成时页面跳动。

## empty：空状态

空状态是一套五件套组合：`empty` 是外层容器，内部依次是 `empty_header`、
`empty_media`、`empty_title`、`empty_description`，需要按钮时再加 `empty_content`：

```python
with shadcn.empty():
    with shadcn.empty_header():
        with shadcn.empty_media(variant='icon'):
            shadcn.icon('folder-open')
        shadcn.empty_title('还没有项目')
        shadcn.empty_description('创建第一个项目，或者从模板开始。')
    with shadcn.empty_content():
        shadcn.button('新建项目', icon='plus')
```

| 工厂函数 | 渲染为 | 位置参数 | 关键字参数 |
| --- | --- | --- | --- |
| `shadcn.empty` | `<div>` | — | — |
| `shadcn.empty_header` | `<div>` | — | — |
| `shadcn.empty_media` | `<div>` | — | `variant`（`default` / `icon`） |
| `shadcn.empty_title` | `<div>` | `text` | — |
| `shadcn.empty_description` | `<div>` | `text` | — |
| `shadcn.empty_content` | `<div>` | — | — |

`empty_media(variant='icon')` 会给图标加一个圆形底衬；默认的 `'default'` 只留透明盒子。

## item：列表项

`item` 是比 card 更轻的一行式容器，用来做「头像/图标 + 标题 + 描述 + 操作」的列表：

```python
with shadcn.item_group():
    with shadcn.item(variant='outline'):
        with shadcn.item_header():
            with shadcn.item_media(variant='icon'):
                shadcn.icon('bell')
            with shadcn.item_content():
                shadcn.item_title('Notifications')
                shadcn.item_description('每封邮件都会通知我。')
            with shadcn.item_actions():
                shadcn.switch()
        with shadcn.item_footer():
            shadcn.button('了解更多', variant='link')
    shadcn.item_separator()
    with shadcn.item(size='sm'):
        with shadcn.item_content():
            shadcn.item_title('Compact row')
```

| 工厂函数 | 说明 |
| --- | --- |
| `shadcn.item` | 单项容器；`variant` ∈ `default`（无边框）/ `outline`，`size` ∈ `default` / `sm` |
| `shadcn.item_group` | 把多项包成一组，统一间距 |
| `shadcn.item_header` | 头部行，通常是 `media` + `content` + `actions` |
| `shadcn.item_media` | 左侧图标/头像位；`variant='icon'` 会加底衬 |
| `shadcn.item_content` | 主体文字区，内部放 title / description |
| `shadcn.item_title` | 标题，接受位置文本 |
| `shadcn.item_description` | 次级说明，接受位置文本 |
| `shadcn.item_actions` | 右侧操作位，放按钮或开关 |
| `shadcn.item_footer` | 底部行，常用于放次要操作 |
| `shadcn.item_separator` | 项之间的分隔线 |

## skeleton 与 separator

这两个组件的完整说明在 {doc}`layout` 里 —— `skeleton` 负责加载占位，`separator` 负责分隔
线。在展示场景里它们最常见的用法是给表格与卡片之间加一条分隔，以及在异步加载期间替换掉
表格行。

## 下一步

- {doc}`layout` —— card 家族，展示组件最常见的容器。
- {doc}`forms` —— 把 `item_actions` 里的开关接上数据。
- {doc}`components` —— 全部工厂函数与参数的一句话索引。
