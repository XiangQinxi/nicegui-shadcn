# 打包与发布

本页讲这个库是怎么被打成 wheel 和 sdist 的、发布前必须补齐什么、以及怎么在一个干净环境里验证产物。
改源码的流程见 {doc}`component-authoring`，构建与测试见 {doc}`testing`。

## 发布出去的到底是什么

最终用户拿到的是一个**纯 Python 包**：没有编译步骤、没有 Node 依赖，
两份预编译资源（样式表和 reka-ui bundle）已经躺在包里。

| 内容 | wheel | sdist |
| --- | --- | --- |
| `nicegui_shadcn/**`（Python、`.vue`、`static/`） | ✅ | ✅ |
| `LICENSE` | ✅ | ✅ |
| `README.md`、`pyproject.toml`、`PKG-INFO` | 元数据里 | ✅ |
| `frontend/`（Tailwind 源、`reka-entry.js`） | ❌ | ✅ |
| `examples/`、`tests/` | ❌ | ✅ |
| `package.json`、`package-lock.json`、`AGENT.md` | ❌ | ✅ |
| `docs/`（Sphinx 源；`docs/_build/` 除外） | ❌ | ✅ |
| `poetry.lock`、`dist/` | ❌ | ❌ |

仓库里现成的 0.1.2 产物可以直接核对：

```
dist/nicegui_shadcn-0.1.2-py3-none-any.whl    168,622 B   49 个条目
dist/nicegui_shadcn-0.1.2.tar.gz              544,174 B   91 个文件
```

wheel 里只有 `nicegui_shadcn/` 下的 45 个文件，加上 `dist-info/licenses/LICENSE`、
`METADATA`、`WHEEL`、`RECORD`。

## `pyproject.toml` 的打包规则

用的是 **Poetry + PEP 621**：元数据写在标准的 `[project]` 表里，
构建后端是 `poetry-core`：

```toml
[build-system]
requires = ["poetry-core>=2.0"]
build-backend = "poetry.core.masonry.api"
```

### `packages`：只有一个可导入包

```toml
[tool.poetry]
packages = [{ include = "nicegui_shadcn" }]
```

`pyproject.toml:41-43` 的注释说明了为什么构建输入要放在包外：
`frontend/` **不是可导入包的一部分**，它是构建输入，只进 sdist。

### `include`：`.vue` 与 `static/` 必须显式列出

```toml
include = [
    { path = "nicegui_shadcn/elements/*.vue", format = ["sdist", "wheel"] },
    { path = "nicegui_shadcn/static/**/*", format = ["sdist", "wheel"] },
    # The build inputs and the development artifacts only belong in the sdist:
    { path = "frontend", format = ["sdist"] },
    { path = "examples", format = ["sdist"] },
    { path = "tests", format = ["sdist"] },
    { path = "package.json", format = ["sdist"] },
    { path = "package-lock.json", format = ["sdist"] },
    { path = "AGENT.md", format = ["sdist"] },
]
```

Poetry 默认只收包内的 `*.py`。但 `.vue` 模板是 NiceGUI 在 `import` 时读的，
`static/` 下的两份文件是要通过 HTTP 提供的——**不显式列出来，发布出去的 wheel 一 `import` 就坏**
（`pyproject.toml:46-50` 的注释就是这么写的）。

:::{warning}
**新增任何运行时文件（新的 `.vue`、新的静态资源）都必须改这个 `include` 列表。**
`frontend/` 里的东西永远不该进 wheel：它只服务于「有人想从源码重建样式表」这个场景，
而这类人需要的是 sdist。
:::

### 两个元数据上的坑

```toml
license = "MIT"
license-files = ["LICENSE"]
requires-python = ">=3.10,<4.0"
```

- **`requires-python` 必须带上界。** 只写 `>=3.10` 会让 pip 在 Python 4 上安装这个包，
  而 NiceGUI 的扩展契约（`__init_subclass__` 的关键字参数）是 3.x 的行为。
- **许可证用 PEP 639 的写法：`license` 加 `license-files`。**
  `pyproject.toml:21-31` 的 classifiers 里**故意没有** `License ::` 这一条——
  PEP 639 下 `license` 与 `License ::` classifier 同时存在会冲突。
  构建出的 `METADATA` 因此长这样（已用现成 wheel 核对）：

  ```
  Metadata-Version: 2.4
  License-Expression: MIT
  License-File: LICENSE
  Requires-Python: >=3.10,<4.0
  Requires-Dist: nicegui (>=3.0)
  ```

- 运行时依赖只有一条：`dependencies = ["nicegui>=3.0"]`（`pyproject.toml:32`）。
  `package.json` 里的那些 npm 包只是构建依赖，不会进 wheel 的依赖列表。

### `.gitignore` 会参与 sdist 的构建

`.gitignore` 顶部的注释写着这一点：**Poetry 构建 sdist 时尊重 `.gitignore`**，
所以被忽略的东西不会进源码分发。当前被忽略且因此不进 sdist 的包括：
`dist/`、`build/`、`node_modules/`、`__pycache__/`、`docs/_build/`、
`_shot-*.png`、`/_*.py`、`/_*.html`、`demos/`。

这既是保护也是陷阱：如果你把某个**必须随源码分发**的文件误加进了 `.gitignore`，
它会静默地从 sdist 里消失。

## 版本号必须三处同步

| 位置 | 内容 |
| --- | --- |
| `pyproject.toml:3` | `version = "0.1.2"` |
| `nicegui_shadcn/__init__.py:57` | `__version__ = '0.1.2'` |
| `package.json:3` | `"version": "0.1.2"` |

