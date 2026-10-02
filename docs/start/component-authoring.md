# 组件制作

本页写给要给 `nicegui-shadcn` 增加一个新组件的人。

仓库根目录有一份面向维护者的契约文档 `AGENT.md`，它记录的不是「怎么写」，而是「为什么必须这样写」——
每一条约定背后都对应一个已经付出过代价的坑。本页把其中与「新增组件」有关的部分展开成可执行的步骤。
凡是本页的描述与 `AGENT.md` 冲突的，以本页引用的源码为准（文末列出了核对时发现的出入）。

:::{note}
本页假定你已经能跑通仓库的构建和测试。如果还没有，先读 {doc}`testing`；
想先搞清楚 `classes=` 在用户侧的行为，读 {doc}`/tutorial/usage`。
:::

## 一个组件由什么组成

新增一个组件，通常只碰下面这几个文件：

| 文件 | 是否必须 | 作用 |
| --- | --- | --- |
| `nicegui_shadcn/elements/shadcn_xxx.py` | 必须 | Python 侧的元素类与工厂函数 |
| `nicegui_shadcn/elements/shadcn_xxx.vue` | 可选 | 需要 Vue / reka-ui 行为时才写 |
| `nicegui_shadcn/elements/__init__.py` | 必须 | 三处注册，见「端到端范例」 |
| `frontend/tailwind.css` | 视情况 | 只在你引入了产物里不存在的 class 时才改 |
| `frontend/vendor/reka-entry.js` | 视情况 | 只在你用到了尚未 re-export 的 reka-ui 原语时才改 |
| `pyproject.toml` | 视情况 | 只在你新增了需要进 wheel 的文件时才改 |

没有 `.vue` 的组件，本质上就是给一个原生 HTML 标签加一套类。`nicegui_shadcn/elements/shadcn_button.py:53`
就是这样：

```python
class Button(ShadcnElement, default_classes=_BASE):
```

它没有 `component=`，因此渲染出来的是一个真正的 `<button>`。仓库里很多「结构性」组件都走这条路
（Card、Badge、Label、整个表格家族）。判断标准很简单：**只有需要 JavaScript 行为或可访问性状态机时才写 `.vue`**。

## NiceGUI 3.x 的扩展契约

### `__init_subclass__` 的六个关键字参数

组件是靠类定义处的关键字参数声明自己的资源的，签名在
`C:\Python\Py313\Lib\site-packages\nicegui\element.py:92-131`：

```python
def __init_subclass__(cls, *,
                      component: str | Path | None = None,
                      dependencies: list[str | Path] = [],
                      esm: dict[str, str] | None = None,
                      default_classes: str | None = None,
                      default_style: str | None = None,
                      default_props: str | None = None,
                      ) -> None:
```

本库用到的只有 `component` 和 `default_classes`：

```python
class Select(ShadcnElement, ValueElement, component='shadcn_select.vue'):
```

### `component` / `dependencies` 是「相对定义文件」的 glob

`element.py:101` 先取定义文件所在目录：

```python
base = Path(inspect.getfile(cls)).parent
```

然后 `glob_absolute_paths()`（`element.py:103-107`）对相对路径做 `base / path`，再 `path.parent.glob(path.name)`：

```python
def glob_absolute_paths(file: str | Path) -> list[Path]:
    path = Path(file)
    if not path.is_absolute():
        path = base / path
    return sorted(path.parent.glob(path.name), key=lambda p: p.stem)
```

所以 `component='shadcn_select.vue'` 会被解析成 `nicegui_shadcn/elements/shadcn_select.vue`，
**不用也不能写包路径**。参数是 glob 而不是文件名，因此可以写成 `component='shadcn_tabs*.vue'`
一次注册多个文件（多个匹配结果按 `p.stem` 排序）。

`dependencies=` 走同一套解析，把额外的 `.js` 加进 `exposed_libraries`；`esm=` 会把一个
`{导入名: 相对 js 路径}` 注册成 ESM 模块（`element.py:115-124`）。
**本库两个都没有用**：reka-ui 是通过 `nicegui_shadcn/theme.py:80` 的
`register_importmap_override('reka-ui', REKA_UI_URL)` 重定向到本地 bundle 的
（`theme.py:40` 从 `nicegui.dependencies` 导入它）。

