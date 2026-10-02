# 浮层

浮层这一组有四个成员：`dialog`（对话框 / sheet 面板）、`popover`（气泡面板）、`dropdown_menu`
（下拉菜单）与 `tooltip`（提示气泡）。它们共享同一套结构：一个**常驻的 root** 保存打开状态，
一个可选的 **trigger** 负责切换，以及一份被 `Teleport` 挂到 `<body>` 的 **content**。

## 触发器的配对规则

所有浮层都是「root 包住 trigger 和 content」的形态：

```python
with shadcn.dialog() as dialog:      # root：保存打开状态，可持有句柄
    shadcn.dialog_trigger('Edit profile')      # 可选：点击切换打开状态
    with shadcn.dialog_content(title='Edit profile'):   # 内容，被挂到 <body>
        ...
```

三条规则：

1. **trigger 与 content 必须写在 root 的 `with` 块里**（直接子元素）。root 不渲染任何可见
   标记，它就是用来承载状态的。
2. **content 声明的位置不影响它显示的位置** —— 它会被 teleport 到 `<body>`，因此不会被
   父级的 `overflow: hidden` 裁剪，也不会被 z-index 层级困住。
3. **trigger 是可选的** —— 你可以完全不给 trigger，只靠 `dialog.open()` 之类的调用从服务端
   打开它。

:::{note}
调用方的 `classes=` 在浮层上会经 `$attrs` 转到**面板**元素上，而不是 root 上。所以
`shadcn.dialog_content(title='…', classes='w-96')` 是有效的，并且作用在真正可见的那一层。
:::

## dialog

```python
from nicegui_shadcn import shadcn

with shadcn.dialog() as dialog:
    shadcn.dialog_trigger('Edit profile')          # 渲染成一个 outline 按钮
    with shadcn.dialog_content(title='Edit profile',
                               description='Changes are saved locally.'):
        shadcn.input(value='Ada Lovelace')
        with shadcn.dialog_footer():
            shadcn.button('Cancel', variant='outline', on_click=dialog.close)
            shadcn.button('Save', on_click=lambda: (ui.notify('Saved'), dialog.close()))

dialog.open()      # 也有 close() 与 toggle()
```

| 工厂函数 | 位置参数 | 关键字参数 |
| --- | --- | --- |
| `shadcn.dialog` | — | `value`、`on_change` |
| `shadcn.dialog_trigger` | `text` | `as_child` |
| `shadcn.dialog_content` | `title` | `description`、`side`、`closable`、`aria_label` |
| `shadcn.dialog_footer` | — | — |

`dialog` 的 `value` 是布尔值（`False` 表示关闭），`open()` / `close()` / `toggle()` 就是
`set_value(True)` / `set_value(False)` / `set_value(not value)` 的语法糖。因此也能直接绑定：

```python
dialog = shadcn.dialog().bind_value(state, 'show_profile')
```

### sheet 风格面板

`dialog_content(side=…)` 接受 `'center'`（默认，居中对话框）与 `'top'`、`'right'`、`'bottom'`、
`'left'`（贴边滑出的 sheet 面板）：

```python
with shadcn.dialog_content(title='Filters', side='right'):
    ...
```

### 可关闭性

`closable=True` 是默认值，此时右上角会出现一个关闭按钮，点击遮罩与按 `Esc` 也会关闭。
`closable=False` 会移除关闭按钮；遮罩点击与 `Esc` 由 reka-ui 的原语控制，因此仍然可用。

`title` 省略时对话框在视觉上没有标题，但仍会对屏幕阅读器使用 `aria_label`（默认
`'Dialog'`）保持可访问。要自定义，传 `aria_label='…'`。

:::{warning}
`dialog_trigger` **没有** `variant` / `size` 参数 —— 它本来就渲染成 outline 按钮。写成
`shadcn.dialog_trigger('Edit profile', variant='outline')` 会抛
`TypeError: Element.__init__() got an unexpected keyword argument 'variant'`，因为 `variant`
会一路透传到 NiceGUI 的 `Element.__init__`，而它不接受这个参数。
:::

