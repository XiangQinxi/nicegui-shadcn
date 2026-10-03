# nicegui-shadcn

**为 [NiceGUI](https://nicegui.io) 打造的 [shadcn/ui](https://ui.shadcn.com) 组件集。**
预编译的 Tailwind v4 主题随包分发，`pip install` 之后直接可用，使用者端不需要任何构建步骤。

```{image} demo-light.png
:alt: nicegui-shadcn 浅色主题演示
:class: only-light screenshot
:width: 100%
```

```{image} demo-dark.png
:alt: nicegui-shadcn 深色主题演示
:class: only-dark screenshot
:width: 100%
```

<sub>浅色与深色都由 `body.body--dark` 驱动，点击右上角的主题切换按钮即可切换。</sub>

---

```{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} 教程
:link: tutorial/index
:link-type: doc
:margin: 0

从安装、工作原理，到布局、表单、展示、折叠、浮层与图标——把基础用法完整过一遍。
:::

:::{grid-item-card} API 参考
:link: api/index
:link-type: doc
:margin: 0

由 Sphinx autodoc 直接从源码 docstring 生成：每个组件类与工厂函数的签名和参数说明。
:::

:::{grid-item-card} 开始
:link: start/index
:link-type: doc
:margin: 0

面向想动手改这个库的人：组件制作、样式与主题、构建与测试、打包与发布。
:::

```

## 安装

```bash
pip install nicegui-shadcn
```

## 最小示例

```python
from nicegui import ui
from nicegui_shadcn import shadcn

state = {'name': 'my-project'}

shadcn.label('项目名称')
shadcn.input(placeholder='my-project').bind_value(state, 'name')
shadcn.button('保存', on_click=lambda: ui.notify(f"已保存 {state['name']}"))

ui.run()
```

样式表由 `nicegui_shadcn` 在导入时自动注册，不需要你在 NiceGUI 里额外引入任何东西。

```{toctree}
:hidden:
:maxdepth: 2

tutorial/index
api/index
start/index
```