### 组件是怎么注册到前端的

`register_vue_component()`（`nicegui/dependencies.py:102-122`）对每个 `.vue` 立刻调用 `VBuild`
完成「编译」，结果缓存在模块级字典里。之后 `generate_resources()`（`dependencies.py:218-227`）为每个组件生成三行：

```js
import { default as shadcn_select } from "/_nicegui_shadcn/components/shadcn_select.vue";
shadcn_select.template = '#tpl-shadcn_select';
app.component("nicegui-shadcn_select", shadcn_select);
```

由此可以直接读出两条硬约束：**组件名是一个裸 JavaScript 标识符**（不能有连字符、点、斜杠），
**模板 id 必须与 VBuild 生成的那一个逐字符相同**。下一节讲怎么保证这两点。

## 命名规则

### 文件名会成为 JavaScript 标识符

`dependencies.py:110` 取 `name = _get_name(path)`，而 `_get_name()` 的实现是：

```python
def _get_name(path: Path) -> str:
    return path.name.split('.', 1)[0]
```

即「文件名里第一个点之前的部分」，并且**不做任何字符替换**。`Component.__post_init__`
（`dependencies.py:26-30`）会为它建索引，撞名直接断言失败：

```
Duplicate name "shadcn_select" for VueComponent .../shadcn_select.vue
Duplicate key "..." for VueComponent .../shadcn_select.vue
```

结论：

1. **文件名里不能有连字符。** `shadcn-select.vue` 会生成 `import { default as shadcn-select }`，那是减法表达式。
2. **stem 在 `.vue` 与 `.js` 之间必须全局唯一。** `Component._names` 是一个带 `assert` 的共享 `ClassVar`。
3. **所有组件前缀 `shadcn_`。** 前缀是约定，也是防撞名的手段。
4. **不要在文件名里加点。** VBuild 自己算模板 id 用的是 `filepath.stem` 并把点替换成 `-`，
   而注册名用的是第一个点之前的部分。`shadcn.foo.vue` 会让 import 名是 `shadcn`、模板 id 却是
   `tpl-shadcn-foo`，`#tpl-shadcn` 找不到模板，组件静默渲染成空——这是 `AGENT.md` 没有写的一条。

### `data-<name>` 标记

`VBuild` 会在模板正文的第一个标签上插入一个标记属性：

```python
html = re.sub(r'^<([\w-]+)', rf'<\1 data-{name}', parser.html)
```

其中 `name` 是文件名 stem（本库的文件名都是合法标识符，所以就是 stem 本身）。这个属性有两个用途：

- 它是自动化测试定位组件的锚点。`tests/visual_check.mjs:112-124` 有一张 `MOUNTS` 表，
  用 `[data-shadcn_<name>]` 的出现次数断言「每个注册过的 `.vue` 都真的编译并挂载了」，
  而不是静默渲染成空。
- 它同时是 scoped 样式的选择器前缀。

**当根节点是一个「不渲染元素」的 fragment 时，标记会丢。** Vue 的 fallthrough attribute 只会落到
组件根节点渲染出的那个 DOM 元素上；如果模板的第一个标签是 `<SelectRoot>` 这种只提供
provide/inject、自己渲染 `<slot />` 的组件，属性无处可落，挂载断言就会失败。两个修法：

1. 在模板里挑一个有意义的后代元素显式写上标记，同时关掉自动继承：

```vue
<SelectRoot :model-value="modelValue">
  <SelectTrigger v-bind="$attrs" data-shadcn_select>
```

```js
export default {
  inheritAttrs: false,
  // ...
};
```

`nicegui_shadcn/elements/shadcn_select.vue:8-10`（模板）与 `:96`（`inheritAttrs: false`）就是这么做的。
本库显式写过的标记只有四处：`data-shadcn_select`、`data-shadcn_dialog_content`、
`data-shadcn_popover_content`、`data-shadcn_dropdown_menu`。

