# 主题（theming）

shadcn 的“主题”不是一套皮肤，而是一组 CSS 变量：组件本身只引用
`var(--primary)`、`var(--radius)` 这类名字，具体是什么颜色由被引用的变量决定。本库把这组
变量编译进 `static/shadcn.css`，同时提供 `nicegui_shadcn.theming`，让你在**运行期**替换
它们 —— 不需要重新构建，也不需要重启。

## 主题就是一组 token

| token 家族 | 作用 | 深色模式下的变化 |
| --- | --- | --- |
| `background` / `foreground` | 页面底色与正文色 | 白底黑字 → 近黑底近白字 |
| `card` / `card-foreground` | 卡片面与卡片上的文字 | 纯白 → 比背景稍亮一层 |
| `popover` / `popover-foreground` | 浮层面板 | 同上 |
| `primary` / `primary-foreground` | 高强调动作（主按钮）、品牌面 | 近黑 / 近白 → 近白 / 近黑 |
| `secondary` / `muted` / `accent` | 次级面、弱化面、hover/focus 面 | 浅灰 → 深灰 |
| `destructive` / `destructive-foreground` | 危险动作 | 提亮以适应深色底 |
| `border` / `input` / `ring` | 描边、输入框边、焦点环 | 实心浅灰 → 半透明白 |
| `chart-1` … `chart-5` | 图表配色 | 整套换成深色可读版本 |
| `sidebar*` | 侧边栏专用的 8 个 token | 同上 |
| `radius` | 所有圆角的基准值 | 不随模式改变 |

`destructive-foreground` 是本库随包提供的：shadcn 现在的注册表里已经没有它，所以
`use_base_color()` 会保留这个 token 不动，而 `set_colors()` 仍然可以改它。

组件为什么不需要任何配合，见 {doc}`dark-mode` —— 一句话：`bg-primary` 编译成
`background-color: var(--primary) !important`，所以换掉 `--primary` 就等于换掉所有主按钮。

## 三种改法

| 想做什么 | 用什么 | 生效时机 |
| --- | --- | --- |
| 换成 shadcn 官方的另一套基础色 | `theming.use_base_color('zinc')` | 立即 |
| 微调某几个 token | `theming.set_colors(primary='#2563eb')` | 立即 |
| 改圆角基准 | `theming.set_radius(0.75)` | 立即 |
| 加一个 shadcn 没有的语义色 | `theming.add_color('warning', …)` | 立即 |
| 回到编译进样式表的默认主题 | `theming.reset()` | 立即 |

所有函数都作用于**整个应用**（它们是全局状态），所以在页面里调用会连同其他已打开的页面一起
改变 —— 这正好是做主题选择器想要的行为。

## 整套换色：`use_base_color()`

shadcn 发布 7 套基础色，本库把它们的 `cssVarsV4`（oklch）离线抓取到
`nicegui_shadcn/static/base-colors.json`：

| 名字 | 观感 |
| --- | --- |
| `neutral` | 纯灰，零彩度 —— 也就是本库默认主题用的那一套 |
| `stone` | 暖灰，略带黄 |
| `zinc` | 冷灰，略偏蓝紫 |
| `mauve` | 灰紫 |
| `olive` | 灰绿 |
| `mist` | 灰蓝 |
| `taupe` | 灰棕 |

```python
from nicegui_shadcn import theming

theming.use_base_color('zinc')
```

这一下会替换掉整套 31 个语义 token（浅色与深色各一份），包括 `chart-1` … `chart-5`。
用 `set_colors()` 做过的覆盖会被丢弃，用 `add_color()` 加的颜色会保留。

:::{note}
注册表里的 `chart-1` … `chart-5` 是**单色灰阶**（带基础色色相的灰），而且同一套色的浅色与
深色取值完全相同；而 shadcn 文档中「Default Theme CSS」给的是鲜艳的多色图表。本库编译进
`shadcn.css` 的默认值采用文档脚手架的鲜艳值，`use_base_color()` 则原样套用注册表 —— 两者
在图表配色上会有可见差异。
:::

