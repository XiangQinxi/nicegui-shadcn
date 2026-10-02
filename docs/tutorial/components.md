# 组件参考

本页给出全部组件的准确清单。所有名字都逐个核对过 `nicegui_shadcn/elements/` 与
`nicegui_shadcn/icons.py` 中的真实导出，而不是照抄 README。

## 数量到底是几个

`nicegui_shadcn.elements.__all__` 一共导出 **105** 个名字，拆开来看：

| 类别 | 数量 | 说明 |
| --- | --- | --- |
| 组件工厂函数 | **51** | 也就是 `shadcn.button(...)` 这种小写函数 |
| 组件类 | 49 | 需要类型标注或 `isinstance` 判断时用 |
| 内部基类 | 2 | `ShadcnElement`、`Text`，不是给用户直接实例化的 |
| 辅助函数 | 3 | `as_class_string`、`normalize_options`、`option` |

所以“51 components”这个说法按**工厂函数**计是准确的，但按**组件类**计只有 **49** 个
（51 个类减去两个基类）。而在这 51 个工厂函数里，`table_container` 与 `icon` 都不是类 ——
前者返回一个普通的 `ShadcnElement` 实例，后者返回一个原生 `ui.html`。

## 组件表

### 按钮（1）

| 组件名 | 工厂函数 | 一句话说明 |
| --- | --- | --- |
| Button | `button` | 带 `variant` / `size` / `icon` / `loading` 的按钮 |

### 表单（10）

| 组件名 | 工厂函数 | 一句话说明 |
| --- | --- | --- |
| Input | `input` | 单行文本输入 |
| Textarea | `textarea` | 多行文本输入（`rows=`） |
| Checkbox | `checkbox` | 布尔复选框；首参是 `value`，标签用 `label` 配 |
| Switch | `switch` | 布尔开关；首参是 `value`，标签用 `label` 配 |
| Label | `label` | 表单标签，`for_=` 接元素或 id |
| Select | `select` | 下拉选择，选项从 Python 数据传入 |
| RadioGroup | `radio_group` | 单选组，选项从 Python 数据传入 |
| Slider | `slider` | 数值滑块，`min` / `max` / `step` |
| Toggle | `toggle` | 按钮式开关；首参是文本，不是 `value` |
| ToggleGroup | `toggle_group` | 按钮组，`multiple=True` 时值是列表 |

### 展示（15）

| 组件名 | 工厂函数 | 一句话说明 |
| --- | --- | --- |
| Badge | `badge` | 状态徽章，`variant` ∈ default/secondary/destructive/outline |
| Alert | `alert` | 提示框，可组合或直接用 `title`/`description` |
| AlertTitle | `alert_title` | `alert` 内的粗体标题行 |
| AlertDescription | `alert_description` | `alert` 内的次级说明 |
| Avatar | `avatar` | 头像，`src` / `fallback` / `size` |
| Progress | `progress` | 进度条，值钳制在 0–100 |
| TableContainer | `table_container` | 表格外层的横向滚动容器（**不是类**） |
| Table | `table` | `<table>` |
| TableHeader | `table_header` | `<thead>` |
| TableBody | `table_body` | `<tbody>` |
| TableFooter | `table_footer` | `<tfoot>` |
| TableRow | `table_row` | `<tr>` |
| TableHead | `table_head` | `<th>`，接受位置文本 |
| TableCell | `table_cell` | `<td>`，接受位置文本 |
| TableCaption | `table_caption` | `<caption>`，接受位置文本 |

### 布局（8）

| 组件名 | 工厂函数 | 一句话说明 |
| --- | --- | --- |
| Card | `card` | 卡片容器 |
| CardHeader | `card_header` | 卡片头部（grid 容器） |
| CardTitle | `card_title` | 卡片标题 |
| CardDescription | `card_description` | 卡片副标题 |
| CardContent | `card_content` | 卡片内容区 |
| CardFooter | `card_footer` | 卡片页脚（横向 flex） |
| Separator | `separator` | 分隔线，`orientation` / `decorative` |
| Skeleton | `skeleton` | 加载占位块，`width` / `height` |

### 折叠（7）

