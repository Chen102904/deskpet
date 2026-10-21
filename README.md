<div align="center">

<img src="docs/hero.png" width="200" alt="白蕾丝小姐">

# 桌宠 · White Lace Pet

一个用 **PySide6** 手搓的 Windows 桌面宠物。

**19 个动作 · 133 句台词 · Q 弹物理形变 · 会自己开地铁和飞机在桌面上乱弹**

Windows 10 / 11 · Python 3.10+ · MIT License

</div>

---

## 这是什么

一个没有窗口、直接站在你桌面上的小型动画程序。

真透明背景（不是假透明、没有白框）、点击穿透到角色轮廓而不是整块矩形、常驻托盘、可以拖动、可以缩放、右键有一整套动作菜单。

它不联网、不上传任何东西、不用账号，双击就活，右键退出就死。

<br>

![19 个动作总览](docs/actions.jpg)

---

## 亮点

**它们不是一段段视频，是一张张 PNG 加上算出来的动画。**

| | |
|---|---|
| **真透明** | `WA_TranslucentBackground` + `Qt.Tool` 无边框窗口，桌面背景下没有白底、没有阴影框 |
| **按像素判定点击** | 判断鼠标位置的 alpha 值，只有点到角色身上才算点中，点她旁边的空气会直接穿过去点到底下的文件 |
| **Q 弹形变** | 阻尼振荡 `sy = 1 - amp·e^(-kt)·cos(2πft)`，横向补偿 `sx = 1/√sy` 保持体积。像果冻，不像整体缩放 |
| **动作不跳位** | 所有立绘锚定在"底边中心"，切动作时底边中心不动，所以她永远是站在地上换姿势，而不是往上跳一格 |
| **甩晕** | 拖她的时候测瞬时速度，连续高帧速就螺旋眼 + 头顶冒星星 + 松手后左右晃 1.8 秒 |
| **零依赖放歌** | 用 Windows 自带的 MCI（`winmm.dll`）播 mp3，不装 ffmpeg、不用 QtMultimedia |
| **动作互斥** | 任何时刻只有一个动作在跑。一个动作进行中你点别的，当前动作立刻取消，不会两个动画叠在一起打架 |

---

## 快速开始

### 方式一：直接跑 exe（推荐给只想玩的）

到 [**Releases**](../../releases) 下载 `WhiteLacePet.exe`，双击。**不用装 Python。**

> 第一次双击可能有点慢（2–3 秒），因为单文件 exe 要先把自己解压到临时目录。
>
> **没有窗口弹出来是正常的** —— 她会直接出现在屏幕右下角，同时任务栏托盘里出现一个小头像。找她就看右下角。

### 方式二：从源码跑