2. 或者干脆让根节点渲染一个真实元素——本库的 checkbox / switch / slider 都选择把 reka 的
   `*Root` 包在一个 `<span>` 里，这样标记自动落在 `<span>` 上。

:::{warning}
凡是「reka 的 `*Root` 包着原生元素」的组件，`data-<name>` 都是自动生效的，不要手动再写一遍——
手动写会与 `re.sub` 插入的那个重复，得到两个同名属性。
:::

## VBuild 能吃什么，不能吃什么

`VBuild`（`C:\Python\Py313\Lib\site-packages\nicegui\vbuild.py`）**不是 Vue SFC 编译器**，
它只是一个约一百行、基于 `HTMLParser` 的字符串重写器。它的能力边界就是你的模板的能力边界。

### 只能有一个顶层标签

`VueParser.handle_starttag` 在解析完第一个顶层标签、又遇到第二个顶层标签时：

```
ValueError: File has more than one top level tag
```

同样地，出现第二个顶层 `<template>` 会得到 `File contains more than one template`。
所以要么单一根节点，要么用一个包装元素当根。

### void 标签不计数

`VOID_TAGS` 明确列出：

```python
VOID_TAGS = 'area base br col embed hr img input link meta param source track wbr'.split()
```

`handle_starttag` 遇到 void 标签直接 `return`，不增加嵌套层级。因此 **`<input>` 可以当根**——
`nicegui_shadcn/elements/shadcn_input.vue` 就是这么写的。

### 没有 `<script setup>`，只有 Options API

解析器根本不认识 `<script setup>`：`<script>` 的内容会被原样作为 ES module 注入，
而 `app.component(tag, options)` 需要的是**一个带 `default` 导出的选项对象**。所以所有模板都写成：

```js
export default {
  name: 'ShadcnStat',
  inheritAttrs: false,   // 只在需要自己控制 $attrs 落点时才加
  props: { /* 见「Props 与事件」 */ },
  emits: ['update:modelValue'],
};
```

没有 `default export` 的话，`app.component()` 注册进去的就是 `undefined`，页面表现为组件不渲染。

### 嵌套 `<template>` 会截断组件

`handle_endtag` 的实现是这样的（注释是上游原文）：

```python
if tag == 'template' and self._p1:
    # don't watch the level (so it can accept malformed HTML)
    self.html = self.rawdata[self._p1:self._get_offset()].strip()
    self._level -= 1
```

它**不看层级**：遇到的第一个 `</template>` 就是模板的结尾。
如果你在模板内部写了 `<template v-if="...">` 或 `<template #trigger>`，组件会在那里被截断，
后面的内容全部消失，而且**不会有任何报错**。需要条件渲染就把 `v-if` 直接写在真实元素上。

### `<script>` 原样作为 ES module

没有转译、没有类型擦除：`lang="ts"` 会原样送到浏览器并报语法错误。
`<script>` 里可以 `import`——解析器只把它当纯文本，导入由浏览器完成，
但只有 `frontend/vendor/reka-entry.js` re-export 过的名字才能 import 成功（见下文）。

### scoped `<style>` 的选择器会被重写

`<style scoped>` 的内容会被 `add_css_prefix(style, f'*[data-{name}]')` 改写；
不带 `scoped` 的 `<style>` 走 `add_css_prefix(style, '')`，即原样注入。
本库的 `.vue` 里没有 `<style>` 块——所有样式都来自 Tailwind 编译产物，
新增样式请加在 `frontend/tailwind.css`，见 {doc}`styling`。

## Props 与事件

### `element._props` 会变成真正的 Vue props

Python 侧写进 `self._props['placeholder']` 的东西，会作为 prop 传给组件。键名在传输前会被转成 camelCase：

```python
self._props['model-value'] = 'a'    # → Vue 里的 modelValue
```

NiceGUI 还会**无条件注入五个 prop**（`nicegui/static/nicegui.js:236-243`）：

```js
{ id: "c" + id, ref: "r" + id, key: id,
  class: element.class.join(" ") || undefined,
  style: ..., ...element.props }
```

- `class` / `style` 是 fallthrough 属性，单根组件会自动把它合并到自己根元素的 class 列表上——
  这就是 `default_classes=` 生效的原理。