| 组件名 | 工厂函数 | 一句话说明 |
| --- | --- | --- |
| Tabs | `tabs` | 标签页容器，持有选中的 `value` |
| TabsList | `tabs_list` | 标签栏，标签以数据传入 |
| TabsContent | `tabs_content` | 标签面板，`value` 必填、常驻 DOM |
| Accordion | `accordion` | 手风琴容器，`multiple` / `collapsible` |
| AccordionItem | `accordion_item` | 折叠项，`value` 必填 |
| AccordionTrigger | `accordion_trigger` | 折叠项标题按钮 |
| AccordionContent | `accordion_content` | 折叠项内容，常驻 DOM |

### 浮层（9）

| 组件名 | 工厂函数 | 一句话说明 |
| --- | --- | --- |
| Dialog | `dialog` | 对话框 / sheet 的根，`open()` / `close()` / `toggle()` |
| DialogTrigger | `dialog_trigger` | 对话框触发器；**没有** `variant` / `size` |
| DialogContent | `dialog_content` | 对话框面板，`side` 支持 sheet，`closable` |
| DialogFooter | `dialog_footer` | 对话框底部按钮行 |
| Popover | `popover` | 气泡面板的根 |
| PopoverTrigger | `popover_trigger` | 气泡触发器；**没有** `variant` / `size` |
| PopoverContent | `popover_content` | 气泡面板，`side` / `align` / `side_offset` |
| DropdownMenu | `dropdown_menu` | 下拉菜单，`items` + `on_select`；子元素即触发器 |
| Tooltip | `tooltip` | 悬停提示，`text` 是必填位置参数 |

### 图标（1）

| 组件名 | 工厂函数 | 一句话说明 |
| --- | --- | --- |
| — | `icon` | 把内联 SVG 包成元素；返回原生 `ui.html`，共 39 个图标 |

## 常用参数速查

| 组件 | 参数 |
| --- | --- |
| `button` | `variant` ∈ default/destructive/outline/secondary/ghost/link，`size` ∈ default/sm/lg/icon，`icon`，`icon_position`，`loading`，`disabled`，`on_click` |
| `input` | `value`，`placeholder`，`type`，`disabled`，`readonly`，`autocomplete`，`on_change` |
| `textarea` | `value`，`placeholder`，`rows`，`disabled`，`readonly`，`on_change` |
| `checkbox`、`switch` | `value: bool`，`disabled`，`on_change` |
| `label` | `text`，`for_` |
| `select` | `options`，`value`，`placeholder`，`disabled`，`on_change` |
| `radio_group` | `options`，`value`，`orientation`，`disabled`，`on_change` |
| `slider` | `value`，`min`，`max`，`step`，`orientation`，`disabled`，`on_change` |
| `toggle` | `text`，`value`，`disabled`，`on_change` |
| `toggle_group` | `options`，`value`，`multiple`，`orientation`，`disabled`，`on_change` |
| `badge` | `text`，`variant` |
| `avatar` | `src`，`fallback`，`size` |
| `alert` | `title`，`description`，`variant`，`icon` |
| `progress` | `value`（钳制 0–100），`set_value()` |
| `separator` | `orientation`，`decorative` |
| `skeleton` | `width`，`height` |
| `tabs` | `value`，`orientation`，`on_change` |
| `tabs_list` | `tabs`，`orientation`，`set_tabs()` |
| `tabs_content` | `value`（必填） |
| `accordion` | `value`，`multiple`，`collapsible`，`orientation`，`on_change` |
| `accordion_item` | `value`（必填），`disabled` |
| `dialog` | `value`，`on_change`，`open()` / `close()` / `toggle()` |
| `dialog_content` | `title`，`description`，`side`，`closable`，`aria_label` |
| `popover_content` | `side`，`align`，`side_offset` |
| `dropdown_menu` | `items`，`align`，`side_offset`，`on_select`，`set_items()` |
| `tooltip` | `text`，`side`，`delay` |

## options / tabs / items 的四种写法

```python
shadcn.select(['system', 'light', 'dark'])                     # value == label
shadcn.select({'system': 'System', 'light': 'Light'})          # value -> label
shadcn.select([('system', 'System'), ('light', 'Light')])      # (value, label) 对
shadcn.select([{'value': 'system', 'label': 'System', 'disabled': False}])
```

## 相关页面

- {doc}`layout`、{doc}`forms`、{doc}`display`、{doc}`disclosure`、{doc}`overlays`、{doc}`icons`
  —— 按类型展开的用法与示例。
- {doc}`usage` —— 所有组件共有的 `classes=` / `variant=` / `size=` 语义。
