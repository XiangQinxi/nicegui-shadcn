# 组件参考

本页给出全部组件的准确清单。所有名字都逐个核对过 `nicegui_shadcn/elements/` 与
`nicegui_shadcn/icons.py` 中的真实导出，而不是照抄 README。

## 数量到底是几个

`nicegui_shadcn.elements.__all__` 一共导出 **265** 个名字，拆开来看：

| 类别 | 数量 | 说明 |
| --- | --- | --- |
| 组件工厂函数 | **130** | 也就是 `shadcn.button(...)` 这种小写函数 |
| 组件类 | 124 | 需要类型标注或 `isinstance` 判断时用 |
| 内部基类 | 2 | `ShadcnElement`、`Text`，不是给用户直接实例化的 |
| 模块与常量 | 6 | `elements` 里转出的 `icons` / `theme` / `theming` 三个模块，以及 `REGEXP_ONLY_*` 三个 OTP 正则 |
| 辅助函数 | 3 | `as_class_string`、`normalize_options`、`option` |

也就是说，**按工厂函数计是 130 个组件**，按组件类计是 124 个。在这 130 个工厂函数里，
`table_container` 与 `icon` 并不是类 —— 前者返回一个普通的 `ShadcnElement` 实例，后者返回
一个原生 `ui.html`。

另外还有两个独立模块：

| 模块 | 内容 |
| --- | --- |
| `nicegui_shadcn.icons` | `ICON_NAMES`（39 个图标名）与 `glyph`、`svg` 两个取值函数，见 {doc}`icons` |
| `nicegui_shadcn.theming` | 10 个导出：`BASE_COLORS`、`COLOR_TOKENS`、`css`、`current`，以及 `use_base_color`、`set_colors`、`set_dark_colors`、`set_radius`、`add_color`、`reset` 六个函数，见 {doc}`theming` |

## 组件表

### 按钮与开关

| 组件名 | 工厂函数 | 关键参数 | 一句话说明 |
| --- | --- | --- | --- |
| Button | `button` | `variant`、`size`、`icon`、`loading` | 带 `variant` / `size` / `icon` / `loading` 的按钮 |
| ButtonGroup | `button_group` | `vertical` | 把若干按钮粘成一个控件 |
| ButtonGroupText | `button_group_text` | `text` | 组内的一段静态文字或图标 |
| ButtonGroupSeparator | `button_group_separator` | `vertical` | 组内按钮之间的细分隔线 |

### 表单

| 组件名 | 工厂函数 | 关键参数 | 一句话说明 |
| --- | --- | --- | --- |
| Input | `input` | `value`、`placeholder`、`type` | 单行文本输入 |
| Textarea | `textarea` | `value`、`rows` | 多行文本输入 |
| Checkbox | `checkbox` | `value` | 布尔复选框；标签用 `label` 配 |
| Switch | `switch` | `value` | 布尔开关；标签用 `label` 配 |
| Label | `label` | `text`、`for_` | 表单标签，`for_` 接元素或 id |
| Select | `select` | `options`、`value` | 下拉选择，选项从 Python 数据传入 |
| NativeSelect | `native_select` | `options`、`value` | 原生 `<select>`，用系统下拉 |
| Combobox | `combobox` | `options`、`value`、`filter` | 可输入搜索的单选下拉 |
| RadioGroup | `radio_group` | `options`、`orientation` | 单选组，选项从 Python 数据传入 |
| Slider | `slider` | `value`、`min`、`max`、`step` | 数值滑块 |
| Toggle | `toggle` | `text`、`value` | 按下去会保持的两态按钮 |
| ToggleGroup | `toggle_group` | `options`、`value`、`multiple` | 分段控件，可单选或多选 |
| InputOTP | `input_otp` | `length`、`groups`、`masked`、`pattern` | 一次性验证码输入格 |
| Calendar | `calendar` | `value`、`min_value`、`locale` | 内联月历 |

`date_picker` 不属于「控件」，它是 `popover` + `calendar` 的组合，列在浮层一节。

### 展示

