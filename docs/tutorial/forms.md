# 表单

每一个表单控件都是 NiceGUI 的 `ValueElement`，所以 `bind_value`、`on_value_change`、`ui.bind`
以及 `.value` 属性全部照常工作。这意味着一半的控件可以直接替换掉原生 `ui.*` 而不用改动
任何数据流代码。

## 控件一览

| 工厂函数 | 值类型 | 位置参数 | 关键字参数 |
| --- | --- | --- | --- |
| `shadcn.input` | `str` | `value` | `placeholder`、`type`、`disabled`、`readonly`、`autocomplete`、`on_change` |
| `shadcn.textarea` | `str` | `value` | `placeholder`、`rows`、`disabled`、`readonly`、`on_change` |
| `shadcn.checkbox` | `bool` | `value` | `disabled`、`on_change` |
| `shadcn.switch` | `bool` | `value` | `disabled`、`on_change` |
| `shadcn.select` | `str` | `options` | `value`、`placeholder`、`disabled`、`on_change` |
| `shadcn.radio_group` | `str` | `options` | `value`、`orientation`、`disabled`、`on_change` |
| `shadcn.slider` | `float` | `value` | `min`、`max`、`step`、`orientation`、`disabled`、`on_change` |
| `shadcn.toggle` | `bool` | `text` | `value`、`disabled`、`on_change` |
| `shadcn.toggle_group` | `str` 或 `list[str]` | `options` | `value`、`multiple`、`orientation`、`disabled`、`on_change` |
| `shadcn.label` | — | `text` | `for_` |

:::{warning}
`checkbox` 与 `switch` 的第一个位置参数是 **`value`**，不是标签文本，它们**没有** `label`
参数。下面这种写法会抛 `TypeError: checkbox() got multiple values for argument 'value'`：

```python
shadcn.checkbox('Accept terms', value=True)   # 错误
```

正确写法是把标签拆成一个独立的 `label` 元素：

```python
terms = shadcn.checkbox(value=True)
shadcn.label('Accept terms', for_=terms)
```

只有 `toggle` 是个例外 —— 它的第一个位置参数确实是显示文本。
:::

## 标签与 `for_`

`shadcn.label(text, for_=…)` 的 `for_` 既可以接一个元素，也可以接一个 id 字符串：

```python
name = shadcn.input(placeholder='Project name')
shadcn.label('Project name', for_=name)
```

:::{tip}
尽量传**元素本身**而不是 `element.html_id`。NiceGUI 的 id 是懒分配的，在元素还没被渲染时
取 `html_id` 可能拿到一个稍后才成立的字符串；传元素则由 `label` 自己去找，永远可靠。
:::

## 一个完整的表单

```python
from dataclasses import dataclass
from nicegui import ui
from nicegui_shadcn import shadcn

@dataclass
class Form:
    name: str = ''
    description: str = ''
    terms: bool = False
    notifications: bool = False
    environment: str = 'system'
    plan: str = 'card'
    replicas: float = 40
    bold: bool = False
    align: str = 'center'

form = Form()

with shadcn.card():
    with shadcn.card_header():
        shadcn.card_title('Deploy')
        shadcn.card_description('所有字段都双向绑定到同一个 dataclass。')
    with shadcn.card_content().classes('grid gap-4'):
        name = shadcn.input(placeholder='Project name').bind_value(form, 'name')
        shadcn.label('Project name', for_=name)

        shadcn.textarea(placeholder='Description', rows=4).bind_value(form, 'description')

        terms = shadcn.checkbox(value=True).bind_value(form, 'terms')
        shadcn.label('Accept terms', for_=terms)

        notify = shadcn.switch().bind_value(form, 'notifications')
        shadcn.label('Notifications', for_=notify)

        shadcn.select({'system': 'System', 'light': 'Light', 'dark': 'Dark'},
                      value='system').bind_value(form, 'environment')
        shadcn.radio_group([('card', 'Card'), ('paypal', 'PayPal')],
                           value='card').bind_value(form, 'plan')
        shadcn.slider(40, min=0, max=100, step=5).bind_value(form, 'replicas')
        shadcn.toggle('Bold', value=True).bind_value(form, 'bold')
        shadcn.toggle_group(['left', 'center', 'right'],
                            value='center', multiple=False).bind_value(form, 'align')

    with shadcn.card_footer():
        shadcn.button('Reset', variant='outline', on_click=lambda: _reset(form))
        shadcn.button('Save', on_click=lambda: ui.notify(f'{form.name!r} saved'))
```

在 shadcn 控件与普通 NiceGUI 元素之间共享同一个对象，正是整件事的意义所在：

```python
ui.label().bind_text_from(form, 'name')      # 跟着输入框实时更新
shadcn.input().bind_value(form, 'name')      # 反过来也成立
```

## 用 `on_change` 而不是 `on_value_change`

每个控件都接受一个 `on_change` 关键字参数，它就是 `on_value_change` 的快捷写法，事件对象
的 `.value` 是转换过的值：

```python
shadcn.slider(40, on_change=lambda e: ui.notify(f'{e.value:.0f}%'))
shadcn.select(['a', 'b'], on_change=lambda e: ui.notify(e.value))
```

两种写法等价，想要链条式或条件式绑定用 `.on_value_change(...)` 更顺手：

```python
slider = shadcn.slider(40)
slider.on_value_change(lambda e: ui.notify(f'{e.value:.0f}%'))
```

## 值的类型与转换

- `checkbox` / `switch` / `toggle`：`value` 经 `bool()` 强制，回传的也是 `bool`。
- `slider`：`value` / `min` / `max` / `step` 都转成 `float`。
- `select` / `radio_group`：选项值统一转成 `str`；`value=None` 表示“未选中”，此时只显示
  `placeholder`（`select` 的默认值是 `'Select an option'`）。
- `toggle_group`：`multiple=False` 时值是单个 `str`，`multiple=True` 时是 `list[str]`，与
  `value` 参数的接受形式一致 —— 单选可以传字符串，多选可以传列表。
- `radio_group` 的 `orientation` 默认是 `'vertical'`，`toggle_group` 与 `slider` 默认是
  `'horizontal'`。

## 选项的写法

`select`、`radio_group`、`toggle_group` 的 `options` 接受四种形式（完整说明见
{doc}`usage`）：

```python
shadcn.radio_group(['card', 'paypal'])                              # value == label
shadcn.radio_group({'card': 'Card', 'paypal': 'PayPal'})            # value -> label
shadcn.radio_group([('card', 'Card'), ('paypal', 'PayPal')])        # (value, label) 对
shadcn.radio_group([{'value': 'card', 'label': 'Card', 'disabled': False}])
```

## 为什么选项必须从 Python 数据传入

`select`、`radio_group`、`toggle_group` 的弹出层与指示器都渲染在 DOM 的
[portal](https://vuejs.org/guide/built-ins/teleport.html) 里，NiceGUI 的子元素放不进去。
所以它们的选项是通过 `options` 参数从 Python 侧以数据形式传入的，而不是用 `with` 块组合
出来的。要动态换选项，用 `set_options(...)`：

```python
select = shadcn.select(['a', 'b'])
select.set_options({'x': 'X', 'y': 'Y'})
```

## 下一步

- {doc}`display` —— 把表单放进卡片之外的展示组件里。
- {doc}`usage` —— `classes=`、`with_classes()`、`bind_value` 之外的 NiceGUI 工具箱。
