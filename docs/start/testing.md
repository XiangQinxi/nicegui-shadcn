# 构建与测试

本页是改这个库时的操作手册：怎么构建、跑哪四道验证、每道验证到底证明了什么、以及哪些东西**还没有**被覆盖。

如果你只是用这个库写应用，不需要看本页——用户侧不需要 Node，见 {doc}`/tutorial/installation`。

## 一次性准备

```bash
npm install
```

只有 `devDependencies` 里的四个包（`package.json:19-24`）：`tailwindcss`、`@tailwindcss/cli`、
`esbuild`、`playwright-core`。注意 `playwright-core` **不会下载浏览器**，
它只负责驱动你机器上已经装好的 Edge 或 Chrome。

## 构建：`npm run build`

```bash
npm run build
```

它等于两个子命令（`package.json:14-16`）：

```bash
# build:css —— 编译样式表
tailwindcss -i ./frontend/tailwind.css -o ./nicegui_shadcn/static/shadcn.css

# build:vendor —— 打包 reka-ui
esbuild frontend/vendor/reka-entry.js --bundle --format=esm --target=es2020 \
  --external:vue --minify --legal-comments=none \
  --outfile=nicegui_shadcn/static/vendor/reka-ui.js
```

两者都写进 `nicegui_shadcn/static/`，也就是 wheel 里真正发布的运行时资源。
实测耗时（开发机、Tailwind v4.3.3）：

| 步骤 | 输出 | 耗时 |
| --- | --- | --- |
| `build:css` | `nicegui_shadcn/static/shadcn.css`（192,160 B） | `Done in 158ms` |
| `build:vendor` | `nicegui_shadcn/static/vendor/reka-ui.js`（282,749 B） | `Done in 116ms` |

`npm run build` 的总墙钟大约 2.3 s，因为 npm 自身启动要花掉一秒多；
真正的编译只有约 270 ms，所以「改一行就重建」几乎没有成本。

:::{warning}
**改 `nicegui_shadcn/` 下任何 `.py` 或 `.vue` 之后都必须重建 CSS。**
Tailwind 只产出它看得见的类，而 Python 里的 `classes=` 字符串是它的输入之一。
你新写一个类但没重建，浏览器就只会得到一个没有样式的元素——而且不会有任何报错。
:::

重建的必要性、以及产物为什么是源码的确定性函数，见 {doc}`styling`。

## 四道验证

按顺序跑。前三个是纯 Python，不需要 Node；第四个需要本机浏览器。

### 1. `tests/test_tw_merge.py` —— 62 个用例

```bash
python tests/test_tw_merge.py
```

```
OK - 62 tw_merge cases passed
```

这是唯一一个完全自包含的测试：它不启动服务器、不读 CSS，
只验证 `nicegui_shadcn/_tw_merge.py` 的冲突解析规则。
用例表在 `tests/test_tw_merge.py:15-109`，覆盖的都是曾经出过错或容易出错的形状：

```python
(('h-9 rounded-md bg-primary px-4', 'bg-destructive rounded-full'),
 'h-9 px-4 bg-destructive rounded-full'),      # 同类驱逐 + 保留顺序
(('size-9 w-full', 'size-4'), 'size-4'),         # size- 同时压制 w- 和 h-
(('w-4 h-2', 'w-full'), 'h-2 w-full'),          # 只驱逐冲突的那一半
(('p-4', 'px-2'), 'p-4 px-2'),                   # p- 与 px- 不冲突
(('!p-2', 'p-4'), 'p-4'),                        # important 变体也参与比较
(('my-custom-class', 'my-custom-class'), 'my-custom-class'),   # 未知类原样保留
```

:::{note}
各文档里抄的用例数字会随用例增加而过期（本页写作时 `AGENT.md:54`、`README.md:369`、
`README_zh.md:358` 与实测的 62 一致）。加了一个用例之后，**以脚本自己打印的
`OK - N tw_merge cases passed` 为准**，别去数文档。
:::

### 2. `tests/test_render.py` —— 30 项

```bash
python tests/test_render.py
```

```
all 30 checks passed (77287 bytes of HTML)
```

它会**自己启动 demo**（`tests/test_render.py:69-77`），在一个独立端口上（默认 8137，
`tests/test_render.py:23`，可被 `SHADCN_TEST_PORT` 覆盖），抓首页 HTML 后关掉进程。

30 项由两部分组成：

- 6 项静态断言（`tests/test_render.py:55-63`）：样式表 link、reka-ui 的 import map 条目、
  `reka-ui` 裸标识符被映射、页面标题、按钮的 `bg-primary`、卡片的 `rounded-xl`。
- **每个 `.vue` 派生一项**（`tests/test_render.py:49-52`）：

  ```python
  (f'{path.stem} registered', f'tpl-{path.stem}')
  ```

  即断言服务端 HTML 里有 `tpl-shadcn_xxx` 这个模板 id。
  当前仓库有 24 个 `.vue`，所以 6 + 24 = 30。**新增一个 `.vue` 会让它变成 31，不需要改测试文件。**

