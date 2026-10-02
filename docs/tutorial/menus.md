# 菜单与命令面板

这一页讲的是**数据驱动**的菜单：`dropdown_menu`、`context_menu`、`menubar`、
`navigation_menu` 与 `command`。它们的共同点是「条目在 Python 里给出，DOM 在浏览器里生成」
—— 因为弹出的面板会被 `Teleport` 到 `<body>`，NiceGUI 无法在它里面插入子元素。

```{note}
菜单类的条目都走同一个规范化函数 `normalize_options`，所以**选项的四种写法**到处通用。
详见 {doc}`forms` 的「选项的写法」一节。
```

## 选项的四种写法

```python
# 1. 字符串列表：value 与 label 都是它本身
ops = ['copy', 'cut', 'paste']

# 2. {value: label} 映射
ops = {'copy': '复制', 'cut': '剪切'}

# 3. (value, label) 元组列表
ops = [('copy', '复制'), ('cut', '剪切')]

# 4. 完整字典：可disabled、可插入分隔符与分组标题
ops = [
    {'value': 'copy', 'label': '复制', 'shortcut': '⌘C'},
    {'kind': 'separator'},
    {'kind': 'label', 'label': '危险操作'},
    {'value': 'delete', 'label': '删除', 'variant': 'destructive'},
    {'value': 'archive', 'label': '归档', 'disabled': True},
]
```

| 键 | 说明 |
| --- | --- |
| `value` / `label` | 选中后回调拿到的值与显示文案 |
| `kind` | `'item'`（默认）、`'label'`（不可选的小标题）、`'separator'`（分隔线） |
| `variant` | `'default'` 或 `'destructive'`（把条目染成红色） |
| `disabled` | 置灰且不可选 |
| `shortcut` | 右侧的快捷键提示（只有 `command` 会渲染） |
| `group` | 分组名（只有 `command` 用它，同一组会自动加标题） |
| `keywords` | 额外的搜索关键字（只有 `command` 用它） |
| `href` | 链接目标（只有 `navigation_menu` 用它） |

`kind='label'` 等于以前那种「灰色说明文字」，`kind='separator'` 是一条 `<hr>`，两者都**不会**
触发 `on_select`。

## dropdown_menu

`dropdown_menu` 的条目是数据，而**触发按钮**是嵌在它里面的子元素 —— 点击任意子元素都会打开
菜单：

```python
from nicegui import ui
from nicegui_shadcn import shadcn

with shadcn.dropdown_menu([{'value': 'edit', 'label': '编辑'},
                           {'value': 'duplicate', 'label': '创建副本'},
                           {'kind': 'separator'},
                           {'value': 'delete', 'label': '删除', 'variant': 'destructive'}],
                          on_select=lambda e: ui.notify(f'选择：{e.args}')) as menu:
    shadcn.button('更多操作', variant='outline', icon='more_horiz')
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `items` | `None` | 位置参数，条目（见上文四种写法） |
| `align` | `'start'` | 面板相对触发器的水平对齐：`'start'` / `'center'` / `'end'` |
| `side_offset` | `4` | 面板与触发器之间的像素间距 |
| `on_select` | `None` | 选中时调用，选中值在 `e.args` 里 |

## context_menu

`context_menu` 是右键菜单，结构上分三层：root 保存状态，`context_menu_trigger` 划定“右键
区域”，`context_menu_content` 才是那份数据列表：

```python
with shadcn.context_menu() as ctx:
    with shadcn.context_menu_trigger(as_child=True):
        with ui.card().classes('w-64'):
            shadcn.muted('在这里点右键')
            shadcn.paragraph('整块卡片都是右键热区。')
    shadcn.context_menu_content(
        [{'value': 'copy', 'label': '复制'},
         {'value': 'cut', 'label': '剪切'},
         {'kind': 'separator'},
         {'value': 'delete', 'label': '删除', 'variant': 'destructive'}],
        on_select=lambda e: ui.notify(f'上下文菜单：{e.args}'),
    )