```bash
git clone https://github.com/<your-name>/deskpet.git
cd deskpet

# 建议用虚拟环境，别装到系统 Python 里
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

> 想放歌的话，往 `music/` 里丢几个 `.mp3`，然后右键 →「哈基米形态」。仓库里**故意没有放音乐文件**（版权原因）。

---

## 能怎么玩

| 你做什么 | 她的反应 |
|---|---|
| **左键按住拖** | 变成"被抓"的表情跟着你走，松手自动吸到屏幕边缘。**甩得快会把她摇晕**（螺旋眼 + 头顶星星 + 摇晃 1.8 秒） |
| **左键单击** | 随机来一个动作 + 头顶弹气泡说话 |
| **双击** | 带位移的跳 —— 横向 80–170 像素，最高抬起 46 像素 |
| **鼠标滚轮** | 放大缩小（180 – 760 像素高） |
| **右键**（必须点在她身上） | 弹出主菜单 |
| **动作进行中又点新的** | 当前动作立刻取消，换成新的，永不叠加 |

### 右键菜单里有什么

- **14 个动作**：打招呼 / 玩手机 / 吃棒棒糖 / 喝奶茶 / 看书 / 伸懒腰 / 跳绳 / 举哑铃 / 害羞 / 生气 / 跳一下 / 坐下 / 打盹 / 睡觉
- **开地铁兜一圈** —— 在整个桌面里四边反弹 25 秒，然后收车回原位
- **开飞机兜一圈** —— 同上，往左飞时图片自动水平翻转
- **哈基米形态** —— 用坐姿那张图持续 Q 弹 + 满屏乱弹 30 秒，有歌就顺带放歌
- **打开 music 文件夹** / **大小三档** / **总在最前面** / **定时提醒喝水** / **回到右下角** / **藏到托盘** / **退出**

---

## 19 个动作

| 素材 | 说明 | 素材 | 说明 |
|---|---|---|---|
| `idle` | 站立待机（会随机眨眼） | `stretch` | 伸懒腰 |
| `blink` | 眨眼，随机 3–6 秒触发 | `rope` | 跳绳 |
| `wave` | 打招呼挥手 | `dumbbell` | 举哑铃 |
| `lollipop` | 吃棒棒糖 | `shy` | 害羞 |
| `drink` | 喝奶茶 | `angry` | 生气 |
| `book` | 看书 | `jump` | 跳（带位移） |
| `phone` | 坐着玩手机 | `sit` | 坐下 |
| `nap` | 打盹 | `sleep` | 睡床（睡 90 秒） |
| `grab` | 被拖动时的表情 | `dizzy` | 被甩晕的螺旋眼 |
| `subway` | 开地铁（横图，四边反弹） | `plane` | 开飞机（横图，四边反弹） |
| `haki` | 哈基米形态用的居中方形图 | | |

所有素材都是 800px 高、真透明 PNG，已统一锚点（底边中心对齐到画布 `(512, 1481)`），所以横图竖图混着切换也不会跳位。

---

## 自己加一个动作

三步，不用改动画代码：

**1.** 把动作图画成真透明 PNG，扔进 `assets/`，比如 `assets/dance.png`（**文件名就是动作 id**）。

**2.** 在 `main.py` 的 `LINES` 里加一组台词：

```python
LINES = {
    ...
    "dance": ["跳一个～", "看我的舞步", "这段我练了很久"],
}
```

**3.** 加进 `CLICK_ACTIONS`（点她会随机抽到）或右键菜单列表里：

```python
CLICK_ACTIONS = ["shy", "jump", "wave", ..., "dance"]
```

重跑就行。如果想让它在桌面上自己移动，把 id 加进 `WIDE`（横向铺满那类）或 `SQUARE`（正方形那类），窗口尺寸会自动按比例分流。

---

## 自己打包成 exe

```bash
pip install pyinstaller

pyinstaller --noconfirm --windowed --onefile --name WhiteLacePet ^
    --icon icon.ico --add-data "assets;assets" main.py
```

产物在 `dist/WhiteLacePet.exe`，**40–60MB**（PySide6 本体就大，正常）。

> `--add-data` 在 Windows 用 `;` 分隔，macOS / Linux 要改成 `:`。
>
> 打包后 `__file__` 会指向临时解压目录，所以配置文件的路径必须用 `sys.executable` 推 —— 这段代码里已经处理好了，见 `APP_DIR` 的写法。

**开机自启**：`Win + R` → 输入 `shell:startup` → 把 exe 的快捷方式拖进去。

---

## 项目结构

```
deskpet/
├── main.py              # 全部逻辑（约 1100 行，单文件）
├── selftest.py          # 无头自检：验证素材加载、窗口尺寸、动画行为
├── assets/              # 21 张动作 PNG，800px 高，真透明
│   ├── idle.png  blink.png  wave.png  ...  haki.png
├── music/               # 往这里丢 mp3（.mp3 已被 gitignore）
├── docs/                # README 用的预览图
├── icon.ico             # 托盘 / exe 图标
├── run.bat              # 本地快速启动（避开系统 Python）
├── WhiteLacePet.spec    # PyInstaller 配置
└── requirements.txt
```

自检脚本可以在不弹窗的情况下跑完所有素材和动画逻辑：

```bash
QT_QPA_PLATFORM=offscreen python selftest.py
```

---

## 技术上有意思的几个点

**1. 窗口透明 ≠ 点击透明**

`WA_TranslucentBackground` 只让背景画不出来，鼠标事件仍然落在整个矩形上。想让她旁边的空气能点到底下的桌面图标，得自己在 `mousePressEvent` 里查 alpha：

```python
if self._scaled.pixelColor(pos.x(), pos.y()).alpha() > 30:
    ...  # 真的点在她身上
