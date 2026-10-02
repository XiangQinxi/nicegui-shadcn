# 工作原理

这个库是 NiceGUI 官方文档中
[“Using other Vue UI frameworks”](https://nicegui.io/documentation/section_styling_appearance#using_other_vue_ui_frameworks)
扩展机制的一个实例：用 shadcn/ui 的设计语言包装 reka-ui 的原语，并把它们做成普通的
NiceGUI 元素。*使用*它不需要任何构建步骤 —— 一切都在发布前编译好了。

## 组成部分

| 组成部分 | 作用 |
| --- | --- |
| `nicegui_shadcn/theme.py` | 提供 `static/` 并注入 `<link>`。导入时即运行。 |
| `frontend/tailwind.css` | Tailwind v4 源码：shadcn 设计 token、`@theme inline` 暴露、绑定到 `body.body--dark` 的 `dark` 变体。属于构建输入，不随 wheel 发布。 |
| `nicegui_shadcn/static/shadcn.css` | 编译后的样式表（约 191 kB）。 |
| `nicegui_shadcn/static/vendor/reka-ui.js` | 本库所封装的那些 `reka-ui` 原语，经过 tree-shaking 后约 283 kB。 |
| `frontend/vendor/reka-entry.js` | 生成上面这个 bundle 的 esbuild 入口。属于构建输入。 |
| `nicegui_shadcn/_tw_merge.py` | `tailwind-merge` 的一个零依赖移植版，也就是 `cn()` 辅助函数。 |
| `nicegui_shadcn/elements/*.py` | 每个组件一个类：`ShadcnElement` 加上 NiceGUI 的 `ValueElement`/`TextElement` mixin。 |
| `nicegui_shadcn/elements/*.vue` | 需要真实交互行为的组件所用的模板。由 NiceGUI 自带的 `VBuild` 解析，以 ES module 方式执行。 |

Python 类决定用哪些 class，`.vue` 文件决定结构。所有 class 字符串都写在 Python 里，这样
`classes=` 才能被正确合并，`tests/audit_classes.py` 也能校验每一个 class 确实存在于编译后
的 CSS 中。

## 导入时会发生的三件事

导入 `nicegui_shadcn` 会把所有必须在**首个组件渲染之前**就位的东西注册好。
`nicegui_shadcn/theme.py` 在模块末尾直接调用 `setup()`，而 `nicegui_shadcn/__init__.py`
会导入它，所以 `from nicegui_shadcn import shadcn` 这一行就够了：

1. **提供静态文件。** `app.add_static_files('/_nicegui_shadcn', …)` 把包内的 `static/`
   挂到 `/_nicegui_shadcn` 前缀下。
2. **注册 import map。** `register_importmap_override('reka-ui', …)` 让 `.vue` 脚本可以写
   可读的裸模块名：

   ```js
   import { DialogRoot } from 'reka-ui';
   ```

   而不是一串带内容哈希的 URL。
3. **注入样式表。** `ui.add_head_html('<link rel="stylesheet" href="/_nicegui_shadcn/shadcn.css">', shared=True)`
   把样式表放进文档 head。

`setup()` 是幂等的（内部有个 `_installed` 布尔量），重复调用是廉价的空操作；需要显式激活
一个被延迟导入的包时也可以手动调用：

```python
from nicegui_shadcn import setup
setup()
```

除此之外没有任何全局注册 —— 没有 Tailwind 运行时，也没有 CDN 导入。

:::{note}
`shared=True` 是必需的，不是可选的。上面这些调用发生在 `ui.context` 之外（导入期），只有
`shared=True` 才让 head HTML 成为页面级的、对每个客户端都生效的声明。
:::

## 为什么用 `<link>` 而不是 `ui.add_css`

`ui.add_css` 会把整张样式表**内联**进一次 `addStyle(...)` 的 JavaScript 调用，于是浏览器
要等到 socket 握手完成、JavaScript 执行之后才看到任何规则。shadcn 的外观完全由 class
驱动，结果是每次刷新都会看到一次明显闪烁的无样式内容（FOUC）。

文档 head 里的 `<link>` 则随第一帧一起绘制。这是这个库唯一一处刻意绕开 NiceGUI 惯用写法
的地方。

## 为什么 `reka-ui` 必须把 `vue` 保持为 external

NiceGUI 自带了 Vue 3.5.x，并且 import map 里已经把裸模块名 `vue` 映射到它。本库的
`reka-ui` bundle 是用下面这条命令构建的：

```bash
npx esbuild frontend/vendor/reka-entry.js --bundle --format=esm --target=es2020 \
    --external:vue --minify --legal-comments=none --outfile=nicegui_shadcn/static/vendor/reka-ui.js
```

`--external:vue` 是整条命令里最关键的一个参数。如果省略它，bundle 会**再打包一份自己的
Vue**，页面上就有两个 Vue 实例，而 Vue 的 `provide`/`inject` 与 `Teleport` 都是实例级的：

- 组件从 `reka-ui` 侧 `provide` 的 context，另一侧的组件永远 `inject` 不到；
- `Teleport` 的目标容器属于另一个实例，浮层会挂到错误的地方或干脆不挂载。

保持 `vue` external，bundle 和所有 `.vue` 组件就共用同一个 Vue 实例，`provide`/`inject`
与 `Teleport` 才能跨组件工作。

:::{tip}
`frontend/vendor/reka-entry.js` 只 re-export 本库真正封装的那些原语 —— 这是 esbuild 能够
tree-shake 掉其余部分、把 bundle 控制在约 283 kB 的原因。加新组件时要从这里增补 export。
:::

## 为什么不需要 Tailwind preflight

Tailwind 的 preflight 是一份全局 reset。NiceGUI 已经加载了 Quasar 自己的规范化样式
（`quasar.unimportant.css`），再来一份 reset 只会和它相互打架。所以
`frontend/tailwind.css` 只导入 `theme` 与 `utilities` 两部分：

```css
@import "tailwindcss/theme.css" layer(theme);
@import "tailwindcss/utilities.css" layer(utilities) source(none) important;
@import "tw-animate-css";
```

只有一条 preflight 规则是真正必需的，它是手工补上的：

```css
@layer base {
  [hidden] { display: none !important; }
}
```

原因见 {doc}`limitations`：`TabsContent` 和 `AccordionContent` 会一直留在 DOM 里，靠
`hidden` 属性来隐藏。没有这条规则，`display: flex` 之类的工具类会压过浏览器默认的
`[hidden]` 规则，关闭的面板就会露出来。

## 样式是怎么压过 Quasar 的

NiceGUI 在 `templates/index.html` 里一次性声明了层叠层级顺序：

```css
@layer theme, base, quasar, nicegui, components, utilities, overrides, quasar_importants;
```

Quasar 的颜色辅助类是这么被导入的：

```css
@import url("quasar.important.css") layer(quasar_importants);
```

而那个文件里有 `.bg-primary { background: var(--q-primary) !important; }` 这样的规则。
`!important` 压过任何普通声明，无论它属于哪个 layer —— 所以 utilities 的导入带了
`important` 标志。important 声明的 layer 优先级是**反的**，因此 `utilities` 一旦也
important，就赢过排在它后面的 `quasar_importants`。

没有这个标志，`shadcn.button()` 会是 Quasar 的蓝色，而不是 shadcn 的近黑 `--primary`。
同时，Quasar 自己的组件保留它们的配色；本库只在 shadcn 组件上使用 shadcn 的 token。

## 编译产物是确定性的

utilities 的导入带了 `source(none)`，这关掉了 Tailwind 的自动内容探测（否则它会扫描整个
checkout，让编译产物取决于构建时的工作目录）。样式表因此只是显式 `@source` glob 的纯函数：

```css
@source "../nicegui_shadcn/elements/**/*.vue";
@source "../nicegui_shadcn/elements/**/*.py";
@source "../nicegui_shadcn/*.py";
@source "../examples/**/*.py";
```

这套 glob 只覆盖本库自己的源码和示例。运行期通过 `classes=` 传进来的字符串由一组
`@source inline(...)` 块兜底，详见 {doc}`usage`。

## 下一站

- {doc}`usage` —— `classes=`、`variant=`、`size=` 的完整语义。
- {doc}`limitations` —— 这套设计带来的、用户会碰到的边界。
- {doc}`/start/component-authoring` —— 如果你要自己加一个组件。
