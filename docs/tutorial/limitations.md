# 设计说明与限制

这一页收集的是**使用者**会真正碰到的边界：哪些看起来应该能用的写法不会生效、哪些行为是
刻意为之的取舍。想了解这些取舍在仓库内部是怎么实现的，请读 {doc}`how-it-works` 和
{doc}`/start/component-authoring`。

## `.classes()` 是追加，`.with_classes()` 才是合并

最容易踩的一条。NiceGUI 的 `.classes(...)` 只做追加，不做冲突解决；当追加的 class 与组件
已有的 class 属于同一个冲突组时，两条规则都在，由样式表里的顺序裁决 —— 而这未必是你想要
的那一条：

```python
shadcn.card().classes('p-0')            # 无声失败：py-6 仍然生效
shadcn.card().with_classes('p-0')       # 正确：py-6 被逐出
```

`.p-0` 在编译产物里排在 `.py-6` **之前**，所以后者赢。详细说明与规则见 {doc}`usage`。

## `classes=` 只能使用编译产物里已有的 class

样式表是**预编译**的，运行期不会生成任何新规则。可以放心依赖的是：

- 组件自身用到的每一个 class；
- shadcn 的语义化颜色及其常见变体（`bg-primary`、`text-muted-foreground`、
  `dark:border-input`、`hover:bg-accent`、`data-[state=open]:bg-accent` …）；
- 一组刻意精选的布局 / 间距 / 排版词汇（`w-full`、`mt-4`、`px-8`、`gap-3`、`text-center`、
  `rounded-full`、`shadow-lg`、`grid-cols-3` …）。

在此之外的任何东西都不会生效，最典型的是原始调色板颜色：

```python
shadcn.button('Save', classes='bg-blue-600')   # 完全没有效果
```

原因不是 bug 而是范围控制：`frontend/tailwind.css` 用 `source(none)` 关掉了自动内容探测，
只扫描显式的 `@source` glob，运行期字符串由一组 `@source inline(...)` 块兜底 —— 那是一个
**刻意的子集**。要走出这个子集就得重新构建样式表，见 {doc}`/start/styling`。

:::{note}
替代方案都被权衡过并否决了：生成**完整的** Tailwind 会让下载体积成倍增长；发布一个运行期
JIT 编译器则会重新引入一套与 Quasar 打架的 reset。当前方案是两者之间最便宜的妥协。
:::

## 与 Quasar 共用一套页面：两个调色板

shadcn 使用自己的 CSS 变量，而不是 Quasar 的 —— 两者都定义了 `--primary`。shadcn 的工具类
之所以能胜出，是因为它们被输出到 `layer(utilities) important`，压过了
`quasar_importants`；**Quasar 自己的组件则保留 Quasar 的配色**。

实际后果：

- `ui.notify`、`ui.dialog`、`ui.menu`、`ui.tabs` 这些原生组件的颜色与 shadcn 组件不同；
- 深色模式下两套变量各自切换，可能出现“两种深色”；
- 用 `classes=` 想给 Quasar 组件套 shadcn 配色时，会碰到 Quasar 的 `!important` 规则
  （shadcn 侧之所以能赢，靠的正是同样的 important 标志）。

这不是可以“修好”的东西，而是有意让两边各自保持一致的配色。

## 没有 Tailwind preflight

Quasar 已经做了全局规范化，再加一份 Tailwind 的 preflight 只会相互打架。所以只有**一条**
preflight 规则被手工补上：

```css
@layer base {
  [hidden] { display: none !important; }
}
```

它是必需的，因为 reka-ui 的强制挂载内容靠 `hidden` 属性隐藏，而 `display: flex` 之类的工具
类会压过浏览器默认的 `[hidden]` 规则。如果你从别处搬来依赖 preflight 的示例代码（例如假定
`h1`–`h6` 的 margin 已被清零），行为可能与预期不同。

## 已挂载但关闭的面板

`TabsContent` 与 `AccordionContent` 的内容**一直留在 DOM 里**，只靠
`data-[state=inactive]:hidden` 与 `data-[state=closed]:hidden` 隐藏。这样服务端更新总能找
到对应的元素，切换标签也不会丢掉表单状态。

代价有两个：

1. **accordion 没有关闭动画** —— 打开时有 `animate-accordion-down`，关闭时是立即消失。
2. 页面上的 DOM 比你看到的更多 —— 对绝大多数量级的界面无所谓，但在一个标签页里塞几百个
   元素时要注意它们始终存在。

## 标签页是数据驱动的

reka-ui 的 `TabsList` 会 `provide` 一个 roving-focus context，供 `TabsTrigger` `inject`；
这种注入无法穿过 NiceGUI 的 slot 传递。因此 trigger 是在 list 组件内部生成的。

代价是：**一个标签不能包含任意 NiceGUI 子元素，它只接受一个 label 字符串。**

```python
shadcn.tabs_list([('account', 'Account')])   # 只能这样给标签
```