- `id` 必须由组件自己声明，否则会漏到根 DOM 上；`shadcn_input.vue` 声明 `id` 并绑到 `<input :id="id">`。
- `ref` / `key` 是 Vue 保留名，**组件绝对不能声明它们**。

### 每个传入的 prop 都必须声明

没有声明的 prop 不会被丢弃，而是走 `patchAttr` 落到根 DOM 上。
NiceGUI 的 `ValueElement` 会往 `_props` 里塞 `loopback`（见下），
在 `shadcn_select` 上它曾经把 `<button>` 变成 `<button loopback="true">`。
现在 `nicegui_shadcn/elements/shadcn_select.vue:104` 显式声明了它：

```js
loopback: { type: [Boolean, String], default: undefined },
```

:::{warning}
这是本库目前**唯一**声明了 `loopback` 的模板。其余 `ValueElement` 组件的 `loopback` 属性确实会漏到 DOM 上，
详见文末的核对记录——它不影响功能，但说明「声明每一个 prop」这条约定还没有被完全贯彻。
:::

### 事件名：Python 侧带冒号，客户端只大写首字母

Python 里监听：

```python
self.on('update:model-value', self._handle_change, [None])
```

`event_type_to_camel_case`（`nicegui/helpers/strings.py:6`）负责把点分段的每一段转成 camelCase，
得到 `update:modelValue`；客户端再补一个 `on` 前缀并把首字母大写（`nicegui.js:259`）：

```js
let event_name = "on" + event.type[0].toLocaleUpperCase() + event.type.substring(1);
```

所以模板里 `$emit` 时必须写 `update:modelValue`，而 `@update:model-value` 这种 kebab 写法由 Vue 自身负责匹配：

```vue
<TabsRoot :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)">
```

### 单个参数会被解包

事件的 `args` 在服务端会被解包（`nicegui/client.py:347-349`）：

```python
msg['args'] = [None if arg is None else json.loads(arg) for arg in msg.get('args', [])]
if len(msg['args']) == 1:
    msg['args'] = msg['args'][0]
```

所以 `$emit('update:modelValue', value)` 到达 `on_change` 时是值本身，不是 `[value]`。
这也意味着**一个事件不能只带一个数组参数**——它会被当成参数列表展开。

### `ValueElement`：`model-value` 与回写

`nicegui/elements/mixins/value_element.py:12-43` 约定：

```python
VALUE_PROP: str = 'model-value'
LOOPBACK: bool | None = True
```

- `self._props['model-value']` 由 `_value_to_model_value(value)` 计算，
  `self._props['loopback'] = self.LOOPBACK`。
- `LOOPBACK = False` 表示「这个组件的值只在服务端决定，客户端改动不回写」
  （`nicegui.js:275`：`if (element.props["loopback"] === False && event.type == "update:modelValue")`）。
  本库的 `Input`（`shadcn_form.py:80`）与 `Textarea`（`:114`）都设成 `False`，
  因为服务端才是唯一权威的值来源。
- 组件自己回写值时**必须**设 `LOOPBACK = False`，否则客户端与 Python 会来回覆盖。
- 选项类组件（Select / RadioGroup / ToggleGroup）用 `_value_to_model_value` 做类型归一：
  `Select` 返回 `'' if value is None else str(value)`（`shadcn_select.py:50-53`），
  因为 reka 用 `undefined` 表示「未选择」，空串也是安全的未选状态。

## 文本与子元素顺序

`renderRecursively` 会把 `element.text` **unshift 到默认 slot 的子元素之前**（`nicegui.js:318-320`）：

```js
if (name === "default" && element.text !== null) {
  children.unshift(element.text);
}
```

后果是：只要一个元素的 `text` 非空，那段文字永远排在它的所有子元素**前面**。
Button 的 `text` 参数走的就是这条路，所以想在 label 左侧加一个图标，不能靠「先建图标、再 set text」，
而要**把 label 本身建成子元素**，让图标和 label 一起排进 slot。