任何一项失败时，抓到的 HTML 会被写到 `_render-dump.html`（`tests/test_render.py:95`，
`.gitignore` 已忽略 `_*.html`），方便直接搜。

:::{note}
这项检查只说明「模板被解析并注册了」，不说明组件在浏览器里真的渲染出了东西。
后者由第 4 道验证负责。
:::

### 3. `tests/audit_classes.py` —— 223 个 class token

```bash
python tests/audit_classes.py
```

```
checked 223 class tokens

all referenced classes are present in static/shadcn.css
```

它把 Python 与 Vue 里所有「被当作类」的字符串抽出来，
逐个在 `nicegui_shadcn/static/shadcn.css` 里找对应的选择器；
找不到就打印 `MISSING  <token>  (first seen in <file>)` 并返回 1。
产物不存在时它会直接提示：

```
!! .../nicegui_shadcn/static/shadcn.css is missing — run the Tailwind build first
```

这是四道验证里最容易被忽略、也最有用的一道：Tailwind **静默丢类**，
一个拼错的类只会在浏览器里表现为「没有样式」。它读哪些字符串、命名约束是什么，见 {doc}`styling`。

### 4. `examples/demo.py` + `tests/visual_check.mjs` —— 34 项

这一步需要两个终端。

```bash
# 终端 1
python examples/demo.py
```

```bash
# 终端 2
node tests/visual_check.mjs http://127.0.0.1:8080/
```

```
all visual checks passed
```

它用 `playwright-core` 驱动本机 Edge/Chrome，打开 demo，读取**计算样式**并断言。
这是唯一能证明「设计 token 真的到达了元素」的层次——前三道验证都只看到类名字符串。
它覆盖的内容包括：

- 页面无 console 错误、无 pageerror；`shadcn.css` 确实被加载；`--primary` 是 `oklch(...)`。
- 按钮的 display、圆角、字重、高度（36px），以及主按钮的背景/文字色与
  `var(--primary)` / `var(--primary-foreground)` 一致（用一个 probe 元素取值后比较，
  而不是硬编码颜色——Chromium 会原样回显 `oklch()`）。
- `[data-shadcn_<name>]` 的挂载计数（`tests/visual_check.mjs:112-124` 的 `MOUNTS` 表），
  断言每个注册过的 `.vue` 都真的编译并挂载了，而不是渲染成空。计数是**下界**。
- input 边框等于 `var(--input)` 且高度 36px；checkbox 的对勾 svg `opacity == 1`；
  switch 有 knob；avatar 的 fallback 在圆角容器内。
- tabs 三个 trigger 只有一个 active、其中一个 disabled，且只有活动面板可见；
  accordion 第一项开、第二项关。
- radio 三项一个选中；slider 的 `aria-valuenow=40` / `min=0` / `max=100`；
  toggle 与 toggle group 的 `data-state=on`。
- select trigger 是 `<button>` 且文本为 `System`；dialog 打开后有标题与描述、Escape 能关闭；
  popover 打开且 count 为 1；dropdown menu 至少三个 `role=menuitem`；tooltip hover 后出现。
- 交互一条完整链路：点 Password tab 切面板、在输入框里打字、点 Submit，
  断言 Quasar 的通知回显了新的值——这证明了值确实回写到了服务端。
- 布局：浅色与深色下卡片背景分别等于 `var(--card)` 且两者不同；
  `documentElement.scrollWidth - clientWidth <= 1`；没有卡片被裁剪；
  没有按钮溢出自身盒（`scrollWidth > clientWidth + 1`）。

最后它会把整页截图写到 `_shot-light.png` 和 `_shot-dark.png`（可用 `SHADCN_SHOT_DIR` 改目录）。
退出码：全部通过是 0，有失败是 1（`tests/visual_check.mjs:322`）。

## 端口与默认 URL

三个脚本各有自己的默认端口：

| 位置 | 默认值 | 覆盖方式 |
| --- | --- | --- |
| `examples/demo.py:228-229` | `8080` | `SHADCN_DEMO_PORT` |
| `examples/demo.py:7`（文件头 docstring） | `http://localhost:8080` | — |
| `tests/visual_check.mjs:21` | `http://127.0.0.1:8080/` | 位置参数或 `SHADCN_DEMO_URL` |
| `tests/test_render.py:23` | `8137`（它自己拉起的服务） | `SHADCN_TEST_PORT` |

`tests/test_render.py` 不需要你预先起服务：它用 `SHADCN_DEMO_PORT=8137` 起自己的 demo 进程
（`tests/test_render.py:69-77`），跑完就关。它是唯一会碰端口的 Python 测试。