如果你想在标签里放图标、徽章或任意组件，当前是不支持的。`accordion_trigger` 没有这个限制，
它接受任意子元素 —— 只有 tabs 因为 roving-focus 的注入边界必须走数据路径。

:::{note}
这不是唯一的实现路线，但另一条路要么放弃方向键与焦点管理，要么自己重写 roving-focus。
对标签栏这种小控件来说，换掉无障碍行为的代价更高。
:::

## `add_slot()` 对 shadcn 组件不起作用

NiceGUI 的 `_collect_slot_dict()` 会排除 default slot，因此 default slot 的模板永远不会被
发往客户端。加上 `.vue` 模板不是 Vue SFC，不可能注入自定义模板。需要自定义结构时，请用
组合的方式：把 shadcn 组件当作积木，而不是继承或改写它们。

## `.vue` 模板用 Options API，而且受解析器限制

NiceGUI 的 `VBuild` 是一个约 100 行的 HTML 解析器，**不是** Vue SFC 编译器。它带来几条硬性
约束（加组件时才会直接碰到，但解释了为什么不能给现有组件传自定义模板）：

- `<script setup>` 不会被编译，只支持 `export default { … }` 的 Options API；
- 嵌套的 `<template>` 会**截断**组件（解析器在第一个 `</template>` 处关闭且不检查嵌套
  层级），所以模板里必须用真实元素上的 `v-for` 或 `<component :is>`；
- 每个模板文件只能有一个顶层标签；
- 文件名（stem）会被当作 JS 标识符，因此不能含连字符，且必须全局唯一。

## 图标只有 39 个

图标是**内联**在 `nicegui_shadcn/icons.py` 里的，不是从 `lucide-vue-next` 打包来的。
`package.json` 里虽然列了这个包，但它并不参与运行期资源 —— 39 个图标的路径数据是写进
Python 的。

因此 `shadcn.button(icon='trash-2')` 只能使用 {doc}`icons` 里列出的那些名字；传别的会抛
`KeyError`。想加一个图标，要向 `_ICONS` 里加一项并重新构建 —— 没有“随便写个 Lucide 名字
就行”的通道。

## 触发器没有 `variant` / `size`

`dialog_trigger` 与 `popover_trigger` 都固定渲染成 outline 按钮，它们的构造函数里**没有**
`variant` 与 `size` 参数。写成：

```python
shadcn.popover_trigger('Open popover', variant='outline')   # TypeError
```

会抛 `TypeError: Element.__init__() got an unexpected keyword argument 'variant'` —— 因为未声明
的关键字参数会一路透传到 NiceGUI 的 `Element.__init__`，而它不接受额外参数。要改外观，用
`classes=` 或 `with_classes()`。

## 表格单元格默认不换行

`table_head` 与 `table_cell` 都自带 `whitespace-nowrap`。长文本要么自己截断，要么用
`.with_classes('whitespace-normal')`（**不是** `.classes(...)`）显式打开换行。

## 抽屉里还有未包装的原语

`reka-ui` bundle 里 re-export 的原语比本库当前包装的更多。以下原语已经在
`nicegui_shadcn/static/vendor/reka-ui.js` 里，但**还没有对应的 Python 组件**：

| 原语 | 对应的 shadcn 组件 |
| --- | --- |
| `AlertDialog*`、`DialogClose` | Alert Dialog |
| `HoverCard*` | Hover Card |
| `ScrollArea*` | Scroll Area |
| `PinInput*` | Input OTP（注意：`PinInputSeparator` 在 reka-ui 2.10.5 里并不存在） |
| `Toast*`、`ToastProvider` | Sonner / Toast |
| `Collapsible*` | Collapsible |
| `AspectRatio` | Aspect Ratio |
| `DropdownMenuSub*`、`DropdownMenuCheckboxItem`、`DropdownMenuRadioItem` | 带子菜单与复选项的下拉菜单 |

它们是可以被封装的目标，只是目前没有 Python 侧的门面。封装一个的流程见
{doc}`/start/component-authoring`。

## 运行时字符串 class 需要显式声明

如果某个 class 只在运行期以字符串形式出现（例如根据数据决定 `bg-blue-600` 还是
`bg-red-600`），Tailwind 扫描源码时根本看不到它。这时必须用
`@source inline("…")` 明确告诉构建器，否则依旧不会生成规则。

## README 里的截图使用相对路径

纯文档问题，但值得记一笔：`README.md` / `README_zh.md` 中的截图用相对路径引用
`docs/demo-light.png`，这在代码托管网站上可用，但在 PyPI 上不行。等项目有了自己的主页，
它们应该被换成绝对 raw URL。

## 相关页面

- {doc}`usage` —— `classes=` 的正确用法与边界。
- {doc}`how-it-works` —— 层叠层级、import map、`<link>` 与 FOUC 的成因。
- {doc}`/start/styling` —— 扩展样式表以突破预编译词汇表。