另一个后果是标签语义。`ui.label` 是 `<div>`，把它塞进 `<button>` 或 `<p>` 是非法 HTML，
浏览器会改写 DOM 结构。所以 `nicegui_shadcn/elements/base.py:126-135` 提供了一个 `Text`：

```python
class Text(TextElement):
    def __init__(self, text: str = '', *, tag: str = 'span') -> None:
        super().__init__(tag=tag, text=text)
```

在 `<button>` 内部一律用它，不要用 `ui.label`。

子元素的创建方式是 `with self:` 上下文（元素会被挂到当前的 slot 上），
`shadcn_display.py:110-119` 的 Avatar fallback 是一个完整例子：

```python
with self:
    self._fallback = ShadcnElement(
        tag='span',
        variant_classes='flex size-full items-center justify-center rounded-full '
                        'bg-muted text-xs font-medium',
    )
    self._fallback._text = fallback
```

:::{danger}
不要试图用 `element.add_slot('default', template)` 往组件里注入标记。
NiceGUI 的 `_collect_slot_dict()` 会排除 default slot，所以这个调用不会产生任何效果——
标记只能靠在 Python 里建真实的子元素。
:::

## 类字符串住在 Python 里

### `ShadcnElement` 与 `cn()` 语义

NiceGUI 的 `.classes()` **只追加、不解析冲突**，`.classes('p-4 p-8')` 会老老实实输出两个类。
本库用 tailwind-merge 的 Python 移植解决了这个问题。所有组件都继承
`nicegui_shadcn/elements/base.py:89` 的 `ShadcnElement`：

```python
class ShadcnElement(Element):
    def __init__(self, *, classes=None, variant_classes=None, **kwargs):
        super().__init__(**kwargs)
        merged = tw_merge(' '.join(self._classes),
                          as_class_string(variant_classes),
                          as_class_string(classes))
        if merged != ' '.join(self._classes):
            self.classes(replace=merged)
```

优先级是 **`classes=` > `variant_classes` > 已有的 `default_classes`**，后者被前者驱逐。
`with_classes()`（`base.py:115-123`）是同一套语义的函数式写法，返回 `self` 以便链式调用。

`variant_classes` 是专门给「组件自己按枚举算出来的类」用的通道。`shadcn_button.py:84-88` 是典型用法：

```python
variant_classes=tw_join('shadcn-button',
                        option('button variant', variant, _VARIANTS),
                        option('button size', size, _SIZES))
```

注意这里用的是 `tw_join`（只拼接）而不是 `tw_merge`（解冲突）：variant 和 size 的类属于不同族，
不该互相驱逐，真正的合并留到 `ShadcnElement.__init__` 一次性做。

### `_tw_merge.py` 里已经踩过的坑

`nicegui_shadcn/_tw_merge.py` 是一个手写的冲突表实现（`_STATIC` / `_PREFIX` / `_GROUP_PATHS`，共 369 行）。
加新族时注意：**一律用 `b[len(prefix):]` 切片，不要手数索引。**
历史上这里用的是 `b[6:]`（`border-`）和 `b[7:]`（`rounded-`），分别错了一个字符，
产生过两个「某些变体偶尔失效」的 bug。另外 `rounded-xl/lg/sm/xs` 必须先按 size 判定，
否则会被读成 side 的 `x`/`l`/`s`/`x`（见该文件 279-285 行的注释）。

枚举参数用 `base.option(kind, value, options)` 校验，非法值会抛出带合法列表的 `ValueError`：

```python
option('button variant', variant, _VARIANTS)
# ValueError: Unknown button variant 'ghostt'. Valid options are: [...]
```

### 常量命名是有语法含义的

`tests/audit_classes.py:31` 只认这一种命名的模块级常量：

```python
CLASS_CONSTANT_RE = re.compile(r'^_?[A-Z][A-Z0-9_]*_(BASE|CLASSES|VARIANTS|SIZES)$')
```

所以类表要叫 `_STAT_BASE`、`_ALERT_VARIANTS`、`_INPUT_CLASSES`、`_AVATAR_SIZES`。
不匹配的名字不会被审计扫描，**写错了不会报错，只会在浏览器里表现为某个类没有样式**。
`default_classes=` / `classes=` / `variant_classes=` 这三个关键字参数的值不受这个正则限制，
无论写成字面量还是常量都会被读到。详见 {doc}`styling`。