| 组件名 | 工厂函数 | 关键参数 | 一句话说明 |
| --- | --- | --- | --- |
| Alert | `alert` | `title`、`description`、`variant` | 重要信息提示框 |
| AlertTitle | `alert_title` | `text` | `alert` 的标题行 |
| AlertDescription | `alert_description` | `text` | `alert` 的正文 |
| Avatar | `avatar` | `src`、`fallback`、`size` | 圆形头像，可退回文字 |
| Badge | `badge` | `text`、`variant` | 小状态标签 |
| Progress | `progress` | `value`、`set_value()` | 横向进度条（**没有** `bind_value`） |
| Table | `table` | — | 表格骨架，外层套 `table_container` |
| TableContainer | `table_container` | — | 让宽表格横向滚动 |
| TableHeader | `table_header` | — | `<thead>` |
| TableBody | `table_body` | — | `<tbody>` |
| TableFooter | `table_footer` | — | `<tfoot>` |
| TableRow | `table_row` | — | `<tr>` |
| TableHead | `table_head` | `text` | 表头 `<th>` |
| TableCell | `table_cell` | `text` | 单元格 `<td>` |
| TableCaption | `table_caption` | `text` | 表格题注 |
| Kbd | `kbd` | `text` | 键位提示，如 `kbd('Ctrl')` |
| Marker | `marker` | `text`、`variant`、`icon`、`pulse` | 状态圆点 + 短标签 |
| Spinner | `spinner` | `size`、`label` | 转圈的加载指示器 |
| AspectRatio | `aspect_ratio` | `ratio` | 固定宽高比的容器 |
| Empty | `empty` | — | 空状态容器 |
| EmptyHeader | `empty_header` | — | 空状态居中堆栈 |
| EmptyMedia | `empty_media` | `variant` | 空状态顶部的插图或图标 |
| EmptyTitle | `empty_title` | `text` | 空状态标题 |
| EmptyDescription | `empty_description` | `text` | 空状态说明 |
| EmptyContent | `empty_content` | — | 空状态底部的操作区 |
| Item | `item` | `variant`、`size` | 列表中的一行 |
| ItemGroup | `item_group` | — | 一组 `item`，读起来像一个列表 |
| ItemHeader | `item_header` | — | 行内容之上的通栏 |
| ItemMedia | `item_media` | `variant` | 行首的图标 / 头像 / 图片 |
| ItemTitle | `item_title` | `text` | 行主标题 |
| ItemDescription | `item_description` | `text` | 行次级说明（截断两行） |
| ItemContent | `item_content` | — | 标题与说明所在的可伸缩列 |
| ItemActions | `item_actions` | — | 行尾的按钮或控件 |
| ItemFooter | `item_footer` | — | 行内容之下的通栏 |
| ItemSeparator | `item_separator` | — | 两行之间的细分隔线 |

### 布局

| 组件名 | 工厂函数 | 关键参数 | 一句话说明 |
| --- | --- | --- | --- |
| Card | `card` | — | 卡片容器 |
| CardHeader | `card_header` | — | 卡片头部 |
| CardTitle | `card_title` | `text` | 卡片标题 |
| CardDescription | `card_description` | `text` | 卡片副标题 |
| CardContent | `card_content` | — | 卡片主体 |
| CardFooter | `card_footer` | — | 卡片底部 |
| Separator | `separator` | `orientation`、`decorative` | 水平或垂直分隔线 |
| Skeleton | `skeleton` | `width`、`height` | 加载占位块 |
| Breadcrumb | `breadcrumb` | — | 面包屑的 `<nav>` 外框 |
| BreadcrumbList | `breadcrumb_list` | — | 面包屑的 `<ol>` |
| BreadcrumbItem | `breadcrumb_item` | — | 路径中的一环 |
| BreadcrumbLink | `breadcrumb_link` | `text`、`href` | 可点击的一环 |
| BreadcrumbPage | `breadcrumb_page` | `text` | 当前页（不可点击） |
| BreadcrumbSeparator | `breadcrumb_separator` | `icon` | 环与环之间的分隔符 |
| BreadcrumbEllipsis | `breadcrumb_ellipsis` | — | 被折叠掉的中间环节 |
| Pagination | `pagination` | `page`、`total`、`siblings` | 带上一页/下一页的分页器 |
| ScrollArea | `scroll_area` | `type_`、`scroll_hide_delay` | 自定义滚动条的容器 |
| Direction | `direction` | `direction`、`inline` | 为内部元素设置 `dir` |