```

| 工厂函数 | 位置参数 | 关键字参数 |
| --- | --- | --- |
| `shadcn.context_menu` | — | — |
| `shadcn.context_menu_trigger` | `text` | `as_child` |
| `shadcn.context_menu_content` | `items` | `on_select` |

`context_menu_trigger` 默认 `as_child=False` —— 它会渲染成一个带虚线的占位区域。要让**已有的
元素**成为右键热区，就设 `as_child=True` 并把元素嵌进去。

## menubar

`menubar` 是桌面应用那种水平的菜单栏：一次传入所有下拉菜单，键是触发器文案，值是条目列表。

```python
shadcn.menubar(
    {'文件': [{'value': 'new', 'label': '新建'},
              {'value': 'open', 'label': '打开…'},
              {'kind': 'separator'},
              {'value': 'quit', 'label': '退出'}],
     '编辑': [{'value': 'undo', 'label': '撤销'},
              {'value': 'redo', 'label': '重做', 'disabled': True}]},
    on_select=lambda e: ui.notify(f'菜单：{e.args}'),
)
```

也可以写成 `[{'label': '文件', 'items': [...]}, ...]` 这种列表形式，顺序更有保证。

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `menus` | `None` | 位置参数，`{label: items}` 映射或 `{'label', 'items'}` 列表 |
| `align` | `'start'` | 下拉面板的水平对齐 |
| `side_offset` | `8` | 面板与菜单栏之间的像素间距 |
| `on_select` | `None` | 选中时调用，选中值在 `e.args` 里 |

## navigation_menu

`navigation_menu` 是悬停展开的站点导航条。它的条目比其它菜单多一层结构：一个条目要么是
**叶子链接**（有 `href`），要么是**面板**（有 `items`，面板里的子项还可以带 `description`）。

```python
shadcn.navigation_menu(
    [{'label': '快速开始',
      'items': [{'label': '简介', 'href': '/docs', 'description': '了解整体结构。'},
                {'label': '安装', 'href': '/docs/install', 'description': '把包装进项目。'}]},
     {'label': '组件', 'href': '/components'}],
    on_select=lambda e: ui.notify(f'跳转：{e.args}'),
)
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `items` | `None` | 位置参数，条目列表 |
| `value` | `None` | 首屏就展开的那个面板对应的条目标签 |
| `on_select` | `None` | 链接被激活时调用，参数是条目的 value |

:::{tip}
`href` 可以是站内路径，也可以是完整 URL。如果只想处理点击而不真的跳转，把 `href` 留空并在
`on_select` 里自己导航即可。
:::

## command

`command` 是一整块命令面板：顶部一个搜索框，下面按 `group` 分组的可执行条目，支持键盘上下键
与 `Enter` 选中。

```python
shadcn.command(
    [{'value': 'calendar', 'label': '打开日历', 'group': '建议', 'shortcut': '⌘K'},
     {'value': 'search', 'label': '搜索文件', 'group': '建议', 'keywords': 'find grep'},
     {'kind': 'separator'},
     {'value': 'profile', 'label': '个人资料', 'group': '设置'},
     {'value': 'billing', 'label': '账单', 'group': '设置', 'disabled': True}],
    placeholder='输入命令或搜索…',
    on_select=lambda e: ui.notify(f'执行：{e.args}'),
)
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `items` | `None` | 位置参数，条目（额外支持 `group` / `keywords` / `shortcut`） |
| `value` | `None` | 初始高亮的条目 |
| `placeholder` | `'Type a command or search...'` | 搜索框占位文案 |
| `empty_text` | `'No results found.'` | 搜不到时的提示 |
| `filter` | `True` | 在浏览器里即时过滤；置 `False` 改由服务端过滤 |
| `autofocus` | `False` | 创建后立刻聚焦搜索框 |
| `on_change` | `None` | 高亮项变化时调用 |
| `on_select` | `None` | 命令被选中时调用 |
| `on_search` | `None` | 输入过程中调用，参数是当前查询词 |

`filter=False` 配合 `on_search` 就是**服务端搜索**：用户每敲一个字，`on_search` 就会收到当前
查询词，你可以据此重建 `items`。

:::{warning}
`menubar`、`navigation_menu`、`command`、`context_menu`、`dropdown_menu` 都是**单个自闭合
元素**，没有配套的 `_trigger` / `_content` / `_item` 子工厂 —— 不要照搬 shadcn 官方的
`<Menubar><MenubarMenu>…` 写法。需要自定义内容时，用条目的数据字典表达。
:::

## 下一步

- {doc}`overlays` —— `dropdown_menu` 的邻居们：dialog、sheet、drawer、toast。
- {doc}`forms` —— 普通表单控件的选项写法与此完全一致。
- {doc}`components` —— 全部组件的速查索引。