### 模板里到底能不能写 `class="…"`

`AGENT.md` 的措辞是「模板里除 `:class` 绑定外不写自己的 `class="…"`」，
但仓库现状并非如此——13 个模板里有 36 处 `class="…"` 字面量（例如 `shadcn_checkbox.vue:6`、
`shadcn_select.vue:10`）。实际执行的约定是：

- **可能被用户的 `classes=` 覆盖或合并的类，必须住在 Python 里**（`default_classes=` 或类表常量），
  否则 `cn()` 根本看不到它们，冲突驱逐会失效。
- 纯结构性的内部装饰（比如 reka 指示器的包装层）可以留在模板里；
  `tests/audit_classes.py:92-94` 会用 `class="…"` 正则把它们也扫一遍，
  所以它们同样必须存在于编译产物中。
- 需要绑定时用 `:class="triggerClasses"` 这类由 Python 传入的 prop，
  这样类字符串仍然只有一个来源——`shadcn_tabs.py:103` 就是这么把 trigger 的类传进模板的。

## 封装 reka-ui 原语

### bundle 与白名单

`frontend/vendor/reka-entry.js`（135 行）只 re-export 本库真正包装过的原语，目的是让 esbuild 能 tree-shake 掉其余部分。
它同时是一份**合法 import 名清单**：`.vue` 里 `import { Foo } from 'reka-ui'` 只能 import 这里出现过的名字。
新增用到的原语时**必须先把它加到 `reka-entry.js`**，再运行 `npm run build:vendor`。

`vue` 在构建时保持 `--external:vue`（`package.json` 的 `build:vendor` 脚本），
因为页面通过 importmap 提供唯一的 Vue 实例；把 Vue 打进 bundle 会导致两份响应式系统。

### 穿不过 NiceGUI slot 的 provide/inject

`TabsList → TabsTrigger` 的 provide/inject **无法跨越 NiceGUI 的 slot 边界**。
reka 的 `TabsTrigger` 会无条件调用 `useRovingFocusItem`，拿不到上下文就抛：

```
Injection `Symbol(RovingFocusGroupContext)` not found.
```

所以标签页被改成了数据驱动：`shadcn_tabs_list.vue` 接收一个 `tabs` 数组，自己 `v-for` 生成 `TabsTrigger`，
而不是让 Python 侧创建 trigger 元素。详见 `nicegui_shadcn/elements/shadcn_tabs.py` 的类文档字符串。

:::{note}
其它原语（dialog、popover、dropdown menu、tooltip、select、accordion）不涉及这条限制，
可以照常把子元素分散在多个 Python 元素里。
:::

### force-mount 的内容不会被自动隐藏

本库让浮层面板在关闭时也留在 DOM 里（force-mount），以保住里面的表单状态。
代价是 reka **只设置 `data-state`，不设置 `hidden`**。所以每个面板都要自己写：

```
data-[state=inactive]:hidden    # tabs 面板
data-[state=closed]:hidden      # accordion 面板
```

`frontend/tailwind.css` 的 `@layer base` 里额外手写了 `[hidden] { display: none !important; }`，
否则面板上的 `display: flex` 会压过浏览器的 UA 规则。
副作用是 accordion 没有关闭动画——元素一直是 `display: none`，没有可动画的中间态。

### 不存在的导出会让构建直接失败

reka-ui 的版本是 `^2.10.5`（`package.json`）。不同小版本之间导出名会变，
例如 `PinInputSeparator` 在当前版本里**不存在**。导入一个不存在的名字时 esbuild 会报：

```
No matching export in "node_modules/reka-ui/dist/index.js" for import "PinInputSeparator"
```

这是好事：本地 `npm run build:vendor` 会立刻失败，而不是运行时静默坏掉。

## 端到端范例：新增一个 `shadcn_stat`

下面是一个完整、可跑的最小新组件：一个 label/value 小方块，无 reka、无事件、无回写。
它覆盖了「有 `.vue` 的组件」的全部必要步骤。