### 折叠与分组

| 组件名 | 工厂函数 | 关键参数 | 一句话说明 |
| --- | --- | --- | --- |
| Tabs | `tabs` | `value`、`orientation` | 标签页根元素 |
| TabsList | `tabs_list` | `tabs`、`orientation`、`set_tabs()` | 标签条 |
| TabsContent | `tabs_content` | `value`（必填） | 某个标签对应的面板 |
| Accordion | `accordion` | `value`、`multiple`、`collapsible` | 手风琴根元素 |
| AccordionItem | `accordion_item` | `value`（必填） | 一个可折叠小节 |
| AccordionTrigger | `accordion_trigger` | `text` | 小节的标题按钮 |
| AccordionContent | `accordion_content` | — | 小节的内容区 |
| Collapsible | `collapsible` | `value`、`open()` / `close()` | 单个可折叠区域 |
| CollapsibleTrigger | `collapsible_trigger` | `text`、`as_child` | 折叠区的标题按钮 |
| CollapsibleContent | `collapsible_content` | — | 折叠区的内容 |

### 浮层与反馈

| 组件名 | 工厂函数 | 关键参数 | 一句话说明 |
| --- | --- | --- | --- |
| Dialog | `dialog` | `value`、`on_change` | 模态对话框 |
| DialogTrigger | `dialog_trigger` | `text`、`as_child` | 打开对话框的元素 |
| DialogContent | `dialog_content` | `title`、`side`、`closable` | 对话框面板 |
| DialogFooter | `dialog_footer` | — | 对话框底部按钮行 |
| Sheet | `sheet` | `value` | 从屏幕边缘滑入的面板 |
| SheetTrigger | `sheet_trigger` | `text`、`as_child` | 打开 sheet 的元素 |
| SheetContent | `sheet_content` | `title`、`side`、`closable` | sheet 面板 |
| SheetFooter | `sheet_footer` | — | sheet 底部按钮行 |
| Drawer | `drawer` | `side`、`modal`、`snap_points` | 可拖拽的底部抽屉 |
| DrawerTrigger | `drawer_trigger` | `text`、`as_child` | 打开抽屉的元素 |
| DrawerContent | `drawer_content` | `title`、`side`、`closable` | 抽屉面板 |
| DrawerFooter | `drawer_footer` | — | 抽屉底部按钮行 |
| Popover | `popover` | `value` | 锚定在触发元素上的浮层 |
| PopoverTrigger | `popover_trigger` | `text`、`as_child` | 打开浮层的元素 |
| PopoverContent | `popover_content` | `side`、`align`、`side_offset` | 浮层面板 |
| HoverCard | `hover_card` | `open_delay`、`close_delay` | 悬停预览卡 |
| HoverCardTrigger | `hover_card_trigger` | `as_child`（默认 `True`） | 触发悬停的元素 |
| HoverCardContent | `hover_card_content` | `side`、`align` | 预览卡面板 |
| AlertDialog | `alert_dialog` | `value` | 必须回答的确认框 |
| AlertDialogTrigger | `alert_dialog_trigger` | `text`、`as_child` | 打开确认框的元素 |
| AlertDialogContent | `alert_dialog_content` | `title`、`description` | 确认框面板 |
| AlertDialogAction | `alert_dialog_action` | `text`、`on_click` | 确认按钮，点击即关闭 |
| AlertDialogCancel | `alert_dialog_cancel` | `text`、`on_click` | 取消按钮，点击即关闭 |
| AlertDialogFooter | `alert_dialog_footer` | — | 确认框底部按钮行 |
| Tooltip | `tooltip` | `text`（必填）、`side`、`delay` | 悬停提示 |
| ToastProvider | `toast_provider` | `position`、`duration` | 通知堆叠的容器 |
| Toast | `toast` | `title`、`description`、`variant`、`duration` | 一条通知，用 `.open()` 弹出 |
| DatePicker | `date_picker` | `value`、`min_value`、`placeholder` | 按钮 + 日历面板 |

