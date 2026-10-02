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
它和 `shadcn.icon` 一样，是 51 个工厂函数里少数几个不对应组件类的成员。
:::

所有单元格都自带 `whitespace-nowrap`。要允许换行，用
`shadcn.table_cell('…').with_classes('whitespace-normal')`，而不是 `.classes(...)`。

用 `shadcn.badge(...)` 放在单元格里做状态标记是最常见的组合：

```python
shadcn.table_cell('')
with shadcn.table_cell():
    shadcn.badge('Paid', variant='secondary')
```

## skeleton 与 separator

这两个组件的完整说明在 {doc}`layout` 里 —— `skeleton` 负责加载占位，`separator` 负责分隔
线。在展示场景里它们最常见的用法是给表格与卡片之间加一条分隔，以及在异步加载期间替换掉
表格行。

## 下一步

- {doc}`layout` —— card 家族，展示组件最常见的容器。
- {doc}`components` —— 全部工厂函数与参数的一句话索引。