### 第一步：写模板

新建 `nicegui_shadcn/elements/shadcn_stat.vue`：

```vue
<template>
  <div class="flex flex-col gap-1">
    <span class="text-sm text-muted-foreground">{{ label }}</span>
    <span class="text-2xl font-semibold">{{ value }}</span>
    <slot />
  </div>
</template>

<script>
export default {
  name: 'ShadcnStat',
  props: {
    label: { type: String, default: '' },
    value: { type: String, default: '' },
  },
};
</script>
```

要点：单根 `<div>`（所以 `data-shadcn_stat` 自动落在它上面）；Options API；所有传入的 prop 都声明了。
`default_classes=` 里的类由 NiceGUI 作为 `class` prop 送进来，Vue 会自动合并到这个单根上，
因此这里不需要预留 `:class`。

### 第二步：写 Python 封装

新建 `nicegui_shadcn/elements/shadcn_stat.py`：

```python
"""``shadcn.stat`` — a label/value tile."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .base import ShadcnElement

__all__ = ['Stat', 'stat']

_STAT_BASE = (
    'inline-flex flex-col rounded-xl border bg-card px-4 py-3 '
    'text-card-foreground shadow-xs'
)


class Stat(ShadcnElement, component='shadcn_stat.vue', default_classes=_STAT_BASE):
    """A label/value tile.

    :param label: the caption above the value.
    :param value: the value itself.
    """

    def __init__(self,
                 label: str = '',
                 value: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['label'] = label
        self._props['value'] = value


def stat(label: str = '', value: str = '', **kwargs: Any) -> Stat:
    """Create a :class:`Stat`."""
    return Stat(label, value, **kwargs)
```

三处约定都体现在这里：常量名匹配 `CLASS_CONSTANT_RE` 所以会被审计扫到；
`__all__` 让 `from .shadcn_stat import *` 只导出这两个名字；工厂函数用小写同名形式，与仓库其它模块一致。

### 第三步：注册模块

改 `nicegui_shadcn/elements/__init__.py`，**三处都要改**（顺序按字母排）：

```python
from . import (
    base,
    shadcn_accordion,
    shadcn_button,
    shadcn_controls,
    shadcn_display,
    shadcn_form,
    shadcn_layout,
    shadcn_overlay,
    shadcn_select,
    shadcn_stat,              # ← 模块元组里追加（当前在第 12-13 行之间）
    shadcn_tabs,
)
```

```python
__all__ = [
    # ...
    *shadcn_select.__all__,
    *shadcn_stat.__all__,     # ← 汇总 __all__
    *shadcn_tabs.__all__,
]

from .shadcn_select import *  # noqa: E402,F401,F403
from .shadcn_stat import *  # noqa: E402,F401,F403
from .shadcn_tabs import *  # noqa: E402,F401,F403
```

:::{warning}
`__all__` 必须在 star import **之前**拼好。文件里第 17-19 行的注释解释了原因：
`from .icon import *` 会把模块级名字 `icon` 重绑成工厂函数，之后再引用 `icon.__all__` 就晚了。
:::

### 第四步：重建并验证

```bash
npm run build          # Tailwind + esbuild，约 250 ms
python tests/audit_classes.py
```

`npm run build` 之所以要跑，是因为 `_STAT_BASE` 与模板里的类只有在 Tailwind 重新扫描
`nicegui_shadcn/elements/**/*.py` 与 `**/*.vue` 之后才会进入 `static/shadcn.css`。
`audit_classes.py` 是这一步最直接的验收：它打印 `checked N class tokens`，
一旦有类没进产物就列出 `MISSING  <token>  (first seen in shadcn_stat.py)`。

:::{note}
这个范例里的类**恰好都已经被别的组件用过**，所以在旧产物上审计也能通过
（实测：把 `shadcn_stat` 加进一个没有重建过 CSS 的副本，审计只从 223 变成 224 个 token 并全过）。
但你不能指望这一点：换几个新类，跳过重建就会得到 `MISSING`。规则是**改完 `.py`/`.vue` 就重建**，
再让审计告诉你漏没漏。
:::

