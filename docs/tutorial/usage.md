# 用法

每个组件都是一个普通的 NiceGUI 元素，但构造参数比 `ui.*` 丰富一些：枚举式的 `variant=` /
`size=`、一个会做冲突合并的 `classes=`，以及照常透传的 NiceGUI 原生关键字参数。

## `classes=` 关键字

用法与 shadcn 的 `cn()` 完全一致：你传入的 class 会通过 `tailwind-merge` 与组件自带的
class 合并，并且**以你的为准**。

```python
shadcn.button('Save')                            # bg-primary text-primary-foreground …
shadcn.button('Save', classes='bg-destructive')  # 红色胜出，不是两者都有
shadcn.button('Save', classes=['w-full', 'mt-4'])
```

合并的优先级是三级，从低到高：

1. 组件自带的 class（`default_classes=`）；
2. 由 `variant=` / `size=` 等枚举参数算出来的 class（内部叫 `variant_classes`）；
3. 你通过 `classes=` 传入的 class。

所以 `classes=` 能覆盖任何东西，包括枚举参数的选择结果：

```python
shadcn.button('Save', variant='outline', classes='bg-primary')  # 仍然是你赢
```

## `variant=` 与 `size=` 枚举参数

凡是带样式的变体，都是显式声明的关键字参数，取值在源码里校验；传错会立刻抛出一个列出全部
合法取值的 `ValueError`：

```
ValueError: Unknown button variant 'danger'. Valid options are: 'default', 'destructive', 'outline', 'secondary', 'ghost', 'link'
```

| 组件 | 枚举参数 | 合法取值 |
| --- | --- | --- |
| `shadcn.button` | `variant` | `default`、`destructive`、`outline`、`secondary`、`ghost`、`link` |
| `shadcn.button` | `size` | `default`、`sm`、`lg`、`icon` |
| `shadcn.badge` | `variant` | `default`、`secondary`、`destructive`、`outline` |
| `shadcn.alert` | `variant` | `default`、`destructive` |
| `shadcn.avatar` | `size` | `default`、`sm`、`lg`、`xl` |
| `shadcn.separator` | `orientation` | `horizontal`、`vertical` |
| `shadcn.dialog_content` | `side` | `center`、`top`、`right`、`bottom`、`left` |
| `shadcn.popover_content` | `side` / `align` | `top`/`right`/`bottom`/`left`、`start`/`center`/`end` |
| `shadcn.tooltip` | `side` | `top`/`right`/`bottom`/`left` |

只接受默认值、没有枚举的组件（`card`、`separator` 之外的布局元素、表格家族等）就不带这些
参数 —— 直接核对 {doc}`components` 里的表。

## NiceGUI 原生关键字参数照常透传

除了上面这些，构造函数会把其余关键字参数原样交给 `Element`。每个组件都是真正的
`nicegui.element.Element`，因此标准工具箱原封不动就能用：

| 能力 | 写法 |
| --- | --- |
| 事件绑定 | `.on('click', handler)`、`.on_value_change(handler)` |
| 双向绑定 | `.bind_value(obj, 'attr')`、`.bind_text_from(obj, 'attr')` |
| 提示气泡 | `.tooltip('…')` |
| 追加 class | `.classes('mt-4')`、`.classes(replace='mt-8')` |
| 合并 class | `.with_classes('mt-4')` |
| 内联样式 | `.style('width: 12rem')` |
| 透传 prop | `.props('flat')` |
| 移动节点 | `.move(target, …)` |
| 启用/禁用 | `.set_enabled(False)` |
| 可见性 | `.visible = False` |
| 插槽 | `.add_slot('…', …)` |
| 当前上下文 | `ui.context` |

此外，任何 shadcn 组件都能直接放进 `ui.row()` / `ui.column()` / `with` 块里，和原生组件
混用。

## `.classes()` 是追加，不合并 —— 这是一个无声陷阱

NiceGUI 自己的 `.classes(...)` 行为**没有变**，它仍然是追加：

