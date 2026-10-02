# 深色模式

深色模式完全交给 NiceGUI 自己的开关 —— 本库不引入任何额外的状态管理。Tailwind 的 `dark:`
变体被绑定到 NiceGUI 已经在切换的那个 class 上，shadcn 的设计 token 则在对应的选择器下重新
定义。

## 一行代码

```python
from nicegui import ui

ui.dark_mode().bind_value(state, 'dark')   # 或者：ui.dark_mode(True)
```

`ui.dark_mode()` 是 NiceGUI 自己的 `ValueElement`：

| 写法 | 效果 |
| --- | --- |
| `ui.dark_mode()` | 默认关闭（`value=False`） |
| `ui.dark_mode(True)` | 立即开启 |
| `ui.dark_mode(None)` | 跟随系统偏好（auto） |
| `.enable()` / `.disable()` | 设为开启 / 关闭 |
| `.toggle()` | 取反；**auto 模式下会抛 `ValueError`** |
| `.auto()` | 切回跟随系统 |
| `.bind_value(obj, 'dark')` | 与任意数据对象双向绑定 |

:::{note}
`ui.dark_mode()` 会覆盖 `ui.run(dark=…)` 与页面装饰器上的 `dark` 参数。页面上只放一个
`ui.dark_mode()` 就够了。
:::

## 它是怎么生效的

`ui.dark_mode()` 切换的是 `<body>` 上的 `body--dark` class。样式表里的 `dark` 变体正是绑定
到它：

```css
@custom-variant dark (&:where(body.body--dark, body.body--dark *));
```

这也是 NiceGUI 自己的 `templates/index.html` 里用的写法，属于刻意保持一致。

设计 token 在同样的钩子下被重新定义，而且两个钩子都有效：

```css
/* Both hooks work: NiceGUI's own `body--dark` and shadcn's conventional `.dark`. */
body.body--dark,
.dark {
  --primary: oklch(0.922 0 0);        /* 浅色模式下是 oklch(0.205 0 0) */
  --background: oklch(0.145 0 0);
  --border: oklch(1 0 0 / 10%);       /* 深色下边框是半透明白 */
}
```

## 为什么组件不需要任何配合

`@theme inline` 把每个 shadcn token 暴露成一个 Tailwind 颜色：

```css
@theme inline {
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
}
```

于是 `bg-primary` 编译成的规则读的是 `var(--primary)`，而 `--primary` 的值随 `body--dark`
改变。切换深色模式时**没有任何 class 变化** —— 只是 CSS 变量换了值，所有 shadcn 组件自动
跟着变。这也是为什么 `#fff` 或 `bg-blue-600` 这类硬编码颜色不会跟随主题：它们不引用变量。

| token 家族 | 深色模式下的变化 |
| --- | --- |
| `background` / `foreground` | 白底黑字 → 近黑底近白字 |
| `card` / `popover` | 纯白 → 比背景稍亮一层的近黑 |
| `primary` / `primary-foreground` | 近黑 / 近白 → 近白 / 近黑（按钮反色） |
| `secondary` / `muted` / `accent` | 浅灰 → 深灰 |
| `border` / `input` | 实心浅灰 → 半透明白（`oklch(1 0 0 / 10%)`） |
| `destructive` | 稍作提亮以适应深色背景 |
| `chart-1` … `chart-5` | 整套换成深色背景下的可读版本 |

## 局部深色

因为变体是 `:where(body.body--dark, body.body--dark *)`，在 `body--dark` 之下，**整个子树**
都处于深色模式；反过来，手动给任意容器加 `.dark` class 也能让那棵子树深色：

```python
with ui.card().classes('dark'):
    shadcn.button('This subtree is dark')
```

这个钩子主要是为了和 shadcn 生态里按 `.dark` 切换的方案兼容，正常使用不需要它。

## 一个切换按钮

```python
from nicegui import ui
from nicegui_shadcn import shadcn

dark = ui.dark_mode()

with shadcn.button(icon='moon', size='icon', variant='outline',
                   on_click=lambda: dark.toggle()) as toggle:
    toggle.props('aria-label="切换深色模式"')
```

想让图标随状态变化，用 NiceGUI 的可见性绑定：

```python
with shadcn.button(size='icon', variant='ghost', on_click=dark.toggle):
    sun = shadcn.icon('sun')
    moon = shadcn.icon('moon')
    dark.bind_value(sun, 'visible', lambda v: not v)
    dark.bind_value(moon, 'visible', lambda v: bool(v))
```

:::{tip}
`sun` 与 `moon` 都在 {doc}`icons` 的 39 个图标里。因为图标用 `currentColor` 上色，它们会
自动跟随当前主题，不需要任何额外处理。
:::

## 与 Quasar 混用时的注意点

shadcn 的 token 与 Quasar 的 token 是两套独立变量（两者都定义了 `--primary`）。shadcn 的
工具类之所以能压过 Quasar，是因为它们被输出到 `layer(utilities) important` 中；而
`ui.notify`、`ui.dialog`、`ui.menu` 这类 Quasar 自带的组件仍然使用 Quasar 自己的配色。

结果是：**在深色模式下切换主题，Quasar 组件与 shadcn 组件会各自按自己的规则变化**，视觉上
可能出现两种不同的“深色”。细节见 {doc}`limitations`。

## 下一步

- {doc}`usage` —— 想在深色模式下微调配色（例如 `dark:bg-accent`）时，先看 `classes=` 的
  边界。
- {doc}`limitations` —— 与 Quasar 共存带来的取舍。