然后确认组件真的注册进去了：

```bash
python examples/demo.py        # 监听 http://localhost:8080
curl -s http://127.0.0.1:8080/ | grep -o 'tpl-shadcn_stat'
```

模板 id 出现即表示 VBuild 成功解析了 `.vue` 并把它注册成了 `nicegui-shadcn_stat`。

不起服务器也可以直接问 NiceGUI 的注册表：

```bash
python -c "import nicegui_shadcn; from nicegui.dependencies import vue_components; print([c.tag for c in vue_components.values() if c.name == 'shadcn_stat'])"
```

```
['nicegui-shadcn_stat']
```

组件是在**类定义时**就构建好的（`nicegui/dependencies.py:114` 的 `VBuild(path)`），所以这条命令顺便验证了模板能通过 VBuild 的解析。

### 第五步：跑测试

```bash
python tests/test_tw_merge.py
python tests/test_render.py    # 会多出一项 "shadcn_stat registered"
node tests/visual_check.mjs http://127.0.0.1:8080/
```

`tests/test_render.py` 的组件检查是**从磁盘上的 `*.vue` 自动派生**的（`tests/test_render.py:49-52`），
所以新增 `.vue` 之后它会从 30 项变成 31 项，不需要你改测试文件。
想让它顺带断言「真的挂载了」，把 `shadcn_stat` 加进 `tests/visual_check.mjs:112-118` 的 `MOUNTS` 表，
并在 `examples/demo.py` 里用一次。

## 提交前检查清单

- 文件名无连字符、无点，前缀 `shadcn_`，且与已有名字不同。
- 模板只有一个顶层标签，没有嵌套 `<template>`，没有 `<script setup>`，`<script>` 有 `default export`。
- 每个会传进来的 prop 都声明了（别忘了 `loopback`）。
- 会被 `classes=` 覆盖的类住在 Python 里，常量名匹配 `(BASE|CLASSES|VARIANTS|SIZES)`。
- 用到了新的 reka 原语 → 已加进 `frontend/vendor/reka-entry.js`。
- 跑过 `npm run build`，`python tests/audit_classes.py` 通过。
- `git status` 里 `nicegui_shadcn/static/` 是干净的（产物是源码的确定性函数，见 {doc}`testing`）。
- 新增了运行时文件 → 已更新 `pyproject.toml` 的 `include` 列表，见 {doc}`packaging`。

## 常见错误对照表

| 症状 | 原因 | 修法 |
| --- | --- | --- |
| `File has more than one top level tag` | 模板有多个根节点 | 加一个包装根 |
| `File contains more than one template` | 顶层出现了第二个 `<template>` | 合并成一个模板 |
| 组件渲染为空，无报错 | 模板内部有嵌套 `<template>`，被第一个 `</template>` 截断 | 把 `v-if` 写到真实元素上 |
| 组件渲染为空，无报错 | 文件名带点，`#tpl-…` 与注册名不一致 | 去掉文件名里的点 |
| 导入期 `Duplicate name "x"` | stem 与另一个 `.vue` / `.js` 撞名 | 改名（统一加 `shadcn_` 前缀） |
| 导入期语法错误 `default as shadcn-x` | 文件名里有连字符 | 改成下划线 |
| `Injection Symbol(...) not found` | provide/inject 跨了 NiceGUI slot 边界 | 改成数据驱动，像 `shadcn_tabs_list.vue` |
| `No matching export in "node_modules/reka-ui/…"` | 用了 `reka-entry.js` 没 re-export 的名字 | 先加 re-export，再 `npm run build:vendor` |
| 类名在 DOM 上，但没有样式 | 该类没进 `static/shadcn.css` | 重跑 `npm run build`，再跑 `audit_classes.py` |
| `[data-shadcn_x]` 计数为 0 | 根是 fragment，标记丢了 | `inheritAttrs: false` + 在真实元素上显式写标记 |
| `<button loopback="true">` | prop 没声明 | 在 `props` 里声明它 |
| 图标跑到 label 前面 | `element.text` 永远排在子元素之前 | 把 label 建成子元素 |
