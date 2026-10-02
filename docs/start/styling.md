# 样式与主题

本页讲这套组件集的样式是从哪来的、为什么长这样、以及你在什么情况下必须重新编译它。
如果你只是想在自己的页面上写 Tailwind 类，看 {doc}`/tutorial/usage` 与 {doc}`/tutorial/limitations`。

## 一个前提：CSS 是预编译产物

用户安装这个库时**不需要 Node、不需要 Tailwind、不需要任何构建步骤**。原因是产物已经提交在仓库里：

| 文件 | 大小 | 内容 |
| --- | --- | --- |
| `nicegui_shadcn/static/shadcn.css` | 192,160 B | design token + 用得到的工具类 |
| `nicegui_shadcn/static/vendor/reka-ui.js` | 282,749 B | 打包好的 reka-ui 原语 |

运行期不存在 JIT：浏览器拿到的 CSS 是一个静态文件，里面有什么类就是什么类。
这一点决定了本库 90% 的「诡异行为」——**没有的类不会报错，只会没有样式**。

## 样式是怎么被加载的

`nicegui_shadcn/theme.py` 负责三件事，全部发生在 `import nicegui_shadcn` 的那一刻
（文件末尾第 84 行的裸调用 `setup()`）：

```python
def setup() -> None:
    global _installed
    if _installed:
        return
    _installed = True

    app.add_static_files(URL_PREFIX, str(STATIC_DIR))
    register_importmap_override(REKA_UI_SPECIFIER, REKA_UI_URL)
    ui.add_head_html(_HEAD_HTML, shared=True)
```

- `URL_PREFIX = '/_nicegui_shadcn'`（`theme.py:47`），`STATIC_DIR` 就是上面那张表里的目录（`theme.py:45`）。
- 样式表 URL 是 `theme.py:50` 的 `CSS_URL`，实际注入的标记是 `theme.py:59` 的：

```python
_HEAD_HTML = f'<link rel="stylesheet" href="{CSS_URL}">'
```

- `setup()` 是幂等的（`theme.py:61,74-77`），所以既能靠导入自动生效，也能在惰性导入的场景里手动调一次。
  它被列在 `theme.py:42` 的 `__all__` 里。

用 `<link>` 而不是 `ui.add_css` 是有意的：`add_css` 会把整份样式表内联进每个页面的 HTML，
而 192 kB 的文件应该走浏览器缓存。细节见 {doc}`/tutorial/how-it-works`。

## `frontend/tailwind.css` 的结构

源文件在 `frontend/tailwind.css`（295 行），它**不在可导入的包里**（`frontend/` 只进 sdist，见 {doc}`packaging`），
编译命令是 `package.json` 里的 `build:css`：

```bash
tailwindcss -i ./frontend/tailwind.css -o ./nicegui_shadcn/static/shadcn.css
```

### 只导入 `theme` 和 `utilities`，不导入 preflight

```css
@import "tailwindcss/theme.css" layer(theme);
@import "tailwindcss/utilities.css" layer(utilities) source(none) important;
@import "tw-animate-css";
```

文件头部第 8-10 行的注释说明了原因：NiceGUI 已经加载了 Quasar 自己的 normalize
（`quasar.unimportant.css`），再加一份 Tailwind preflight 会互相打架。
preflight 里唯一真正需要的规则——`[hidden]` 要真的隐藏——被手写进了 `@layer base`（见下）。

### `important` 不是装饰

第 20-34 行的注释记录了这条约定，值得完整理解：

NiceGUI 在 `templates/index.html` 里导入 Quasar 的颜色助手：

```css
@import url("quasar.important.css") layer(quasar_importants);
```

而那个文件里有 `.bg-primary { background: var(--q-primary) !important; }`。
`!important` 会压过任何普通声明，**无论它在哪一层**；
而层优先级对 important 声明是**反转**的，所以只要我方声明也是 important，
声明在 `quasar_importants` **之前**的 `utilities` 层反而赢。没有这个 `important`，
`shadcn.button()` 会长成 Quasar 蓝，而不是 shadcn 的近黑 `--primary`。