### 菜单与导航

| 组件名 | 工厂函数 | 关键参数 | 一句话说明 |
| --- | --- | --- | --- |
| DropdownMenu | `dropdown_menu` | `items`、`align`、`on_select` | 下拉菜单，子元素即触发器 |
| ContextMenu | `context_menu` | — | 右键菜单的根元素 |
| ContextMenuTrigger | `context_menu_trigger` | `text`、`as_child` | 划定右键热区 |
| ContextMenuContent | `context_menu_content` | `items`、`on_select` | 右键菜单的条目列表 |
| Menubar | `menubar` | `menus`、`align`、`on_select` | 应用菜单栏 |
| NavigationMenu | `navigation_menu` | `items`、`value`、`on_select` | 悬停展开的站点导航 |
| Command | `command` | `items`、`placeholder`、`on_select`、`on_search` | 可搜索的命令面板 |

### 排版

| 组件名 | 工厂函数 | 关键参数 | 一句话说明 |
| --- | --- | --- | --- |
| Heading | `heading` | `text`、`level` | `<h1>`–`<h4>`，由 `level` 决定 |
| H1 | `h1` | `text` | 等价于 `heading(level=1)` |
| H2 | `h2` | `text` | 等价于 `heading(level=2)` |
| H3 | `h3` | `text` | 等价于 `heading(level=3)` |
| H4 | `h4` | `text` | 等价于 `heading(level=4)` |
| Paragraph | `paragraph` | `text` | 正文段落 |
| Lead | `lead` | `text` | 标题下方那行更大的引言 |
| Large | `large` | `text` | 比标题弱一档的强调文字 |
| Small | `small` | `text` | 小号印刷体（`<small>`） |
| Muted | `muted` | `text` | 次级说明、时间戳 |
| Blockquote | `blockquote` | `text` | 左侧竖线引出的引文 |
| BulletList | `bullet_list` | — | 带项目符号的 `<ul>` |
| InlineCode | `inline_code` | `text` | 句子里的 `<code>` |

### 图标

| 组件名 | 工厂函数 | 关键参数 | 一句话说明 |
| --- | --- | --- | --- |
| Icon | `icon` | `name`、`size`、`classes` | 把内联 SVG 包成元素；返回原生 `ui.html`，共 39 个图标 |

## 常用参数速查

