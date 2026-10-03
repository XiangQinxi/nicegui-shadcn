# 基础与按钮

按钮、按钮组，以及所有组件共享的基类与几个工具函数。

`ShadcnElement` 是这套组件的公共基类，它带来 `cn()` 语义：组件自带的类、变体带来的类、
以及调用方传进来的 `classes=` 会一起过一遍 `tw_merge`，同一 CSS 属性上后写的赢。
NiceGUI 3.x 的 `Element.classes()` 只会追加、不做冲突解析，所以想覆盖默认样式时，
要么用构造参数 `classes=`，要么用 `.with_classes()`——直接 `.classes()` 会留下两份互相打架的工具类。

```{eval-rst}
.. automodule:: nicegui_shadcn.elements.base
   :members:
   :show-inheritance:
```

```{eval-rst}
.. automodule:: nicegui_shadcn.elements.shadcn_button
   :members:
   :show-inheritance:
```

```{eval-rst}
.. automodule:: nicegui_shadcn.elements.shadcn_button_group
   :members:
   :show-inheritance:
```

## 图标

`shadcn.icon(name)` 直接吐一个内联 `<svg>`，用的是 lucide 的图标数据（`shadcn.icons.ICON_NAMES`
可以列出全部名字），不依赖图标字体或额外的网络请求。绝大多数组件已经在自己内部画图标了，
只有需要手工放一个的时候才用它。

```{eval-rst}
.. automodule:: nicegui_shadcn.elements.icon
   :members:
   :show-inheritance:
```
