# 折叠

折叠这一组包含两种东西：**accordion**（手风琴，垂直折叠）与 **tabs**（标签页）。两者都由
reka-ui 的原语驱动，因此键盘导航、方向键与 `aria` 属性都是现成的。

## accordion

```python
with shadcn.accordion(value='shipping'):
    with shadcn.accordion_item(value='shipping'):
        shadcn.accordion_trigger('How do you ship?')
        with shadcn.accordion_content():
            ui.label('By carrier pigeon.')
    with shadcn.accordion_item(value='returns'):
        shadcn.accordion_trigger('What is your return policy?')
        with shadcn.accordion_content():
            ui.label('30 days.')
```

| 工厂函数 | 位置参数 | 关键字参数 |
| --- | --- | --- |
| `shadcn.accordion` | — | `value`、`multiple`、`collapsible`、`orientation`、`on_change` |
| `shadcn.accordion_item` | `value`（**必填**） | `disabled` |
| `shadcn.accordion_trigger` | `text` | — |
| `shadcn.accordion_content` | — | — |

### accordion 的 `value` 语义

`accordion(value=…)` 的 `value` 决定**最初展开哪一项**，而 `accordion_item(value=…)` 的
`value` 是这一项的身份标识。两者按字符串匹配。

在单选模式下，`value` 是一个字符串（`''` 表示全部收起）；在 `multiple=True` 时，`value`
是一个字符串列表：

```python
shadcn.accordion(['shipping', 'returns'], multiple=True)   # 同时展开两项
```

运行时改变展开状态就是给 `value` 赋值：

```python
accordion = shadcn.accordion(value='shipping', on_change=lambda e: ui.notify(str(e.value)))
accordion.value = 'returns'
```

### 单选 / 多选 / 可折叠

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `multiple` | `False` | `True` 时映射为 reka 的 `type="multiple"`，`value` 变成列表 |
| `collapsible` | `True` | 单选模式下是否允许把已展开的项再收起 |
| `orientation` | `'vertical'` | 方向键语义 |

:::{note}
`collapsible` 只在单选模式下有意义：`multiple=True` 时内部会强制把它设为 `False`，因为
“全部收起”在多选模式下是正常状态，不需要额外开关。
:::

`accordion_item(disabled=True)` 会让该项不可点击，`aria-disabled` 也会同步。

:::{tip}
`accordion_trigger` 的 `classes=` 会落到内层的 `<button>`，而不是外层的 `<h3>` —— 这是为了让
你的样式能真正作用在可点击区域上。
:::

## tabs

标签页有一个重要区别必须记住：**标签按钮是以数据形式传入的，而标签面板是普通的 NiceGUI
子元素**。

```python
with shadcn.tabs(value='account'):
    shadcn.tabs_list([('account', 'Account'),
                      ('password', 'Password'),
                      {'value': 'disabled', 'label': 'Disabled', 'disabled': True}])
    with shadcn.tabs_content(value='account'):
        shadcn.input(value='Ada Lovelace')
    with shadcn.tabs_content(value='password'):
        shadcn.input(placeholder='Current password', type='password')
```

| 工厂函数 | 位置参数 | 关键字参数 |
| --- | --- | --- |
| `shadcn.tabs` | — | `value`、`orientation`、`on_change` |
| `shadcn.tabs_list` | `tabs` | `orientation` |
| `shadcn.tabs_content` | `value`（**必填**） | — |

### 为什么标签是数据驱动的

reka-ui 的 `TabsList` 会 `provide` 一个 roving-focus context，供 `TabsTrigger` `inject`。
这种注入无法穿过 NiceGUI 的 slot 传递 —— 如果 trigger 由你在 `with shadcn.tabs_list():`
里手写，它会抛 `` Injection `Symbol(RovingFocusGroupContext)` not found ``。

所以 trigger 在 `tabs_list` 组件内部生成。好处是方向键导航、焦点环、`aria-selected` 全部
保持正确；代价是一个标签**不能包含任意 NiceGUI 子元素**，它只接受一个 label 字符串。

:::{warning}
下面这种写法是不成立的，请勿尝试：

```python
with shadcn.tabs_list():          # 没有 tabs 参数 → 标签栏是空的
    shadcn.button('Account')      # 不会被当成标签
```

标签只能通过 `shadcn.tabs_list([...])` 的数据参数给出。
:::

### tabs 的 `value` 语义

`tabs(value=…)` 决定选中的标签，`tabs_content(value=…)` 的 `value` 与 `tabs_list` 里对应
项的值匹配。`tabs` 的 `value` 可以是字符串或整数，内部统一转成字符串比较。

```python
tabs = shadcn.tabs(value='account', on_change=lambda e: ui.notify(e.value))
tabs.value = 'password'
```

### 禁用项与动态标签

```python
shadcn.tabs_list(['account', 'password', 'disabled'])          # value == label
shadcn.tabs_list({'account': 'Account', 'password': 'Password'})
shadcn.tabs_list([{'value': 'x', 'label': 'X', 'disabled': True}])
```

四种写法共用与 `select` 相同的规范化规则，详见 {doc}`usage`。运行时要换掉整组标签，用
`set_tabs(...)`：

```python
tabs_list = shadcn.tabs_list(['a', 'b'])
tabs_list.set_tabs(['x', 'y', 'z'])
```

### 面板是常驻的

`tabs_content` 的面板**始终留在 DOM 里**，只是被 `data-[state=inactive]:hidden` 隐藏。因此
切换标签不会重置面板里的表单 —— 输入框的值会保留，服务端也总能找到这些元素。这个行为的
代价见 {doc}`limitations`。

## 下一步

- {doc}`overlays` —— dialog 与 popover，另一种“按需显示”的组织方式。
- {doc}`limitations` —— 为什么 accordion 没有关闭动画。
