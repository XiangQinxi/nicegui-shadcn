# 安装

`nicegui-shadcn` 是一个纯 Python 包：使用它不需要 Node.js，也没有构建步骤。编译好的
Tailwind 样式表和 `reka-ui` 的 ESM bundle 都以预编译的形式随 wheel 一起发布。

## 环境要求

| 项目 | 要求 | 说明 |
| --- | --- | --- |
| Python | `>=3.10,<4.0` | `pyproject.toml` 里同时声明了上下界 |
| 运行时依赖 | `nicegui>=3.0` | 由包自动拉入 |
| NiceGUI | 3.x | 本库依赖 3.x 的扩展接口与 `VBuild` |
| Node.js | 可选 | 只有重新构建静态资源时才需要 |

`requires-python` 的上界不是装饰：Poetry 在解析依赖时需要一个上界，裸写 `>=3.10` 会让
`poetry lock` 直接报错。

## 从 PyPI 安装

```bash
pip install nicegui-shadcn
```

这一条命令会把 `nicegui>=3.0` 一起装好。如果你的项目另外固定了 NiceGUI 的版本，请确认它
仍然满足 `>=3.0`：本库直接使用 NiceGUI 3.x 的扩展机制（`Element.__init_subclass__` 的
`component=` / `dependencies=` / `esm=` 参数，以及
`nicegui.dependencies.register_importmap_override`），在 2.x 上无法工作。

## 最小验证

安装完成后，下面这个页面应该立刻能跑起来：

```python
from nicegui import ui
from nicegui_shadcn import shadcn

with shadcn.card():
    with shadcn.card_header():
        shadcn.card_title('nicegui-shadcn')
        shadcn.card_description('看到带边框的卡片和圆角按钮就说明样式生效了。')
    with shadcn.card_content():
        shadcn.input(placeholder='Name')
    with shadcn.card_footer():
        shadcn.button('Deploy', on_click=lambda: ui.notify('Deployed'))

ui.run()
```

:::{tip}
判断样式是否真的生效，看按钮的颜色：它应该是 shadcn 的近黑色 `--primary`，而不是 Quasar
默认的蓝色。如果整页是无样式的裸 HTML，说明样式表没被加载，请检查浏览器控制台的网络面板里
是否有 `/_nicegui_shadcn/shadcn.css` 这条请求。
:::

## 看一下全部组件

仓库自带一个渲染了所有组件的演示应用：

```bash
python examples/demo.py        # 然后打开 http://localhost:8080
```

端口由环境变量 `SHADCN_DEMO_PORT` 控制，默认是 `8080`：

```bash
SHADCN_DEMO_PORT=9000 python examples/demo.py
```

```powershell
$env:SHADCN_DEMO_PORT = '9000'; python examples/demo.py
```

## 从源码安装（开发）

如果你要改的是这个库本身，而不只是使用它：

```bash
git clone https://github.com/XiangQinxi/nicegui-shadcn.git
cd nicegui-shadcn
poetry install
```

`pip install -e .` 也可以，两者都会以可编辑模式装上 `nicegui_shadcn`。

只有需要**重新生成**随包发布的静态资源时才需要 Node：

```bash
npm install        # 安装 Tailwind v4 CLI、esbuild、playwright-core 等构建工具
npm run build      # = npm run build:css + npm run build:vendor
```

`npm run build` 展开后就是 README 里那两条命令：

```bash
npx @tailwindcss/cli -i ./frontend/tailwind.css -o ./nicegui_shadcn/static/shadcn.css
npx esbuild frontend/vendor/reka-entry.js --bundle --format=esm --target=es2020 \
    --external:vue --minify --legal-comments=none --outfile=nicegui_shadcn/static/vendor/reka-ui.js
```

:::{warning}
改动 `nicegui_shadcn/` 下任何 `.py` 或 `.vue` 文件之后都必须重新构建 CSS。Tailwind 只会
输出它扫描到的工具类，新增的 class 如果没被重新编译就不会出现在样式表里 —— 而且**不会有
任何报错**，只是样式静默失效。仓库里的 `tests/audit_classes.py` 就是专门用来抓这个失败
模式的。
:::

## 下一步

- {doc}`how-it-works` —— 导入 `nicegui_shadcn` 时到底发生了什么。
- {doc}`usage` —— 立刻要用的 `classes=`、`variant=`、`size=`。
- {doc}`/start/styling` —— 想用编译产物之外的 class 时怎么扩展样式表。