else:
    e.ignore()   # 放过去
```

阈值取 30 而不是 0，是为了照顾抗锯齿边缘 —— 否则她的轮廓线会变成一圈点不动的死区。

**2. Q 弹用三角函数衰减，不用关键帧**

```python
sy = 1.0 - amp * math.exp(-t * 5.2) * math.cos(t * 2 * math.pi * 3.1)
sy = max(0.72, min(1.22, sy))       # 夹住，别压成负的
sx = 1.0 / math.sqrt(sy)            # 横向补偿，保体积
```

`exp` 负责衰减，`cos` 负责来回振荡，两个一乘就是"弹三下慢慢停"的手感。改 `3.1` 调频率，改 `5.2` 调衰减快慢。

绘制时把变换锚在**底边中心**而不是中心点：

```python
cx, cy = self.width() / 2.0, float(self.height())
p.translate(cx, cy); p.scale(sx, sy); p.translate(-cx, -cy)
```

锚在中心点的话，压扁时她会像被吊在半空一样往上缩；锚在底边才是站在地上被压。

**3. 单张图做出翻转、旋转、Q 弹**

全靠 `QTransform` 组合和 `paintEvent` 里的变换链，不需要任何骨骼动画或 Live2D。

**4. 播 mp3 不装任何库**

```python
self._mci = ctypes.windll.winmm.mciSendStringW
self._mci(f'open "{path}" type mpegvideo alias bgm', None, 0, None)
self._mci('play bgm repeat', None, 0, None)
```

Windows 自带的能力，代价是**只能跑 Windows**，而且从发命令到真出声有几十毫秒延迟（想做音乐卡点的话这是个坑）。

---

## 已知限制

- **只有 Windows 能用** —— 透明窗口和 MCI 音频都是 Windows 专属实现。跨平台要换 `QMediaPlayer` + 平台相关窗口标志。
- **Q 弹是整图缩放，不是网格变形** —— 真果冻效果需要 mesh warp，现在的做法在极端拉伸下会看出"整张图被压扁"，而不是"肉在抖"。
- **动作是帧替换，不是补间** —— 每个动作一张静态图，靠 Q 弹和位移制造动感。想做平滑动画得拆骨绑骨（Live2D 那套），AI 生成的立绘自动拆层目前质量不够。
- **打包体积大** —— PySide6 塞进单文件就是 40–60MB，`--onefile` 还会让首次启动多等 2–3 秒。想要快就用 `--onedir`。

---

## 素材与协议

**代码**：MIT，见 [LICENSE](LICENSE)。随便用、随便改、随便商用，保留署名就行。

**角色美术素材**（`assets/`、`docs/` 下的图片）：**不在 MIT 范围内**。版权归原作者，随仓库提供仅供学习、个人使用和二次创作参考，**不得用于商业用途**，也不得作为商品/服务的主要卖点再分发。

想拿去改自己的角色？完全可以 —— 按上面「自己加一个动作」的步骤换成你自己的图就行，代码部分没有和具体角色绑死。

---

<div align="center">
<sub>用 PySide6 手搓，没有引擎、没有美术外包，就是一个人 + 一堆 PNG。</sub>
</div>