## popover

```python
with shadcn.popover() as popover:
    shadcn.popover_trigger('Open popover')     # 同样是 outline 按钮
    with shadcn.popover_content():
        ui.label('Anything NiceGUI can render.')
```

| 工厂函数 | 位置参数 | 关键字参数 |
| --- | --- | --- |
| `shadcn.popover` | — | `value`、`on_change` |
| `shadcn.popover_trigger` | `text` | `as_child` |
| `shadcn.popover_content` | — | `side`、`align`、`side_offset` |

- `side`：`'bottom'`（默认）、`'top'`、`'right'`、`'left'`。
- `align`：`'center'`（默认）、`'start'`、`'end'`。
- `side_offset`：面板与触发器的像素间距，默认 `4`。

与 dialog 一样，`popover` 也提供 `open()` / `close()` / `toggle()`，并且 `value` 可以绑定。
区别在于 popover 不锁滚动、不设遮罩，点击外部即关闭 —— 适合放筛选器、小表单、颜色选择
这类轻量面板。

:::{warning}
`popover_trigger` 与 `dialog_trigger` 相同，**没有** `variant` / `size` 参数。README 里
`shadcn.popover_trigger('Open popover', variant='outline')` 是一个错误示例。
:::

## dropdown_menu

下拉菜单没有专门的 trigger 组件：**你放进 root 的第一个子元素就是触发器**。

```python
with shadcn.dropdown_menu([
        {'kind': 'label', 'label': 'My account'},
        {'value': 'profile', 'label': 'Profile'},
        {'value': 'settings', 'label': 'Settings'},
        {'kind': 'separator'},
        {'value': 'logout', 'label': 'Log out', 'variant': 'destructive'},
    ], on_select=lambda e: ui.notify(f'Menu: {e.args}')):
    shadcn.button('Open menu', variant='outline', icon='ellipsis')
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `items` | `None` | 菜单项列表 |
| `align` | `'start'` | 相对触发器的对齐方式：`start` / `center` / `end` |
| `side_offset` | `4` | 与触发器的像素间距 |
| `on_select` | `None` | 选中回调，事件对象的 `.args` 是被选中项的值 |

### 菜单项的种类

每一项都是一个字典，`kind` 决定它的类型：

| `kind` | 需要的字段 | 说明 |
| --- | --- | --- |
| `'item'`（默认） | `value`、`label`，可选 `disabled`、`variant` | 可点击的菜单项 |
| `'label'` | `label` | 分组标题，不可点击 |
| `'separator'` | — | 一条分隔线 |

`variant='destructive'` 让菜单项变成危险色 —— 登出、删除这类操作的标准写法。

`on_select` 的事件对象把值放在 `.args` 里。用四元组或字符串简写时同样适用：

```python
shadcn.dropdown_menu(['profile', 'settings'], on_select=lambda e: ui.notify(e.args))
```

运行时整体换掉菜单项，用 `set_items(items)`：

```python
menu = shadcn.dropdown_menu([{'value': 'a', 'label': 'A'}])
menu.set_items([{'value': 'b', 'label': 'B'}])
```

## tooltip

`tooltip` 是唯一一个把内容写成**位置参数**的浮层 —— 它就是提示文本本身，被包住的子元素
就是触发器：

```python
with shadcn.tooltip('Add to library', side='top'):
    shadcn.button('Hover me', variant='outline')
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `text` | — | 提示文本，**必填位置参数** |
| `side` | `'top'` | `top` / `right` / `bottom` / `left` |
| `delay` | `200` | 悬停多少毫秒后出现 |

:::{tip}
tooltip 只响应悬停与键盘焦点，不响应点击。用它来解释图标按钮的含义是最常见的场景 ——
配合 `shadcn.button('Delete', icon='trash-2', size='icon')` 这种只有图标的按钮尤其必要。
:::

## 下一步

- {doc}`disclosure` —— tabs 与 accordion，另一种**非** portal 的“按需显示”。
- {doc}`limitations` —— 已挂载内容与 `hidden` 属性的取舍。