NiceGUI 声明的完整层序（`nicegui/templates/index.html:13`）：

```css
@layer theme, base, quasar, nicegui, components, utilities, overrides, quasar_importants;
```

### 暗色变体绑定在 `body.body--dark` 上

```css
@custom-variant dark (&:where(body.body--dark, body.body--dark *));
```

NiceGUI/Quasar 表达深色模式的方式就是在 `<body>` 上加 `body--dark` 类，
所以 `dark:` 前缀等价于 `body.body--dark` 下的任意元素。用户侧用法见 {doc}`/tutorial/dark-mode`。

### 设计 token：`:root` 与 `body.body--dark`

两套变量分别在 `frontend/tailwind.css:66-103` 和 `:106-142`，全部用 `oklch()`，
默认是 shadcn 的 neutral 基础色：

```css
:root {
  --radius: 0.625rem;
  --primary: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  /* … */
}

body.body--dark,
.dark {
  --border: oklch(1 0 0 / 10%);
  /* … */
}
```

这些是 **shadcn 自己的变量**，不是 Quasar 的 `--q-primary`。两套调色板会同时存在于页面上，
所以「把 Quasar 的 `q-btn` 和 shadcn 的 `button` 混着用」时颜色对不上是预期行为。

### `@theme inline`：把变量暴露成 Tailwind 的调色板

`:144-192` 把上面那些变量接到 Tailwind 的命名空间上：

```css
@theme inline {
  --color-primary: var(--primary);
  --radius-sm: calc(var(--radius) - 4px);
  --font-sans: /* … */;
  --animate-accordion-down: accordion-down 0.2s ease-out;
}
```

`inline` 是关键：它让生成的工具类里出现的是 `var(--primary)` 而不是把当前值烤进去，
所以深色模式下切换 `body--dark` 就能立刻生效。
**只有在这里被别名过的 token 才会产生工具类**——例如 `--color-input` 存在，`bg-input/30` 才有意义。

`@keyframes accordion-down/up`（`:194-202`）用 `var(--reka-accordion-content-height)`，
由 reka 在展开时写入。

### `@layer base` 里的两条规则

`:214-232` 只有两件事：

```css
@layer base {
  * { border-color: var(--border); outline-color: color-mix(in oklab, var(--ring) 50%, transparent); }
  [hidden] { display: none !important; }
}
```

第一条补的是缺失的 preflight：Tailwind 的 `border` / `border-2` 只设置**宽度**，
颜色来自 shadcn 的 preflight，而我们跳过了它；没有这条，`border` 会得到浏览器默认的 `currentColor`。

第二条是浮层能正常工作的前提。本库让关闭后的面板留在 DOM 里（为了保住表单状态），
reka 只设置 `data-state`，隐藏靠元素上的 `hidden` 属性——
而 Tailwind 的 `display: flex` 会压过浏览器的 UA 规则 `[hidden] { display: none }`。
没有这条 `!important`，所有 tab 面板会同时可见。代价是 accordion 没有关闭动画。

### 一个可选的页面级辅助类

```css
.nicegui-shadcn-surface {
  background-color: var(--background);
  color: var(--foreground);
}
```

`:238-241`。想让整页使用 shadcn 的背景/前景色（而不是 Quasar 的）时，把它加到页面容器上。

## 类词汇表是「显式的子集」

### `source(none)` 让产物成为纯函数

```css
@import "tailwindcss/utilities.css" layer(utilities) source(none) important;
```

`source(none)` 关掉了 Tailwind v4 的自动内容探测。否则 Tailwind 会扫描整个 checkout
（README 里的代码片段、测试、示例），产物就取决于构建时的工作目录。
关掉之后，**产出的 CSS 是下面这些显式 `@source` 规则的纯函数**，
所以「改了源码但忘了重建」可以被 `git status` 抓出来。

### 四个 `@source` glob

```css
@source "../nicegui_shadcn/elements/**/*.vue";
@source "../nicegui_shadcn/elements/**/*.py";
@source "../nicegui_shadcn/*.py";
@source "../examples/**/*.py";
```

