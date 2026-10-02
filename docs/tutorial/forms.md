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
| `shadcn.native_select` | `str` | `options` | `value`、`disabled`、`on_change` |
| `shadcn.combobox` | `str` | `options` | `value`、`placeholder`、`search_placeholder`、`empty_text`、`filter`、`on_change`、`on_select` |
| `shadcn.input_otp` | `str` | `value` | `length`、`groups`、`pattern`、`masked`、`disabled`、`inputmode`、`on_change` |
| `shadcn.calendar` | `date` / `str` | `value` | `min_value`、`max_value`、`week_starts_on`、`number_of_months`、`fixed_weeks`、`disabled`、`readonly`、`locale`、`on_change` |
| `shadcn.date_picker` | `date` / `str` | `value` | `min_value`、`max_value`、`placeholder`、`week_starts_on`、`locale`、`disabled`、`format_date`、`on_date_change` |
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
- `calendar` / `date_picker`：`value` 接受 `datetime.date`、`datetime.datetime` 或 ISO 的
  `'YYYY-MM-DD'` 字符串，回传的值同样是 ISO 字符串。`min_value` / `max_value` 接受同一组
  形式，`week_starts_on` 是 `0`（周一）到 `6`（周日）。
- `input_otp`：值始终是字符串，长度由 `length` 决定。

## 原生下拉与可搜索下拉

`select` 是 reka-ui 的自绘下拉，弹出层被 teleport 到 `<body>`。如果你需要**原生**
`<select>`（表单提交、移动端系统选择器、或者极简的渲染开销），用 `native_select`：

```python
shadcn.native_select({'system': 'System', 'light': 'Light', 'dark': 'Dark'}, value='system')
shadcn.native_select(['a', 'b', 'c'])
```

`native_select` 的 `options` 与其它控件共用同一套规范化规则，但它渲染的是真正的
`<select>` + `<option>`，没有 `placeholder` 参数 —— 需要占位项时自己在选项里加一条。

选项很多时用 `combobox`：它是一个「按钮 + 搜索框 + 选项列表」的组合，输入时在浏览器里做
过滤：

```python
shadcn.combobox({'next': 'Next.js', 'svelte': 'SvelteKit', 'nuxt': 'Nuxt'},
                placeholder='选择框架…',
                search_placeholder='搜索框架…',
                empty_text='没有匹配项')
shadcn.combobox(['Apple', 'Banana', 'Cherry'], filter=False)
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `placeholder` | `'Select an option...'` | 未选中时按钮上的文字 |
| `search_placeholder` | `'Search...'` | 面板内搜索框的占位文字 |
| `empty_text` | `'No results found.'` | 过滤后没有结果时的提示 |
| `filter` | `True` | 是否在浏览器端过滤；`False` 时列表原样展示 |
| `on_select` | `None` | 选中某项时回调 |

`combobox` 与 `select` 一样有 `set_options(...)`，可以运行时换掉整组选项。

## 一次性验证码：`input_otp`

```python
shadcn.input_otp(length=6)
shadcn.input_otp(length=6, groups=[3, 3])
shadcn.input_otp(length=4, pattern=r'^[0-9]+$', on_change=lambda e: ui.notify(e.value))
shadcn.input_otp(length=6, masked=True)
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `length` | `6` | 能输入多少个字符 |
| `groups` | `None` | 分组长度，例如 `[3, 3]` 会渲染成 `123-456` |
| `pattern` | `None` | 逐字符校验的正则源码；模块里也导出了三个现成常量 |
| `masked` | `False` | 用圆点遮住输入内容 |
| `inputmode` | `'numeric'` | 移动端键盘类型 |
| `on_change` | `None` | 值变化回调，`e.value` 是当前完整输入 |

`pattern` 可以直接用模块导出的常量，省得自己写正则。它们既可以从 `shadcn` 侧取，也可以从
`nicegui_shadcn.elements` 导入：

```python
shadcn.input_otp(length=6, pattern=shadcn.REGEXP_ONLY_DIGITS)
```

## 日历与日期选择

`calendar` 是一个内联的月历，`date_picker` 则是「按钮 + popover + calendar」的组合：

```python
import datetime
from nicegui import ui
from nicegui_shadcn import shadcn

shadcn.calendar(value='2026-01-15')
shadcn.calendar(datetime.date(2026, 1, 15), number_of_months=2)
shadcn.calendar(min_value='2026-01-01', max_value='2026-12-31', locale='zh-CN')

shadcn.date_picker(value='2026-01-15', placeholder='选择日期')
picker = shadcn.date_picker(placeholder='选择日期',
                            on_date_change=lambda e: ui.notify(str(e.value)))
picker.value = '2026-02-01'
```

| 参数 | 适用 | 说明 |
| --- | --- | --- |
| `min_value` / `max_value` | 两者 | 可选日期区间（含端点） |
| `week_starts_on` | 两者 | `0` 周一 … `6` 周日；默认按 `locale` 推断 |
| `number_of_months` | `calendar` | 并排显示几个月 |
| `fixed_weeks` | `calendar` | 固定渲染六行，切换月份时高度不跳动 |
| `disabled` / `readonly` | 两者 | 整体禁用；`readonly` 允许聚焦但不允许选 |
| `locale` | 两者 | 月份与星期名的语言，例如 `'zh-CN'` |
| `format_date` | `date_picker` | 把 ISO 字符串转成按钮上显示的文本 |

`calendar` 的回调是 `on_change`，`date_picker` 的是 `on_date_change` —— 两者都存在，但不要
混用。两者都是 `ValueElement`，`.value` 可以直接赋值。

:::{tip}
需要「日期 + 时间」时，把 `date_picker` 与一个 `shadcn.input(type='time')` 拼在一起，
比找第三个组件更省事。
:::

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
