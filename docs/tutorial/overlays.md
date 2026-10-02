# 浮层

浮层这一组覆盖了所有「按需出现的东西」：`dialog`（对话框）、`sheet`（侧边面板）、`drawer`
（底部抽屉）、`popover`（气泡面板）、`dropdown_menu`（下拉菜单）、`hover_card`（悬停卡片）、
`alert_dialog`（确认对话框）、`tooltip`（提示气泡），以及不依附于触发器的 `toast`（通知）。
菜单类浮层（`menubar`、`navigation_menu`、`command`）以及同样按数据驱动渲染的
`context_menu` 在 {doc}`menus` 里单独展开。

它们的共同结构是：一个**常驻的 root** 保存打开状态，一个可选的 **trigger** 负责切换，以及
一份被 `Teleport` 挂到 `<body>` 的 **content**。

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

## sheet 与 drawer

`sheet` 与 `drawer` 都是「从屏幕边缘滑出的 dialog」，共用 `_Openable` 的
`open()` / `close()` / `toggle()`，区别只在默认滑入的边和面板的形态：

```python
with shadcn.sheet() as sheet:
    shadcn.sheet_trigger('打开设置')
    with shadcn.sheet_content(title='编辑设置',
                              description='改动立即生效。',
                              side='right'):
        shadcn.input(placeholder='工作区名称').classes('w-full')
        with shadcn.sheet_footer():
            shadcn.button('保存', icon='check', on_click=sheet.close)
```

| 工厂函数 | 位置参数 | 关键字参数 |
| --- | --- | --- |
| `shadcn.sheet` | — | `value`、`on_change` |
| `shadcn.sheet_trigger` | `text` | `as_child`、`on_click` |
| `shadcn.sheet_content` | `title` | `description`、`side`、`closable`、`aria_label` |
| `shadcn.sheet_footer` | — | — |

```python
with shadcn.drawer() as drawer:
    shadcn.drawer_trigger('快速操作')
    with shadcn.drawer_content(title='快速操作', side='bottom'):
        shadcn.muted('向下滑动即可关闭。')
        with shadcn.drawer_footer():
            shadcn.button('完成', variant='outline', on_click=drawer.close)
```

| 参数 | 适用 | 说明 |
| --- | --- | --- |
| `side` | `sheet` 为 `'right'`；`drawer` 为 `'bottom'` | 从哪条边滑入 |
| `modal` | `drawer` | 默认 `True`，置 `False` 时打开期间仍可操作背景 |
| `snap_points` / `snap_point` | `drawer` | 抽屉可以停留的高度（如 `[0.25, 0.6]`）与初始停留点 |

`sheet_content(side=…)` 与 `drawer_content(side=…)` 的取值要和外层 root 的默认边保持一致，
否则面板的圆角与滑动方向会对不上。

:::{warning}
`sheet_trigger` / `drawer_trigger` 和 `dialog_trigger` 一样，**没有** `variant` / `size`
参数 —— 它们本身就渲染成 outline 按钮。
:::

## hover_card

`hover_card` 在鼠标悬停（或键盘聚焦）时弹出一张卡片，适合做用户资料卡、术语解释：

```python
with shadcn.hover_card():
    with shadcn.hover_card_trigger():
        shadcn.button('@nicegui', variant='link')
    with shadcn.hover_card_content():
        with ui.column().classes('gap-1'):
            shadcn.large('NiceGUI')
            shadcn.muted('用 Python 构建 Web 界面。')
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `value` | `None` | `None` 表示完全交给悬停；`True` / `False` 可强制卡片常开或常关 |
| `open_delay` | `200` | 悬停多少毫秒后打开 |
| `close_delay` | `150` | 指针离开后多少毫秒关闭 |
| `side` / `align` | `'bottom'` / `'center'` | `hover_card_content` 的弹出方位 |

`hover_card_trigger(as_child=True)` 是**默认值**（和别的触发器相反），所以里面直接放一个
元素即可，不必传 `as_child`。

## alert_dialog

`alert_dialog` 是「必须回答才能继续」的确认框：它锁住背景、没有右上角关闭按钮、也不会被
遮罩点击关掉，只能通过 action 或 cancel 结束：

```python
with shadcn.alert_dialog() as confirm:
    shadcn.alert_dialog_trigger('删除项目')
    with shadcn.alert_dialog_content(title='确定要删除项目吗？',
                                     description='此操作不可撤销。'):
        with shadcn.alert_dialog_footer():
            shadcn.alert_dialog_cancel('取消')
            shadcn.alert_dialog_action('删除', on_click=confirm.close)
```

| 工厂函数 | 位置参数 | 关键字参数 |
| --- | --- | --- |
| `shadcn.alert_dialog` | — | `value`、`on_change` |
| `shadcn.alert_dialog_trigger` | `text` | `as_child`、`on_click` |
| `shadcn.alert_dialog_content` | `title` | `description`、`aria_label` |
| `shadcn.alert_dialog_action` | `text` | `on_click` |
| `shadcn.alert_dialog_cancel` | `text` | `on_click` |
| `shadcn.alert_dialog_footer` | — | — |

`alert_dialog_content` **没有** `side` / `closable` —— 它是不可轻率关闭的，也不做 sheet
形态。`action` 与 `cancel` 渲染成两个扁平按钮，各自只额外接受 `on_click`，其中 `action` 的
回调会在关闭动画之前执行：想「先弹确认再执行」时，把业务逻辑写在 `on_click` 里即可。

## toast

`toast` 不依附于触发器，它挂在一个 **provider** 上，由服务端随时 `open()`：

```python
from nicegui import ui
from nicegui_shadcn import shadcn

with shadcn.toast_provider(position='bottom-right', duration=5000):
    saved = shadcn.toast('部署已排队',
                         description='上线后我们会邮件通知你。',
                         duration=60000)
    shadcn.button('显示通知', variant='outline', on_click=saved.open)
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `title` | `''` | 位置参数，粗体第一行 |
| `value` | `False` | 是否一开始就可见 |
| `description` | `''` | 标题下方的次级说明 |
| `variant` | `'default'` | `default` / `destructive` / `success` |
| `duration` | `None` | 多少毫秒后自动关闭；`0` 表示不自动关闭 |
| `closable` | `True` | 是否显示关闭按钮 |

`toast_provider` 决定这一组通知的位置与默认时长：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `position` | `'bottom-right'` | 通知堆叠的角落 |
| `duration` | `5000` | 默认停留毫秒数，`0` 表示常驻 |
| `swipe_direction` | `'right'` | 可以朝哪个方向把通知划走 |

`toast` 同样是 `_Openable`，`open()` / `close()` / `toggle()` 与 `value` 都可以用，所以也能
写成 `shadcn.toast('已保存', value=True)` 直接在页面加载时弹出。

:::{tip}
一个页面可以放多个 `toast_provider`，例如左下角放提示、右上角放错误。同一个 provider 里的
通知会按打开顺序堆叠。
:::

## 下一步

- {doc}`menus` —— menubar、navigation_menu、command 与 context_menu。
- {doc}`disclosure` —— tabs 与 accordion，另一种**非** portal 的“按需显示”。
- {doc}`limitations` —— 已挂载内容与 `hidden` 属性的取舍。