:::{tip}
`--radius` 也属于基础色（7 套在注册表里都是 `0.625rem`）。`use_base_color()` 会套用它，
**但如果你调用过 `set_radius()`，你设定的值会被保留** —— 否则一个实时换色按钮会把用户调好的
圆角打回去。
:::

## 微调单个 token：`set_colors()`

```python
theming.set_colors(primary='#2563eb', ring='#93c5fd')
theming.set_dark_colors(primary='#60a5fa')
```

关键字名就是上表的 token，把连字符写成下划线即可（`card_foreground='#111'`）。浅色与深色是
两组独立的值：**`set_colors()` 不动深色**，所以想让一个颜色两种模式都变，需要同时调用
`set_dark_colors()`。写错 token 名会直接抛 `ValueError`，并在消息里给出最接近的候选：

```text
set_colors() got an unknown colour token 'primry'. Did you mean 'primary'? See nicegui_shadcn.theming.COLOR_TOKENS for the full list.
```

## 改圆角：`set_radius()`

`--radius` 是唯一一个其它圆角都由它派生的 token。`@theme inline` 里的阶梯是 shadcn 官方的
比例式：

| 工具类 | 值 | `--radius: 0.625rem` 时 |
| --- | --- | --- |
| `rounded-xs` | `calc(var(--radius) * 0.4)` | 4px |
| `rounded-sm` | `calc(var(--radius) * 0.6)` | 6px |
| `rounded-md` | `calc(var(--radius) * 0.8)` | 8px |
| `rounded-lg` | `var(--radius)` | 10px |
| `rounded-xl` | `calc(var(--radius) * 1.4)` | 14px |
| `rounded-2xl` | `calc(var(--radius) * 1.8)` | 18px |
| `rounded-3xl` | `calc(var(--radius) * 2.2)` | 22px |
| `rounded-4xl` | `calc(var(--radius) * 2.6)` | 26px |

`xs` 是 shadcn 官方阶梯之外补的一档（比例延续 0.6 − 0.2），这样那个恰好用到它的组件
（对话框右上角的关闭按钮）也会跟着主题变。

```python
theming.set_radius(0.75)      # 数字 = rem
theming.set_radius('12px')    # 或者直接给 CSS 长度
```

:::{warning}
裸 `rounded`（也就是 Tailwind 的默认 `--radius`）在编译产物里是**写死的 `0.25rem`** ——
Tailwind v4 会把没有在 `@theme` 里重新声明的变量的值内联进去，所以 `rounded`、`rounded-t`、
`rounded-s` 这类不带尺寸后缀的工具类不会跟随 `--radius`。需要跟随主题时请用
`rounded-sm` / `rounded-lg` 等带后缀的写法（组件默认用的就是它们）。
:::

## 加一个 shadcn 没有的颜色：`add_color()`

```python
theming.add_color('warning', light='#f59e0b', dark='#fbbf24',
                  foreground_light='#1c1917')
```

这会做两件事：定义 `--warning`（以及 `--warning-foreground`，两个模式各一份），并生成配套的
工具类：

| 生成的工具类 | 编译出的声明 |
| --- | --- |
| `bg-warning` | `background-color: var(--warning) !important` |
| `text-warning` | `color: var(--warning) !important` |
| `border-warning` | `border-color: var(--warning) !important` |
| `ring-warning` | `--tw-ring-color: var(--warning) !important` |
| `fill-warning` / `stroke-warning` | `fill` / `stroke` |
| `outline-warning` | `outline-color` |
| `divide-warning` | `:where(.divide-warning > :not(:last-child))` 的 `border-color` |

以及每一个的 `dark:` 变体（例如 `dark:bg-warning`）。只给一侧 foreground 时，另一侧会自动
复制同一个值。

```python
shadcn.badge('Beta').classes('bg-warning text-warning-foreground')
```

:::{important}
生成的工具类都被包在 `@layer utilities { … }` 里并带 `!important`，这一点是必须的：NiceGUI
在 `templates/index.html` 里声明的层序把 Quasar 的 `!important` 放在最后，而 `!important`
声明的层序是**反转**的（先声明的层获胜）。Quasar 恰好自带 `.bg-warning`，如果不加这一层，
你的 amber 会被 Quasar 的 `#f2c037` 压掉。
:::