第三处容易被忘：它是 npm 侧的构建工具链版本，虽然 `private: true` 不会发布到 npm，
但 `npm run build` 的产物与它绑定，版本漂移会让「这个 CSS 是哪个版本编译的」变得不可考。

改完可以用一条命令自查（PowerShell）：

```powershell
Select-String -Path pyproject.toml, nicegui_shadcn\__init__.py, package.json -Pattern '\d+\.\d+\.\d+'
```

文档站的版本号不需要手动改：`docs/conf.py` 会从 `pyproject.toml` 的 `[project].version` 读。

## 构建

```bash
poetry check          # 元数据与 pyproject 语法自检
poetry build          # 同时产出 wheel 和 sdist 到 dist/
```

然后**检查 `dist/` 的内容**，而不是只看构建成功：

```bash
python -c "import zipfile;print('\n'.join(zipfile.ZipFile('dist/nicegui_shadcn-0.1.2-py3-none-any.whl').namelist()))"
python -c "import tarfile;print('\n'.join(tarfile.open('dist/nicegui_shadcn-0.1.2.tar.gz').getnames()))"
```

要确认的是三件事：`.vue` 在 wheel 里、`static/` 三个文件（`shadcn.css`、`vendor/reka-ui.js`、
`base-colors.json`）在 wheel 里、`docs/` 只在 sdist 里。

## 在干净环境验证 wheel

这一步不能省。**必须在全新的虚拟环境里，而且工作目录要在仓库之外**——
否则当前目录会被放进 `sys.path`，`import nicegui_shadcn` 命中的是你的 checkout，
而不是刚装上的 wheel，验证就变成了自欺。

```bash
python -m venv /tmp/verify-shadcn
/tmp/verify-shadcn/bin/python -m pip install dist/nicegui_shadcn-0.1.2-py3-none-any.whl
```

```bash
cd /tmp          # 关键：不要站在仓库根目录里
/tmp/verify-shadcn/bin/python -c "
import nicegui_shadcn, pathlib
print(nicegui_shadcn.__version__)
print(nicegui_shadcn.__file__)                       # 必须是 site-packages，不是 checkout
p = pathlib.Path(nicegui_shadcn.theme.STATIC_DIR)
print(sorted(x.name for x in p.rglob('*') if x.is_file()))
"
```

Windows 上把路径换成 `C:\Temp\verify-shadcn\Scripts\python.exe` 即可。

最后起一个真实的页面，确认样式与 reka-ui 都能加载：

```bash
/tmp/verify-shadcn/bin/python -c "
from nicegui import ui
from nicegui_shadcn import shadcn
with shadcn.card():
    shadcn.card_title('hello')
    shadcn.select(['a', 'b'])
ui.run(port=8099, show=False, reload=False)
"
```

页面出来后看两点：按钮/卡片的颜色是 shadcn 的（不是 Quasar 蓝），
以及 `<select>` 那个组件有正常的触发器样式——后者依赖 `static/vendor/reka-ui.js` 与 import map。

## 发布

```bash
poetry publish --build          # 构建 + 上传
```

:::{danger}
**`poetry publish` 默认不重新构建，只上传 `dist/` 里已有的文件。**
改了源码却忘了 `poetry build`，上传的就是上一版产物——而且版本号一样，PyPI 会直接拒收或静默覆盖你本地的认知。
要么永远用 `--build`，要么严格按 `poetry build` → 检查 `dist/` → `poetry publish` 的顺序做。
:::

先走 TestPyPI：

```bash
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi <token>
poetry publish --repository testpypi --build
```

确认无误再上正式：

```bash
poetry config pypi-token.pypi <token>
poetry publish --build
```

`poetry publish --dry-run` 可以在不真正上传的前提下走一遍流程。

:::{note}
token 不要写进任何会被提交的文件。`poetry config pypi-token.pypi` 会把它存到 Poetry 自己的
用户级配置目录里，这也是 README 推荐的用法；CI 上则用环境变量 `POETRY_PYPI_TOKEN_PYPI`。
:::

## 发布前还差什么

`pyproject.toml:34-38` 现在是**注释掉的占位**，里面的用户名还是 `<you>`：

```toml
# Fill these in before publishing — PyPI shows them on the project page.
# [project.urls]
# Homepage = "https://github.com/<you>/nicegui-shadcn"
# Repository = "https://github.com/<you>/nicegui-shadcn"
# Issues = "https://github.com/<you>/nicegui-shadcn/issues"
```

发布前必须把这三条填好并取消注释，否则 PyPI 项目页上不会有任何回链。
`README.md` 里的相对路径截图同理：PyPI 渲染 README 时相对路径会失效，
README 目前用的是仓库内的 `docs/` 截图（`docs/demo-light.png`、`docs/demo-dark.png`），
这一点在 {doc}`/tutorial/limitations` 里有记录。

发布前清单：

- [ ] `npm run build` 后 `git status` 干净（产物是源码的确定性函数，见 {doc}`testing`）
- [ ] 四道验证全过（见 {doc}`testing`）
- [ ] 三处版本号一致
- [ ] `poetry check` 通过
- [ ] `[project.urls]` 已填写并取消注释
- [ ] 新增运行时文件 → 已在 `[tool.poetry].include` 里列出
- [ ] `poetry build` 后检查过 `dist/` 的文件列表
- [ ] 在**仓库之外**的全新 venv 里装过 wheel 并起过一次页面
- [ ] 需要的话先发 TestPyPI