```python
btn = shadcn.button('Save')
btn.classes('mt-4')          # 追加，不做冲突解决
btn.classes(replace='mt-8')  # NiceGUI 的 replace 仍然有效
```

问题出在追加与已有 class 冲突时：两个工具类都会出现在 `class` 属性里，由**样式表里的顺序**
决定谁生效，而这未必是你想要的。最典型的例子是 `Card`：

```python
shadcn.card().classes('p-0')   # 看起来想去掉内边距，实际上不会生效
```

`Card` 自带 `py-6`，而编译产物把 `.p-0` 排在 `.py-6` **之前**，于是 1.5rem 的垂直内边距
依然保留。这是无声的：没有异常、没有警告，class 也确实写进了属性里，只是没赢得竞争。

:::{warning}
不熟悉 `tailwind-merge` 的冲突组时，请不要用 `.classes()` 覆盖组件已有的样式。凡是想
**替换**而不是**追加**，一律用 `.with_classes()`。
:::

## `.with_classes()` —— 会合并的版本

`.with_classes(...)` 走的是同一套 `tailwind-merge`，返回元素本身，因此可以链式调用：

```python
shadcn.card().with_classes('p-0')           # py-6 被逐出，p-0 生效
shadcn.card().with_classes('rounded-full')  # rounded-xl 被逐出
card = shadcn.card().with_classes('p-0 mt-4')
```

它也能在构造之后单独调用：

```python
card = shadcn.card()
card.with_classes('p-0')
```

一句话的规则：**构造期用 `classes=`，构造之后用 `.with_classes()`**，只有在确实想要
“两个类都在、让样式表裁决”时才用 `.classes()`。

## `classes=` 能依赖哪些 class

样式表是预编译的，所以 `classes=` 只能作用于**构建时已经生成**的 class。可以放心依赖的
范围是：

- 组件自身用到的每一个 class；
- shadcn 的语义化颜色，包括基础形式和常见变体 —— `bg-primary`、`text-muted-foreground`、
  `dark:border-input`、`hover:bg-accent`、`data-[state=open]:bg-accent` 等；
- 一套精选的布局 / 间距 / 排版词汇 —— `w-full`、`mt-4`、`px-8`、`gap-3`、`text-center`、
  `rounded-full`、`shadow-lg`、`grid-cols-3` 等。

**在此之外的任何东西**都需要重新构建样式表才能使用，最典型的是原始调色板颜色：

```python
shadcn.button('Save', classes='bg-blue-600')   # 不会有任何效果
```

因为 `bg-blue-600` 不在 `@source inline(...)` 的词汇表里，编译产物里根本没有这条规则。
要使用它，走 {doc}`/start/styling` 里的扩展流程 —— 向 `frontend/tailwind.css` 追加一条
指向你自己应用的 `@source`，例如 `@source inline("bg-blue-600")`，然后用 Tailwind CLI 重新
编译。想确认某个 class 到底可不可用，直接去 `nicegui_shadcn/static/shadcn.css` 里搜一下
就好。

## 选项与菜单项的四种写法

`select`、`radio_group`、`toggle_group`、`tabs_list`、`dropdown_menu` 的 `options` /
`tabs` / `items` 参数接受同一种规范化格式，共四种写法：

```python
shadcn.select(['system', 'light', 'dark'])                     # value == label
shadcn.select({'system': 'System', 'light': 'Light'})          # value -> label
shadcn.select([('system', 'System'), ('light', 'Light')])      # (value, label) 对
shadcn.select([{'value': 'system', 'label': 'System', 'disabled': False}])
```

字典写法是唯一能同时带 `disabled`、`kind`、`variant` 的形式。`(value, label)` 二元组只产出
value 与 label，不带其它字段。

## 下一步

- {doc}`layout`、{doc}`forms`、{doc}`display`、{doc}`disclosure`、{doc}`overlays` —— 按类型
  看具体组件。
- {doc}`components` —— 完整的组件清单与参数表。
- {doc}`limitations` —— `classes=` 边界的成因与其它设计取舍。