`:52-57`。路径相对于 `frontend/tailwind.css` 自身。
也就是说：**写在 Python 里的类字符串会被编译器当成「用法」扫描到**。
`strict` 的正则并不存在，Tailwind 只是在文件里找候选字符串，
所以任何出现在 `.py` / `.vue` 里的形如工具类的词都会进入产物。

### 运行期词汇表：`@source inline(...)`

用户会在运行期写 `ui.button(...).classes('mt-8')`，这些字符串不在任何文件里，编译器看不见。
`frontend/tailwind.css:267-295` 用 29 条 `@source inline(...)` 声明了刻意挑选的子集，
覆盖间距、尺寸、排版、圆角、边框、阴影、布局、过渡等常用族，例如：

```css
@source inline("{p,px,py,pt,pr,pb,pl,m,mx,my,mt,mr,mb,ml,gap,gap-x,gap-y}-{0,1,2,3,4,5,6,8,10,12,16}");
@source inline("{flex,grid,block,inline-block,inline,hidden,contents}");
@source inline("rounded{,-none,-sm,-md,-lg,-xl,-2xl,-3xl,-full,-t,-r,-b,-l,-tl,-tr,-br,-bl}");
```

### 语义色的三块 `inline`

`:249-251` 单独展开语义色（`bg-card`、`text-muted-foreground`、`border-input` …），
并且额外生成了 `hover:`/`focus-visible:`/`disabled:`/`dark:` 等前缀版本：

```css
@source inline("{bg,text,border,ring,fill,stroke,divide,outline}-{background,foreground,card,…,chart-5}");
@source inline("{hover,focus-visible,focus,active,disabled,group-hover,aria-expanded,data-[state=open]}:{bg,text,border,ring}-{…}");
@source inline("dark:{bg,text,border,ring,fill,stroke}-{…}");
```

### 后果

```python
ui.button('OK').classes('bg-blue-600')   # ← 不会有任何效果
ui.button('OK').classes('bg-primary')    # ← 可以
```

`bg-blue-600` 属于 Tailwind 的原始调色板，既不在 `@source` 的文件里，也不在 `inline` 子集里，
所以它**根本没有被生成**。这是刻意的：产物大小可控、设计语言统一。
完整的可用类清单看 {doc}`/tutorial/limitations`，或直接搜产物：

```bash
grep -o '\.bg-[a-z-]*' nicegui_shadcn/static/shadcn.css | sort -u
```

:::{note}
一个有趣的例外：`inline-flex` 并不出现在任何 `@source inline(...)` 清单里，
它只是因为字面出现在 `nicegui_shadcn/elements/*.py` 中才被四个 glob 之一扫到。
:::

## 什么时候必须重建 CSS

**只要你动了 `nicegui_shadcn/` 下的任何 `.py` 或 `.vue`，就要重建。**
原因就是上面那条纯函数性质：`classes=` 里新出现的字符串只有被重新扫描之后才会进入产物。

```bash
npm run build          # = build:css + build:vendor，约 250 ms
```

重建之后立刻用审计脚本验收：

```bash
python tests/audit_classes.py
```

它会把「Python / Vue 里引用过、但产物里没有规则」的类全部列出来。详见下节。

## 怎么加一个新 token

1. 在 `frontend/tailwind.css:66-103`（浅色）和 `:106-142`（深色）里各加一条 `--xxx: oklch(...)`。
2. 在 `:144-192` 的 `@theme inline` 里加别名，例如 `--color-xxx: var(--xxx)`。
   别名决定 Tailwind 会生成哪些工具类：`--color-xxx` 生成 `bg-xxx` / `text-xxx` / `border-xxx` / `ring-xxx`。
3. 如果你希望用户也能在运行期用 `classes='bg-xxx'`，把它加进 `:249-251` 的 `inline` 清单
   （`--color-` 后面的名字要出现在 `{…}` 花括号列表里）。
4. `npm run build`，然后 `python tests/audit_classes.py`。

## 怎么把一个新类加进子集

三种办法，按推荐顺序：

1. **让它出现在组件源码里。** 把类写进某个 `default_classes=` 或类表常量，
   四个 glob 会自动扫到它，子集不需要改。这也是组件作者的正常路径。
