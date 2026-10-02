# 图标

本库把它需要的那几个 [Lucide](https://lucide.dev) 图标直接内联在 Python 里，因此不随包发布
任何图标 bundle。全部图标都是 24×24 的描边路径，用 `currentColor` 上色 —— 它们会继承文字
颜色，也能被 Tailwind 的尺寸工具类缩放。

## 全部图标名

`nicegui_shadcn.icons.ICON_NAMES` 是唯一权威列表，共 **39** 个：

| 分组 | 图标名 |
| --- | --- |
| 方向 | `arrow-down`、`arrow-left`、`arrow-right`、`arrow-up`、`chevron-down`、`chevron-left`、`chevron-right`、`chevron-up`、`chevrons-up-down` |
| 状态 | `check`、`circle`、`circle-check`、`circle-x`、`info`、`triangle-alert`、`loader-circle`、`minus`、`plus`、`x` |
| 操作 | `copy`、`download`、`upload`、`search`、`settings`、`trash-2`、`external-link`、`eye`、`eye-off`、`ellipsis`、`ellipsis-vertical` |
| 界面 | `menu`、`panel-left`、`bell`、`calendar`、`mail`、`user`、`github` |
| 主题 | `moon`、`sun` |

```python
from nicegui_shadcn import icons

icons.ICON_NAMES          # ('arrow-down', 'arrow-left', …)
len(icons.ICON_NAMES)     # 39
```

想用列表之外的图标，需要往 `nicegui_shadcn/icons.py` 的 `_ICONS` 里加一项再重新构建。这些
图标是**手工内联进 Python 的**，并不是从 `lucide-vue-next` 打包来的 —— `package.json` 里
虽然列了这个包，但它不参与运行期资源，所以没有“随手写个 Lucide 名字就能用”的通道。

## `icons.svg()` —— 拿到原始标记

```python
def svg(name: str, *, size: int | float = 16, stroke_width: float = 2,
        classes: str = '', **attrs: object) -> str
```

它返回一段 `<svg …>` 字符串：

```python
from nicegui import ui
from nicegui_shadcn import icons

ui.html(icons.svg('github', size=24), sanitize=False)
```

`sanitize=False` 是必需的 —— 否则 NiceGUI 会把 SVG 标记当成不安全的 HTML 处理掉。产物大致
长这样：

```html
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
     stroke-linejoin="round" class="lucide lucide-github" aria-hidden="true">…</svg>
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `name` | — | 图标名，**必填** |
| `size` | `16` | 同时写成 `width` 与 `height` 属性 |
| `stroke_width` | `2` | 描边粗细 |
| `classes` | `''` | 追加到 `class` 属性（基础值是 `lucide lucide-<name>`） |
| `**attrs` | — | 额外属性；键里的 `_` 会转成 `-`，尾部 `_` 会被去掉 |

```python
icons.svg('check', size=20, classes='text-primary')
icons.svg('loader-circle', classes='animate-spin')
icons.svg('arrow-right', data_testid='go')      # 渲染成 data-testid="go"
```

:::{warning}
传一个不存在的名字会抛 `KeyError`，错误信息里带着全部 39 个合法名字：

```
KeyError: unknown icon 'trash'; available: arrow-down, arrow-left, …
```

注意 `trash` 不存在，正确名字是 `trash-2`。
:::

## `shadcn.icon()` —— 作为元素使用

`icons.svg()` 返回的是字符串，`shadcn.icon()` 则把它包成一个真正的 NiceGUI 元素（一个
`ui.html`，`tag='span'`），因此可以放进 `with` 块、被 `.move()`、被绑定：

```python
from nicegui_shadcn import shadcn

with ui.row().classes('items-center gap-2'):
    shadcn.icon('info')
    shadcn.icon('circle-check', size=20, classes='text-primary')
```

```python
def icon(name: str, *, size: int | float = 16, classes: str = '', **attrs: Any) -> ui.html
```

`classes` 会在构造之后经 `.classes()` 追加。注意它与其他 `shadcn.*` 组件不同：返回的不是
`ShadcnElement`，而是原生 `ui.html`，因此**没有** `with_classes()`。

## 在组件里用图标

带 `icon` 参数的组件会自己调用 `icons.svg()`，标签名直接写字符串即可：

```python
shadcn.button('Delete', icon='trash-2', variant='destructive')
shadcn.button('Next', icon='arrow-right', icon_position='right', variant='outline')
shadcn.button('Icon only', icon='settings', size='icon')      # 标签变成 sr-only
shadcn.alert(title='Saved', icon='circle-check')              # 覆盖默认图标
```

几个要点：

- **`icon_position`** 默认是 `'left'`，可选 `'right'`。它只影响图标相对标签的位置。
- **`size='icon'`** 会把标签文字放到 `sr-only`（只对屏幕阅读器可见），并给按钮加
  `aria-label`。如果 `size='icon'` 且只给了 `icon` 没给 `text`，`aria-label` 会自动取图标名。
- **`loading=True`** 会在标签前面插一个旋转的 `loader-circle`，同时禁用按钮。
- 组件内的 SVG 由 `[&_svg]:size-4` 统一控制尺寸，所以按钮里的图标是无视 `size` 参数的 ——
  想让按钮里的图标更大，得调按钮的 `size`。

## 当前可用的图标名（完整清单）

```
arrow-down        arrow-left        arrow-right       arrow-up
bell              calendar          check             chevron-down
chevron-left      chevron-right     chevron-up        chevrons-up-down
circle            circle-check      circle-x          copy
download          ellipsis          ellipsis-vertical external-link
eye               eye-off           github            info
loader-circle     mail              menu              minus
moon              panel-left        plus              search
settings          sun               trash-2           triangle-alert
upload            user              x
```

## 下一步

- {doc}`dark-mode` —— `moon` / `sun` 两个图标最常见的用途。
- {doc}`components` —— 哪些组件接受 `icon=` 参数。
