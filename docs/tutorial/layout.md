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

## 下一步

- {doc}`display` —— 表格家族，本质上也是一种布局。
- {doc}`forms` —— 放进 `card_content` 里的表单控件。