```bash
npm run build
python tests/test_tw_merge.py          # 不碰服务器
python tests/test_render.py            # 自己起在 8137，跑完就关
python tests/audit_classes.py          # 不碰服务器
python examples/demo.py                # 终端 1：默认 8080
node tests/visual_check.mjs            # 终端 2：默认连 8080
```

`package.json:17` 的 `npm test` 就是 `node tests/visual_check.mjs`，不带参数，
连的正好是 demo 的默认端口，所以上面最后一步也可以直接写成 `npm test`。

:::{warning}
两边端口必须一致，而脚本**不会**给你一句「端口不对」。`tests/visual_check.mjs:69` 的
`page.goto(BASE)` 没有被 `catch` 包住（那里的 `try` 只有 `finally`，见
`tests/visual_check.mjs:62` 与 `:315-317`），连接失败会以未处理的异常直接结束进程——
你看到的是一段 Node 的 `ERR_CONNECTION_REFUSED` 堆栈，而不是 `all visual checks passed`。
只有「找不到浏览器」这一种失败有友好提示并 `exit 2`（`tests/visual_check.mjs:38-39`）。
:::

同理，脚本等的是 demo 里一个**写死的选择器**（`tests/visual_check.mjs:72`）：

```js
await page.waitForSelector('input[placeholder="my-project"]', { timeout: 45000 });
```

改了 `examples/demo.py` 里那个 input 的 placeholder，脚本就会安静地等满 45 秒再超时。

改过端口就把 URL 显式传进去：

```bash
SHADCN_DEMO_PORT=9000 python examples/demo.py            # 终端 1
node tests/visual_check.mjs http://127.0.0.1:9000/       # 终端 2
```

（Windows PowerShell 里是 `$env:SHADCN_DEMO_PORT='9000'; python examples/demo.py`。）

## 没覆盖什么

`tests/visual_check.mjs` 的可信度取决于它**不**声明什么。以下场景目前没有被任何自动化验证覆盖，
改动这些路径时请手动在浏览器里点一遍：

- 打开 select 的下拉并选中一个选项（它只断言 trigger 的标签文本）。
- dropdown menu 的菜单项点击回调。
- slider 的拖动与键盘改值（只读初始的 aria 属性）。
- textarea（只有 input 有样式断言）。
- dialog 内部的组件嵌套。
- popover 里的输入框。
- tooltip 的键盘 focus 路径（只测了 hover）。
- 各控件的 disabled 外观（只测了 tabs trigger 的 disabled 状态）。
- focus trap 的正确性。
- 可访问性名称（accessible name）的质量。

另外它需要一个**外部已经启动的 demo**：脚本自己不会拉起服务。
它也不会下载浏览器——按固定顺序探测（`tests/visual_check.mjs:24-34`）：

```
$CHROME_PATH
C:\Program Files\Microsoft\Edge\Application\msedge.exe
C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
C:\Program Files\Google\Chrome\Application\chrome.exe
C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe
/usr/bin/google-chrome
/usr/bin/chromium
/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
```

全部不存在时直接失败并退出：

```
!! no local Chromium found; set CHROME_PATH to one
```

退出码是 **2**（区别于「检查失败」的 1）。用 `CHROME_PATH` 指到你自己的浏览器可执行文件即可。

## 提交前

```bash
npm run build
git status
```

**编译产物是源码的确定性函数**（`source(none)` + 显式 `@source`，见 {doc}`styling`），
所以只要源码没变，重建之后 `nicegui_shadcn/static/` 应该**完全没有改动**。
如果 `git status` 里出现了这两个文件，说明源码确实变了——把产物一起提交。

完整的提交前清单见 {doc}`component-authoring` 的最后一节；打包与版本号同步见 {doc}`packaging`。

## 常见失败

| 现象 | 原因 | 修法 |
| --- | --- | --- |
| `!! .../shadcn.css is missing` | 从没构建过，或产物被清掉 | `npm run build` |
| `MISSING  mt-8  (first seen in xxx.py)` | 新写的类没进产物 | `npm run build`；若是运行期字符串，加进 `@source inline(...)` |
| `!! no local Chromium found`（退出码 2） | 没装 Edge/Chrome 或路径不在探测列表 | 设 `CHROME_PATH` |
| 视觉检查全部超时 / 连接被拒 | demo 没起，或端口不对 | 起 demo，并显式传 URL（8080） |
| `RuntimeError: the demo app did not come up: …` | 8137 被占用，或 demo 起不来 | 设 `SHADCN_TEST_PORT`，或先手动跑一次 `python examples/demo.py` 看报错 |
| 视觉检查过的仍然是旧样式 | demo 进程还在跑旧代码 | `examples/demo.py` 用 `reload=False`，改完代码必须重启 |
| 本地跑得好、CI 上差一项 | 浏览器版本或字体不同导致的计算值差异 | 先看具体是哪一项，不要直接放宽断言 |