:::{note}
出于体积考虑，`add_color()` 只生成**基础档与 `dark:` 档**，不生成 `hover:`、`focus:`、
`focus-visible:`、`active:`、`disabled:`、`group-hover:` 等变体。要改的是内置 token 时请用
`set_colors()` —— 官方样式表里已经带全了这套矩阵，改值即可。
:::

## 实时切换

`theming` 的注入策略分两个阶段：

- **NiceGUI 启动之前**的调用会被**合并成一次注入**。一个页面在 `@ui.page` 函数外连续调用
  `use_base_color()`、`set_radius()`、`set_colors()`，`Client.shared_head_html` 里只会多出
  一份样式快照。
- **启动之后**的调用会立即推送，并且把同一个小片段广播给所有**已经连上**的页面，它们无需刷新
  就会重新上色。片段的做法是删掉旧的 `style#nicegui-shadcn-theme` 再插入新的，所以反复切换
  也只会留下一份。

一个基础色选择器可以就这么写：

```python
from nicegui import ui
from nicegui_shadcn import shadcn, theming

for name in theming.BASE_COLORS:
    shadcn.button(name, variant='outline',
                  on_click=lambda name=name: theming.use_base_color(name))
```

:::{note}
广播只发给已经建立 websocket 连接的页面（`Client.has_socket_connection`），而且需要事件循环
在运行 —— 也就是说，在 `ui.run()` 之前的调用只影响之后渲染的页面，不会报错。
:::

## API 速查

| 函数 | 说明 |
| --- | --- |
| `use_base_color(name)` | 套用一套官方基础色（7 选 1），保留 `add_color()` 加的颜色 |
| `set_colors(**tokens)` | 覆盖浅色 token，关键字用下划线 |
| `set_dark_colors(**tokens)` | 覆盖深色 token |
| `set_radius(value)` | 设置 `--radius`，数字按 rem，也可传 CSS 长度 |
| `add_color(name, light, dark, *, foreground_light=None, foreground_dark=None)` | 定义新颜色并生成工具类 |
| `reset()` | 丢弃全部覆盖，回到编译进样式表的默认主题 |
| `current()` | 以普通 dict 返回当前主题（`radius` / `light` / `dark` / `colors`） |
| `css()` | 返回当前会注入的样式表；什么都没设置时返回 `''` |
| `BASE_COLORS` | 7 个基础色名字的元组 |
| `COLOR_TOKENS` | 32 个 token 名字的元组 |

`css()` 可以用来检查实际注入了什么，也可以把主题写成真正的样式表文件：

```python
from pathlib import Path

Path('my-theme.css').write_text(theming.css(), encoding='utf-8')
```

## 边界与注意

- **值必须是 CSS 颜色字符串**。传数字会抛 `TypeError`；值里出现 `;`、`{`、`}`、`<`、`>`
  也会被拒绝 —— 它们会被注入 `<style>` 元素，允许出现就等于允许注入任意 CSS。
- **`add_color()` 的名字必须是 kebab-case**，且不能撞上 32 个内置 token（会提示改用
  `set_colors()`）。
- **Quasar 与 shadcn 是两套独立变量**。`theming` 只改 shadcn 那一套；`ui.notify`、
  `ui.dialog`、`ui.menu` 这类 Quasar 组件仍用 Quasar 自己的配色。详见 {doc}`limitations`。
- **主题是全局状态**，不是每个页面一份。多页面应用里所有页面共享同一份设置。
- 想在**构建期**定死主题（例如不引入运行期脚本），直接改 `frontend/tailwind.css` 里的
  `:root` 与 `body.body--dark, .dark` 两块，然后 `npm run build` —— 见 {doc}`/start/styling`。

## 下一步

- {doc}`dark-mode` —— 深色模式本身的开关与局部深色。
- {doc}`/start/styling` —— 样式表是怎么编译出来的，以及怎么改编译期的默认主题。
- {doc}`limitations` —— 与 Quasar 共存带来的取舍。
