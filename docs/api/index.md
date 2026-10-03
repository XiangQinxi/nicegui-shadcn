# API 参考

这一节由 [Sphinx autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html)
直接从源码生成：每个组件类与工厂函数的签名、参数说明都读自 `nicegui_shadcn/` 里的 docstring，
没有第二份需要手工同步的 API 清单。改了代码注释，这里的页面下次构建时就跟着变。

## 两种等价的引入方式

组件既可以从 `shadcn` 命名空间取，也可以直接从 `nicegui_shadcn.elements` 导入：

```python
from nicegui_shadcn import shadcn

shadcn.button('保存', variant='outline', on_click=save)
```

```python
from nicegui_shadcn.elements import Button

Button('保存', variant='outline', on_click=save)
```

下面每一页按模块列出：先是实现该组件的类，然后是它的工厂函数简写。工厂函数只是
`类(...)` 的一行包装，参数表完全一致，用哪个都不会少拿到东西。

## 参数是怎么写的

参数统一写成 reStructuredText 字段列表，autodoc 原生就能识别：

```text
:param text: the label of the button.
:param variant: ``default``, ``destructive``, ``outline``, ``secondary``,
    ``ghost`` or ``link``.
```

Google 风格（`Args:`）与 NumPy 风格（`Parameters` 段）也都能渲染——`docs/conf.py`
里打开了 `sphinx.ext.napoleon`——但本库统一用上面这一种。新增组件时请照着写，
`tests/check_docstrings.py` 会检查每个公开参数都在 docstring 里出现过。

## 只列本库自己的成员

每个类都继承自 NiceGUI 的 `Element`，所以 `props()`、`classes()`、`on()`、`bind_value()`
这些通用方法不在这里重复——它们属于 NiceGUI，请查
[NiceGUI 官方文档](https://nicegui.io/documentation)。本参考只覆盖
`nicegui_shadcn` 自己定义的东西。

```{toctree}
:maxdepth: 1

forms
display
overlays
navigation
primitives
theming
```