2. **加进 `@source inline(...)`。** 只有当这个类确实是「用户运行期才写」的通用工具类时才这么做，
   例如 `mt-8`。加之前确认它属于已有的族，不要为了一个特例引入一族。
3. **让用户加自己的 `@source`。** 见下节。

## 用户侧扩展样式表

README 的 *Extending the stylesheet* 一节给了不需要改仓库的做法：

```bash
npm install -D tailwindcss @tailwindcss/cli
printf '@source "../myapp/**/*.py";\n' >> frontend/tailwind.css
npx @tailwindcss/cli -i ./frontend/tailwind.css -o ./static/shadcn.css
```

然后不要注入库自带的那份，而是指向你自己的产物：

```python
from nicegui import ui

ui.add_head_html('<link rel="stylesheet" href="/static/shadcn.css">', shared=True)
```

这样 `classes='bg-blue-600'` 之类你自己的类就有了。注意库的 `theme.setup()` 在导入时也会注入
它自带的 `<link>`，自建产物时要么接受两份样式表（后者层序靠后、能覆盖前者），
要么显式控制导入时机。

## `tests/audit_classes.py` 编码了哪些约定

这个脚本是「Tailwind 会静默丢类」的唯一防线（123 行）。它规定了下面这些约束：

- **常量命名**（`tests/audit_classes.py:31`）：

  ```python
  CLASS_CONSTANT_RE = re.compile(r'^_?[A-Z][A-Z0-9_]*_(BASE|CLASSES|VARIANTS|SIZES)$')
  ```

  只有这种名字的模块级赋值会被当成类表。名字不对 → 不被扫描 → 漏掉的类不会有人替你发现。

- **用 `ast` 而不是正则解析 Python**（`:72-89`）：读的是
  `default_classes=` / `classes=` / `variant_classes=` 三个关键字参数、
  `.classes(...)` 这类方法调用的位置参数，以及上面那个正则命中的赋值语句。
  `_strings()`（`:57-69`）支持字符串、`dict`（取 values）、`tuple`/`list` 形式的类表。

- **`class="…"` 只扫字面量**（`:34`）：

  ```python
  CLASS_ATTR_RE = re.compile(r'(?<![\w:-])class="([^"]*)"')
  ```

  lookbehind 排除了 `:class` 与 `v-bind:class`，因为它们的值是 JavaScript 表达式而不是类列表。
  所以 `.vue` 里由 prop 传入的类（如 `:class="triggerClasses"`）不会被审计——
  它必须已经在 Python 侧被扫到。

- **选择器匹配是精确的**（`:37-54`）：`escape_class()` 复刻 Tailwind 的 CSS 转义，
  `has_selector()` 还要求类名后面不能是标识符字符或另一个转义符的反斜杠，
  否则 `.a` 会错误地匹配 `.animate-pulse`。

- **扫描范围**（`:104-109`）：`nicegui_shadcn/elements/*.py`、`nicegui_shadcn/*.py`、
  `nicegui_shadcn/elements/*.vue`。**注意它不扫 `examples/`**——
  所以 demo 里写了产物中没有的类，审计不会报，只有 `visual_check.mjs` 的计算样式断言才有可能发现。

跑一次的正常输出：

```
checked 223 class tokens

all referenced classes are present in static/shadcn.css
```

## 与 Quasar 混用

- 本库的工具类是 important 的，所以能压过 Quasar 的普通声明；
  但 Quasar 的 `quasar.important.css` 里同样是 important 的声明（如 `.bg-primary`）会被本库压过。
- Quasar 的组件（`q-btn`、`q-input` …）和 shadcn 组件默认不共享调色板：
  前者读 `--q-primary`，后者读 `--primary`。想统一就自己同步这两组变量。
- 页面级背景色请用 `.nicegui-shadcn-surface`（`frontend/tailwind.css:238-241`），
  否则 `<body>` 上仍然是 Quasar 的主题背景。

想建立整体心智模型，接着读 {doc}`/tutorial/how-it-works`；想动手改源码，读 {doc}`component-authoring`。