| 组件 | 参数 |
| --- | --- |
| `button` | `variant` ∈ default/destructive/outline/secondary/ghost/link，`size` ∈ default/sm/lg/icon，`icon`，`icon_position`，`loading`，`disabled`，`on_click` |
| `button_group` | `vertical`；子元素用 `button_group_text` / `button_group_separator` 分隔 |
| `input` | `value`，`placeholder`，`type`，`disabled`，`readonly`，`autocomplete`，`on_change` |
| `textarea` | `value`，`placeholder`，`rows`，`disabled`，`readonly`，`on_change` |
| `checkbox`、`switch` | `value: bool`，`disabled`，`on_change` |
| `label` | `text`，`for_` |
| `select`、`combobox` | `options`，`value`，`placeholder`，`disabled`，`on_change`；`combobox` 另有 `filter`、`on_select` |
| `native_select` | `options`，`value: Any`，`disabled`，`on_change` |
| `radio_group` | `options`，`value`，`orientation`，`disabled`，`on_change` |
| `slider` | `value`，`min`，`max`，`step`，`orientation`，`disabled`，`on_change` |
| `toggle` | `text`，`value`，`disabled`，`on_change` |
| `toggle_group` | `options`，`value`，`multiple`，`orientation`，`disabled`，`on_change` |
| `input_otp` | `value`，`length`，`groups`，`pattern`，`masked`，`inputmode`，`on_change` |
| `calendar` | `value`（ISO 字符串或 `date`），`min_value`，`max_value`，`week_starts_on`，`number_of_months`，`fixed_weeks`，`locale`，`on_change` |
| `date_picker` | `value`，`min_value`，`max_value`，`placeholder`，`locale`，`on_date_change` |
| `badge` | `text`，`variant` |
| `avatar` | `src`，`fallback`，`size` |
| `alert` | `title`，`description`，`variant`，`icon` |
| `progress` | `value`（钳制 0–100），`set_value()`；**不是** `ValueElement`，没有 `bind_value` |
| `kbd` | `text` |
| `marker` | `text`，`variant`，`icon`，`pulse` |
| `spinner` | `size`，`label` |
| `aspect_ratio` | `ratio` |
| `empty*` | `empty_media(variant=)`、`empty_title(text)`、`empty_description(text)` |
| `item` | `variant`，`size`；配套 `item_media(variant=)` / `item_title` / `item_description` / `item_actions` |
| `breadcrumb_link` | `text`，`href`；`breadcrumb_separator(icon=)` |
| `pagination` | `page`（从 1 开始），`total`，`siblings`，`on_change`（读 `e.value`） |
| `scroll_area` | `type_` ∈ hover/scroll/auto/always，`scroll_hide_delay` |
| `direction` | `direction` ∈ ltr/rtl，`inline` |
| `separator` | `orientation`，`decorative` |
| `skeleton` | `width`，`height` |
| `tabs` | `value`，`orientation`，`on_change` |
| `tabs_list` | `tabs`，`orientation`，`set_tabs()` |
| `tabs_content` | `value`（必填） |
| `accordion` | `value`，`multiple`，`collapsible`，`orientation`，`on_change` |
| `accordion_item` | `value`（必填），`disabled` |
| `collapsible` | `value`，`disabled`，`on_change`，`open()` / `close()` / `toggle()` |
| `dialog`、`sheet`、`drawer`、`alert_dialog` | `value`，`on_change`，`open()` / `close()` / `toggle()` |
| `dialog_content` | `title`，`description`，`side`，`closable`，`aria_label` |
| `sheet_content` | 同上，`side` 默认 `'right'` |
| `drawer_content` | `title`，`description`，`side`，`closable`；root 另有 `modal`、`snap_points` |
| `popover_content` | `side`，`align`，`side_offset` |
| `hover_card` | `value`，`open_delay`，`close_delay` |
| `dropdown_menu` | `items`，`align`，`side_offset`，`on_select`，`set_items()` |
| `menubar` | `menus`，`align`，`side_offset`，`on_select` |
| `navigation_menu` | `items`，`value`，`on_select` |
| `command` | `items`，`value`，`placeholder`，`empty_text`，`filter`，`autofocus`，`on_select`，`on_search` |
| `context_menu_content` | `items`，`on_select` |
| `toast` | `title`，`value`，`description`，`variant`，`duration`，`closable`，`open()` |
| `toast_provider` | `position`，`duration`，`swipe_direction` |
| `tooltip` | `text`，`side`，`delay` |
| `heading` / `h1`–`h4` | `text`，`level`（仅 `heading`） |
| `paragraph`、`lead`、`large`、`small`、`muted`、`blockquote`、`inline_code` | `text` |
| `bullet_list` | 无参数，往里放元素即可 |

## options / tabs / items 的四种写法

```python
shadcn.select(['system', 'light', 'dark'])                     # value == label
shadcn.select({'system': 'System', 'light': 'Light'})          # value -> label
shadcn.select([('system', 'System'), ('light', 'Light')])      # (value, label) 对
shadcn.select([{'value': 'system', 'label': 'System', 'disabled': False}])
```

菜单类组件（`select`、`combobox`、`dropdown_menu`、`context_menu_content`、`command`、
`menubar`、`toggle_group`、`radio_group`）的选项还会额外认识 `kind='label'` /
`kind='separator'` 与 `variant='destructive'`，细节见 {doc}`menus`。

## 相关页面

- {doc}`layout`、{doc}`typography`、{doc}`forms`、{doc}`display`、{doc}`disclosure`、
  {doc}`overlays`、{doc}`menus` —— 按类型展开的用法与示例。
- {doc}`icons` —— 39 个图标常量与 `icons.icon(...)` 的用法。
- {doc}`theming` —— `theming` 模块注册颜色、调圆角、切换深浅色的完整 API。
- {doc}`usage` —— 所有组件共有的 `classes=` / `variant=` / `size=` 语义。
