# 表单与输入

文本框、选择器、开关与日期选择。它们都继承自 NiceGUI 的 `ValueElement`（`Input`、`Checkbox`、
`Switch`、`Select` 等还带 `LOOPBACK = False`，输入在浏览器本地回写，不往服务端跑一趟），
因此 `bind_value()`、`value`、`set_value()` 的用法和 NiceGUI 自带控件完全一致。

```{eval-rst}
.. automodule:: nicegui_shadcn.elements.shadcn_form
   :members:
   :show-inheritance:
```

```{eval-rst}
.. automodule:: nicegui_shadcn.elements.shadcn_controls
   :members:
   :show-inheritance:
```

```{eval-rst}
.. automodule:: nicegui_shadcn.elements.shadcn_select
   :members:
   :show-inheritance:
```

```{eval-rst}
.. automodule:: nicegui_shadcn.elements.shadcn_native_select
   :members:
   :show-inheritance:
```

```{eval-rst}
.. automodule:: nicegui_shadcn.elements.shadcn_combobox
   :members:
   :show-inheritance:
```

```{eval-rst}
.. automodule:: nicegui_shadcn.elements.shadcn_input_otp
   :members:
   :show-inheritance:
```

```{eval-rst}
.. automodule:: nicegui_shadcn.elements.shadcn_calendar
   :members:
   :show-inheritance:
```

```{eval-rst}
.. automodule:: nicegui_shadcn.elements.shadcn_date_picker
   :members:
   :show-inheritance:
```
