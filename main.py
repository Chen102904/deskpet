# -*- coding: utf-8 -*-
"""
桌面宠物 · 白蕾丝小姐
PySide6 实现：真透明窗口、置顶、可拖动、点击互动、右键菜单、托盘常驻。

运行：python main.py
打包：pyinstaller --noconfirm --windowed --onefile --name WhiteLacePet ^
      --icon icon.ico --add-data "assets;assets" main.py
"""
import json
import math
import os
import random
import sys
import time
from datetime import datetime

from PySide6.QtCore import QPoint, QRect, Qt, QTimer
from PySide6.QtGui import (QAction, QColor, QCursor, QFont, QIcon, QImage,
                           QPainter, QPixmap, QPolygon, QTransform)
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QWidget


# ---------------------------------------------------------------- 资源路径
def res(*parts):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


ASSET_DIR = res("assets")

# 打包成 exe 后 __file__ 在临时解压目录，配置要写到 exe 旁边才不会丢
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(APP_DIR, "config.json")

# ---------------------------------------------------------------- 台词库
LINES = {
    "idle": [
        "在的在的～", "叫我干嘛呀", "我在这儿陪你", "今天也要加油哦",
        "摸鱼一下也没关系啦", "喝水了吗？", "坐久了起来走两步吧",
        "我一直看着你哦", "要不要歇一会儿",
    ],
    "wave": [
        "你好呀～", "嗨嗨！", "回来啦？", "又见面了", "欢迎回来～",
        "好久不见！", "我等你很久了", "今天过得怎么样？", "在忙什么呢",
        "有事就叫我哦",
    ],
    "lollipop": [
        "草莓味的，最好吃", "要不要也来一根", "舔一口心情就好啦",
        "这个不给你吃哦", "甜的东西治愈一切", "含着糖就不困了",
    ],
    "drink": [
        "喝口奶茶续命", "要不要也来一杯", "糖分补充中…", "三分糖，谢谢",
        "这杯是犒劳自己的", "喝完这杯继续加油",
    ],
    "book": [
        "我在看书，别打扰", "这段好难懂…", "学到新东西了", "安静看会儿书",
        "你也要多读书哦", "看到精彩的地方了",
    ],
    "stretch": [
        "伸个懒腰～", "好酸啊…", "坐太久了，你也起来动动",
        "骨头咔咔响", "啊——舒服", "拉一拉，长得高",
    ],
    "shy": [
        "别、别突然戳我啦…", "唔…有点痒", "讨厌啦～", "脸好烫…",
        "不要一直盯着看", "这样很害羞的", "哼…也不是不喜欢啦",
    ],
    "angry": [
        "再点我就要生气了！", "哼！", "你工作不专心哦", "别戳了别戳了",
        "我很凶的哦", "真拿你没办法", "生气气，哄不好的那种",
    ],
    "jump": [
        "耶！", "跳一下！", "精神来了！", "看我跳得高不高",
        "蹦蹦蹦～", "运动一下更健康",
    ],
    "sit": [
        "坐下歇会儿", "腿有点酸", "陪我坐一会儿", "站久了要坐下",
        "这里风景不错", "一起偷个懒吧",
    ],
    "rope": [
        "一百下…九十九…", "跳绳减肥！", "呼、呼，好累", "你也来跳两下",
        "再跳五十个就休息", "绳子别抽到我",
    ],
    "dumbbell": [
        "举铁中…别打扰", "一、二、一、二", "手臂好酸啊", "练完就能吃蛋糕了",
        "我要变强壮！", "再来一组",
    ],
    "phone": [
        "刷会儿手机…", "在看什么呢", "有你的消息哦", "别抢，我在回信息",
        "手机真好玩", "再刷五分钟就睡",
    ],
    "subway": [
        "上车吧，下一站到你心里", "本列车开往：下班", "叮咚，请站稳扶好",
        "我是司机哦", "这趟车不收费",
    ],
    "plane": [
        "系好安全带，起飞咯", "看，云在下面", "风好大呀", "要一起飞吗",
        "目的地：不想上班", "塔台，请求起飞",
    ],
    "nap": [
        "打个盹…", "就眯五分钟", "呼…呼…", "别吵，我小睡一会",
        "眼皮好重…",
    ],
    "sleep": [
        "困了…先睡一会儿", "晚安…", "呼…呼…", "别吵我啦…",
        "床好软…", "做梦也要甜甜的",
    ],
    "grab": [
        "哇啊！放我下来！", "别晃别晃～", "要掉了要掉了", "抓这么高干嘛！",
        "轻一点啦…", "我恐高！",
    ],
}

# 按时段说的问候（点她时如果抽到打招呼，优先说这些）
GREET = {
    "dawn": ["这么早就起来啦？", "天还没亮呢…", "早安，先喝杯水吧"],
    "morning": ["早上好～", "早安！今天也要加油", "早饭吃了吗"],
    "noon": ["中午了，吃饭没？", "该吃午饭啦", "午休一下再干"],
    "afternoon": ["下午好～", "下午容易犯困，撑住", "来杯咖啡？"],
    "evening": ["晚上好呀", "今天辛苦了", "下班了吗？"],
    "night": ["这么晚还不睡？", "夜深了，早点休息", "别熬夜哦，真的"],
}

# 会随机自动出现的动作
IDLE_ACTIONS = ["wave", "drink", "lollipop", "book", "stretch",
                "shy", "angry", "jump", "sit", "nap", "phone",
                "rope", "dumbbell"]

# 点击时会随机做的动作
CLICK_ACTIONS = ["shy", "jump", "wave", "angry", "lollipop",
                 "stretch", "book", "phone", "rope", "dumbbell"]

# 横向素材：程序会给它们单独开横向窗口
WIDE = {"subway", "plane"}
# 正方形素材：哈基米形态用正方形窗口
SQUARE = {"haki"}


def greet_text():
    h = datetime.now().hour
    if 4 <= h < 7:
        key = "dawn"
    elif 7 <= h < 11:
        key = "morning"
    elif 11 <= h < 14:
        key = "noon"
    elif 14 <= h < 18:
        key = "afternoon"
    elif 18 <= h < 23:
        key = "evening"
    else:
        key = "night"
    return random.choice(GREET[key])


# ---------------------------------------------------------------- 背景音乐
class Music:
    """用 Windows 自带的 MCI 接口放 mp3，不依赖 QtMultimedia，也不用装任何东西。"""

    def __init__(self):
        self.alias = "lacedoll_bgm"
        self.opened = False
        self._mci = None
        try:
            import ctypes
            self._mci = ctypes.windll.winmm.mciSendStringW
            self._mci.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p,
                                  ctypes.c_uint, ctypes.c_void_p]
        except Exception:
            self._mci = None

    def _send(self, cmd):
        if self._mci is None:
            return 1
        buf = __import__("ctypes").create_unicode_buffer(512)
        return self._mci(cmd, buf, 510, None)

    def play(self, path, repeat=True):
        if self._mci is None or not os.path.isfile(path):
            return False
        self.close()
        ok = self._send(f'open "{path}" type mpegvideo alias {self.alias}')
        if ok != 0:                      # 有些文件要让它自己判断类型
            ok = self._send(f'open "{path}" alias {self.alias}')
        if ok != 0:
            return False
        self.opened = True
        self._send(f"play {self.alias}" + (" repeat" if repeat else ""))
        return True

    def stop(self):
        if self.opened:
            self._send(f"stop {self.alias}")

    def close(self):
        if self.opened:
            self._send(f"close {self.alias}")
            self.opened = False


# ---------------------------------------------------------------- 气泡窗口
class Bubble(QWidget):
    """角色头顶的对话气泡，圆角白底，1.8 秒后淡出"""

    def __init__(self):
        super().__init__(None,
                         Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.text = ""
        self.fade = 1.0
        self._elapsed = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

    def show_text(self, text, anchor_bottom_center):
        self.text = text
        fm = self.fontMetrics()
        w = min(max(fm.horizontalAdvance(text) + 46, 120), 460)
        self.resize(w, 54)
        x = anchor_bottom_center.x() - w // 2
        y = anchor_bottom_center.y() - 54
        scr = QApplication.primaryScreen().availableGeometry()
        x = max(scr.left() + 4, min(x, scr.right() - w - 4))
        y = max(scr.top() + 4, y)
        self.move(x, y)
        self.fade = 1.0
        self._elapsed = 0
        self.setWindowOpacity(1.0)
        self.show()
        self.raise_()
        self.timer.start(40)

    def _tick(self):
        self._elapsed += 40
        if self._elapsed < 1500:
            return
        self.fade -= 0.08
        if self.fade <= 0:
            self.timer.stop()
            self.hide()
        else:
            self.setWindowOpacity(max(self.fade, 0.0))

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect().adjusted(2, 2, -2, -10)
        p.setBrush(QColor(255, 253, 250, 242))
        p.setPen(QColor(120, 90, 75, 200))
        p.drawRoundedRect(r, 18, 18)
        cx = self.width() // 2
        p.setBrush(QColor(255, 253, 250, 242))
        p.drawPolygon(QPolygon([QPoint(cx - 8, r.bottom() - 1),
                                QPoint(cx + 8, r.bottom() - 1),
                                QPoint(cx, r.bottom() + 9)]))
        p.setPen(QColor(80, 48, 34))
        p.setFont(QFont("Microsoft YaHei", 10))
        p.drawText(r, Qt.AlignCenter, self.text)


# ---------------------------------------------------------------- 主体
class DeskPet(QWidget):
    def __init__(self):
        super().__init__(None,
                         Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowTitle("白蕾丝小姐")

        self.frames = {}
        self.state = "idle"
        self.display_h = 380
        self.offset_y = 0
        self.offset_x = 0
        self._scaled = None
        self._img = None
        self._flip = False          # 载具向左行驶时为 True，绘制时镜像
        self._angle = 0.0           # 摇晕时的摇摆角度
        self._dizzy_until = 0.0
        self._dizzy_score = 0.0
        self._haki = False          # 哈基米形态进行中
        self._haki_phase = 0.0
        self._haki_home = None

        self._press_global = None
        self._press_win = None
        self._dragging = False
        self._moved = False
        self._idle_seconds = 0
        self._busy = False          # 跳跃动画进行中，不接受新的自动动作

        self._load_frames()
        self._load_config()
        self._apply_size()

        # Q 弹形变（squash & stretch）
        self._sq_active = False
        self._sq_t0 = 0.0
        self._sq_amp = 0.16

        # 放歌跳舞
        self.music = Music()
        self.music_dir = os.path.join(APP_DIR, "music")
        try:
            os.makedirs(self.music_dir, exist_ok=True)
        except Exception:
            pass
        self._haki_dx = 3.5
        self._haki_dy = 3.5
        self._haki_until = 0.0
        self._haki_x = 0.0
        self._haki_y = 0.0

        self.bubble = Bubble()
        self._start_timers()

        self.tray = QSystemTrayIcon(self)
        icon = self.frames.get("idle")
        if icon:
            self.tray.setIcon(QIcon(icon.scaled(
                64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        self.tray.setToolTip("白蕾丝小姐")
        self.tray.setContextMenu(self._build_menu())
        self.tray.show()

    # ------------------------------------------------- 资源
    def _load_frames(self):
        if not os.path.isdir(ASSET_DIR):
            raise SystemExit(f"找不到素材目录: {ASSET_DIR}")
        for f in os.listdir(ASSET_DIR):
            if f.lower().endswith(".png"):
                pm = QPixmap(os.path.join(ASSET_DIR, f))
                if not pm.isNull():
                    self.frames[os.path.splitext(f)[0]] = pm
        if "idle" not in self.frames:
            raise SystemExit("assets 目录里缺少 idle.png")

    def _load_config(self):
        try:
            with open(CONFIG, "r", encoding="utf-8") as fp:
                cfg = json.load(fp)
            self.display_h = int(cfg.get("height", 380))
            self.saved_pos = QPoint(cfg.get("x", -1), cfg.get("y", -1))
        except Exception:
            self.saved_pos = QPoint(-1, -1)

    def _save_config(self):
        try:
            with open(CONFIG, "w", encoding="utf-8") as fp:
                json.dump({"x": self.x(), "y": self.y(), "height": self.display_h},
                          fp, ensure_ascii=False)
        except Exception:
            pass

    # ------------------------------------------------- 尺寸与绘制
    def _target_size(self):
        """按当前动作算出窗口该多大：竖图按身高，横图/方块另算"""
        st = self.state if self.state in self.frames else "idle"
        pm = self.frames[st]
        if st in SQUARE:
            side = int(self.display_h * 1.15)
            return side, side
        h = int(self.display_h * 0.72) if st in WIDE else self.display_h
        return int(h * pm.width() / pm.height()), h

    def _apply_size(self, keep_anchor=True):
        w, h = self._target_size()
        if w == self.width() and h == self.height():
            self._rescale()
            return
        if keep_anchor and self.isVisible():
            # 底边中心不动，这样从站立切到载具时不会整体跳一下
            ax = self.x() + self.width() // 2
            ay = self.y() + self.height()
            self.resize(w, h)
            self.move(ax - w // 2, ay - h)
        else:
            self.resize(w, h)
        self._rescale()

    def _rescale(self):
        pm = self.frames.get(self.state) or self.frames["idle"]
        if self._flip:                       # 载具反向行驶时水平镜像
            pm = pm.transformed(QTransform().scale(-1, 1))
        dpr = self.devicePixelRatioF()
        scaled = pm.scaled(int(self.width() * dpr), int(self.height() * dpr),
                           Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scaled.setDevicePixelRatio(dpr)
        self._scaled = scaled
        self._img = scaled.toImage()
        self.update()

    def paintEvent(self, e):
        if self._scaled is None:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        sy, sx = self._squash()
        if sy != 1.0 or sx != 1.0 or self._angle != 0.0:
            # 哈基米形态绕画面中心变形，其它动作绕脚底
            if self.state == "haki":
                cx, cy = self.width() / 2.0, self.height() / 2.0
            else:
                cx, cy = self.width() / 2.0, float(self.height())
            p.translate(cx, cy)
            p.scale(sx, sy)
            if self._angle:
                p.rotate(self._angle)
            p.translate(-cx, -cy)

        dpr = self._scaled.devicePixelRatio()
        x = (self.width() - self._scaled.width() / dpr) / 2
        p.drawPixmap(int(x + self.offset_x), int(self.offset_y), self._scaled)

    def _squash(self):
        """阻尼振荡算当前缩放；哈基米形态用持续正弦，一直软软地弹"""
        if self.state == "haki" and self._haki:
            sy = 1.0 + 0.16 * math.cos(self._haki_phase * 1.25)
            return sy, 1.0 / math.sqrt(max(sy, 0.55))
        if not self._sq_active:
            return 1.0, 1.0
        t = time.time() - self._sq_t0
        if t > 0.95:
            self._sq_active = False
            return 1.0, 1.0
        sy = 1.0 - self._sq_amp * math.exp(-t * 5.2) * math.cos(t * 2 * math.pi * 3.1)
        sy = max(0.72, min(1.22, sy))
        sx = 1.0 / math.sqrt(sy)
        return sy, sx

    def bounce(self, power=1.0):
        """触发一次 Q 弹"""
        self._sq_amp = 0.17 * power
        self._sq_t0 = time.time()
        self._sq_active = True
        if not self._sq_timer.isActive():
            self._sq_timer.start(16)

    def hit_test(self, pos):
        if self._scaled is None or self._img is None:
            return False
        dpr = self._scaled.devicePixelRatio()
        x = (pos.x() - self.offset_x) * dpr
        y = (pos.y() - self.offset_y) * dpr
        if x < 0 or y < 0 or x >= self._img.width() or y >= self._img.height():
            return False
        return self._img.pixelColor(int(x), int(y)).alpha() > 30

    # ------------------------------------------------- 状态切换
    def set_state(self, name, back_to="idle", hold_ms=None):
        if name not in self.frames:
            return
        self.state = name
        self._apply_size()
        # 这几个状态由自己的逻辑控制何时结束，不挂自动回退定时器
        sticky = ("sleep", "subway", "plane")
        if hold_ms is None and name not in sticky:
            hold_ms = 2600
        if hold_ms and name not in sticky:
            old = getattr(self, "_hold_timer", None)
            if old is not None:
                old.stop()
            self._hold_timer = QTimer(self)
            self._hold_timer.setSingleShot(True)
            self._hold_timer.timeout.connect(lambda: self._back(back_to))
            self._hold_timer.start(hold_ms)

    def _back(self, name="idle"):
        self.state = name if name in self.frames else "idle"
        self._apply_size()

    def say(self, text=None):
        if not text:
            text = random.choice(LINES.get(self.state, LINES["idle"]))
        head = self.mapToGlobal(QPoint(self.width() // 2, int(self.height() * 0.10)))
        self.bubble.show_text(text, head)

    # ------------------------------------------------- 定时器
    def _start_timers(self):
        self._t = 0.0
        self.breath = QTimer(self)
        self.breath.timeout.connect(self._breathe)
        self.breath.start(40)

        self.blink = QTimer(self)
        self.blink.timeout.connect(self._do_blink)
        self._schedule_blink()

        self.rand_act = QTimer(self)
        self.rand_act.timeout.connect(self._random_action)
        self._schedule_random()

        self.doze = QTimer(self)
        self.doze.timeout.connect(self._check_doze)
        self.doze.start(5000)

        # 每 45 分钟提醒一次喝水/活动（实用项，可在菜单里关掉）
        self._remind_on = True
        self.remind = QTimer(self)
        self.remind.timeout.connect(self._remind)
        self.remind.start(45 * 60 * 1000)

        # 跳跃位移动画
        self._jump_timer = QTimer(self)
        self._jump_timer.timeout.connect(self._jump_step)

        # 地铁 / 飞机横穿屏幕
        self._travel_timer = QTimer(self)
        self._travel_timer.timeout.connect(self._travel_step)
        self._travel = None
        self._travel_home = None

        # Q 弹形变的帧刷新
        self._sq_timer = QTimer(self)
        self._sq_timer.timeout.connect(self._sq_tick)

        # 哈基米形态（坐姿 + 一直 Q 弹 + 满屏四周弹）
        self._haki_timer = QTimer(self)
        self._haki_timer.timeout.connect(self._haki_step)

        # 被摇晕时的左右摇摆
        self._dizzy_timer = QTimer(self)
        self._dizzy_timer.timeout.connect(self._dizzy_tick)

    def _sq_tick(self):
        if self._sq_active:
            self.update()
        else:
            self._sq_timer.stop()

    def _dizzy_tick(self):
        """被摇晕后左右摇晃一会儿"""
        now = time.time()
        if now >= self._dizzy_until:
            self._dizzy_timer.stop()
            self._angle = 0.0
            if self.state == "dizzy":
                self.state = "idle"
                self._rescale()
            self.update()
            return
        self._angle = math.sin(now * 9.5) * 9.0
        self.update()

    def _breathe(self):
        self._t += 0.06
        self.offset_y = math.sin(self._t) * 3.0
        self.offset_x = math.sin(self._t * 0.6) * 1.2
        self.update()

    def _schedule_blink(self):
        self.blink.start(random.randint(2600, 6500))

    def _do_blink(self):
        self.blink.stop()
        if self.state == "idle" and "blink" in self.frames:
            self.state = "blink"
            self._rescale()
            QTimer.singleShot(130, self._end_blink)
        self._schedule_blink()

    def _end_blink(self):
        if self.state == "blink":
            self.state = "idle"
            self._rescale()

    def _schedule_random(self):
        self.rand_act.start(random.randint(14000, 32000))

    def _random_action(self):
        self._schedule_random()
        if self._busy or self._dragging:
            return
        if self.state not in ("idle", "blink") or self._idle_seconds >= 60:
            return
        act = random.choice(IDLE_ACTIONS)
        if act == "jump":
            self.do_jump(say_it=False)
        else:
            self.set_state(act, "idle", random.randint(2200, 3400))

    def _check_doze(self):
        if self._dragging or self._busy:
            return
        self._idle_seconds += 5
        if self._idle_seconds >= 90 and self.state in ("idle", "blink"):
            self.set_state("sleep", "idle", None)
            self.say(random.choice(LINES["sleep"]))

    def _remind(self):
        if not self._remind_on or self._dragging:
            return
        self.say(random.choice(["起来走走？坐好久了", "喝口水吧，别忘记",
                                "眼睛也累了，看看远处", "该活动一下啦"]))

    # ------------------------------------------------- 跳跃（带位移）
    def do_jump(self, say_it=True):
        """横向跳一段，y 走抛物线，落地回 idle"""
        if self._dragging:
            return
        self._cancel_current()
        scr = self.screen().availableGeometry()
        cur = self.pos()
        dist = random.randint(80, 170) * random.choice([-1, 1])
        tx = cur.x() + dist
        # 撞边就反向
        if tx < scr.left() or tx + self.width() > scr.right():
            tx = cur.x() - dist
        tx = max(scr.left(), min(tx, scr.right() - self.width()))

        # 位移太小就放弃（贴边时）
        if abs(tx - cur.x()) < 30:
            self.set_state("jump", "idle", 900)
            if say_it:
                self.say(random.choice(LINES["jump"]))
            return

        self._busy = True
        self.set_state("jump")
        self._jx0, self._jy0, self._jx1 = cur.x(), cur.y(), tx
        self._jt = 0.0
        self._jump_timer.start(16)
        if say_it:
            self.say(random.choice(LINES["jump"]))

    def _jump_step(self):
        self._jt += 16.0 / 520.0          # 全程 520ms
        if self._jt >= 1.0:
            self._jump_timer.stop()
            self.move(self._jx1, self._jy0)
            self._busy = False
            self.state = "idle"
            self._rescale()
            self.bounce(1.25)            # 落地压一下
            self._save_config()
            return
        t = self._jt
        x = self._jx0 + (self._jx1 - self._jx0) * t
        y = self._jy0 - math.sin(math.pi * t) * 46   # 最高抬 46 像素
        self.move(int(x), int(y))

    # ------------------------------------------------- 放歌乱跑
    def _tracks(self):
        out = []
        if os.path.isdir(self.music_dir):
            for f in os.listdir(self.music_dir):
                if f.lower().endswith((".mp3", ".wav", ".wma", ".m4a")):
                    out.append(os.path.join(self.music_dir, f))
        return out

    def _cancel_current(self):
        """把正在进行中的动作/模式全部取消，保证任何时刻只有一个动作在跑"""
        for name in ("_hold_timer", "_travel_timer", "_jump_timer",
                     "_haki_timer", "_sq_timer", "_dizzy_timer"):
            t = getattr(self, name, None)
            if t is not None and t.isActive():
                t.stop()
        self._busy = False
        self._travel = None
        self._haki = False
        self._sq_active = False
        self._angle = 0.0
        self._dizzy_until = 0.0
        try:
            self.music.close()
        except Exception:
            pass
        self.state = "idle"
        self._apply_size(keep_anchor=False)

    # ------------------------------------------------- 哈基米形态
    def start_haki(self):
        """哈基米形态：用坐下那张图，一直 Q 弹，在桌面上四周乱弹，同时放歌"""
        if self._haki:
            self.stop_haki()
            return
        self._cancel_current()
        if "haki" not in self.frames:
            return

        self._haki = True
        self._haki_home = self.pos()
        self.state = "haki"
        self._apply_size(keep_anchor=False)

        scr = self.screen().availableGeometry()
        self._haki_x = scr.left() + max(0, (scr.width() - self.width()) // 2)
        self._haki_y = scr.top() + max(0, (scr.height() - self.height()) // 2)
        self.move(int(self._haki_x), int(self._haki_y))
        self._haki_dx = random.choice([-1, 1]) * 4.2
        self._haki_dy = random.choice([-1, 1]) * 3.4
        self._haki_phase = 0.0
        self._haki_until = time.time() + 30
        self._haki_timer.start(16)

        tracks = self._tracks()
        played = bool(tracks) and self.music.play(random.choice(tracks), repeat=True)
        self.say("哈基米～哈基米～" if played else "哈基米形态！")

    def stop_haki(self, go_home=True):
        if not self._haki:
            return
        self._haki = False
        self._haki_timer.stop()
        try:
            self.music.close()
        except Exception:
            pass
        self.state = "idle"
        self._apply_size(keep_anchor=False)
        if go_home and self._haki_home is not None:
            self.move(self._haki_home)
        self._snap_to_edge()
        self._save_config()

    def _haki_step(self):
        now = time.time()
        if now > self._haki_until:
            self.stop_haki()
            return

        self._haki_phase += 0.16
        scr = self.screen().availableGeometry()
        self._haki_x += self._haki_dx
        self._haki_y += self._haki_dy

        hop_max = 0
        x0, x1 = scr.left(), scr.right() - self.width()
        y0, y1 = scr.top() + hop_max, scr.bottom() - self.height()
        if self._haki_x <= x0:
            self._haki_x, self._haki_dx = x0, abs(self._haki_dx)
        elif self._haki_x >= x1:
            self._haki_x, self._haki_dx = x1, -abs(self._haki_dx)
        if self._haki_y <= y0:
            self._haki_y, self._haki_dy = y0, abs(self._haki_dy)
        elif self._haki_y >= y1:
            self._haki_y, self._haki_dy = y1, -abs(self._haki_dy)

        self.move(int(self._haki_x), int(self._haki_y - hop_max))
        self.update()

    # ------------------------------------------------- 载具出行（碰壁反弹）
    def do_travel(self, kind):
        """地铁/飞机在屏幕里来回弹。同一种载具再点一次 = 停车。

        地铁贴任务栏、只左右弹；飞机四个边都弹，像弹球。
        """
        if self._travel_timer.isActive():
            self._stop_travel()          # 再点一次就收车
            return
        if self._dragging or kind not in self.frames:
            return
        self._cancel_current()

        self._busy = True
        self._travel_home = self.pos()
        self._flip = False
        self.set_state(kind)

        scr = self.screen().availableGeometry()
        w, h = self.width(), self.height()
        # 地铁和飞机都在整个桌面里四边弹，不再限制在一条水平线上
        self._move_range = (scr.left(), scr.right() - w,
                            scr.top(), scr.bottom() - h)
        if kind == "subway":
            y = scr.bottom() - h                 # 从底部出发
            dx, dy = 3.8, 2.4
        else:
            y = scr.top() + int(scr.height() * 0.30)
            dx, dy = 4.6, 3.0
        self.move(scr.left() + 40, y)
        self._travel = {"dx": dx, "dy": dy, "kind": kind, "t": 0,
                        "out": time.time() + 25}      # 最多跑 25 秒
        self._travel_timer.start(16)
        self.say(random.choice(LINES[kind]))

    def _travel_step(self):
        d = self._travel
        if d is None:
            self._travel_timer.stop()
            return
        d["t"] += 1
        if time.time() > d["out"]:             # 到时间自己收车，不会一直挡着屏幕
            self._stop_travel()
            return

        x0, x1, y0, y1 = self._move_range
        x = self.x() + d["dx"]
        y = self.y() + d["dy"]

        # 四周碰壁反弹（地铁/飞机都用同一套）
        if x <= x0:
            x, d["dx"] = x0, abs(d["dx"])
        elif x >= x1:
            x, d["dx"] = x1, -abs(d["dx"])
        if y <= y0:
            y, d["dy"] = y0, abs(d["dy"])
        elif y >= y1:
            y, d["dy"] = y1, -abs(d["dy"])

        # 往左开就把图水平翻过来
        want_flip = d["dx"] < 0
        if want_flip != self._flip:
            self._flip = want_flip
            self._rescale()

        self.move(int(x), int(y))

    def _stop_travel(self):
        """收车：回到出发前的位置和大小"""
        if self._travel_timer.isActive():
            self._travel_timer.stop()
        if self._travel is None:
            return
        self._busy = False
        home = self._travel_home
        self._travel = None
        self._flip = False
        self.state = "idle"
        self._apply_size(keep_anchor=False)
        if home is not None:
            self.move(home)
        self._snap_to_edge()
        self._save_config()
        self.say("到站啦～")

    # ------------------------------------------------- 鼠标交互
    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        self._idle_seconds = 0
        self._press_global = e.globalPosition().toPoint()
        self._press_win = self.pos()
        self._last_gp = self._press_global
        self._last_t = time.time()
        self._dizzy_score = 0.0
        self._dragging = False
        self._moved = False
        e.accept()

    def mouseMoveEvent(self, e):
        if self._press_global is None:
            return
        gp = e.globalPosition().toPoint()
        now = time.time()
        prev = getattr(self, "_last_gp", gp)
        dt = max(now - getattr(self, "_last_t", now), 0.008)
        inst_speed = (gp - prev).manhattanLength() / dt     # 瞬时速度 px/秒
        self._last_gp, self._last_t = gp, now

        delta = gp - self._press_global
        if not self._moved and delta.manhattanLength() > 4:
            self._moved = True
            self._dragging = True
            self.state = "grab" if "grab" in self.frames else "idle"
            self._rescale()
        if self._moved:
            self.move(self._press_win + delta)
            # 甩得太快就会晕
            if inst_speed > 1600:
                self._dizzy_score += 1.0
            else:
                self._dizzy_score = max(0.0, self._dizzy_score - 0.4)
            if self._dizzy_score >= 4 and "dizzy" in self.frames and self.state != "dizzy":
                self.state = "dizzy"
                self._rescale()
                self.say("唔…晕了晕了")

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        if self._press_global is None:
            return                        # 按下时被忽略了，抬起也不做事
        if self._dragging:
            self._dragging = False
            if self._dizzy_score >= 4 and "dizzy" in self.frames:
                self.state = "dizzy"
                self._rescale()
                self._dizzy_until = time.time() + 1.8
                self._dizzy_timer.start(16)
            else:
                self.state = "idle"
                self._rescale()
            self._snap_to_edge()
            self.bounce(1.15)            # 放下时落地弹一下
            self._save_config()
            self._dizzy_score = 0.0
        elif not self._moved:
            was_sleep = self.state in ("sleep", "nap")
            self._cancel_current()       # 点一下就取消当前动作，不叠加
            if was_sleep:
                self.set_state("stretch", "idle", 1200)
                self.say("唔…醒了醒了")
            else:
                act = random.choice(CLICK_ACTIONS)
                self.bounce(1.0)             # 戳一下就 Q 弹
                if act == "jump":
                    self.do_jump()
                else:
                    self.set_state(act, "idle", 1800)
                    if act == "wave":
                        self.say(greet_text())
                    else:
                        self.say(random.choice(LINES.get(act, LINES["idle"])))
        self._press_global = None
        self._idle_seconds = 0

    def mouseDoubleClickEvent(self, e):
        self.do_jump()

    def wheelEvent(self, e):
        if self._busy:
            return                       # 开载具时改尺寸会乱，忽略
        step = 24 if e.angleDelta().y() > 0 else -24
        self.display_h = max(180, min(760, self.display_h + step))
        self._apply_size()
        self._save_config()

    def _snap_to_edge(self):
        scr = self.screen().availableGeometry()
        x, y = self.x(), self.y()
        if x < scr.left() + 30:
            x = scr.left()
        if x + self.width() > scr.right() - 30:
            x = scr.right() - self.width()
        if y + self.height() > scr.bottom() + 20:
            y = scr.bottom() - self.height() + 20
        if y < scr.top():
            y = scr.top()
        self.move(x, y)

    def contextMenuEvent(self, e):
        if not self.hit_test(e.pos()):
            e.ignore()
            return
        was_running = self._travel_timer.isActive()
        if was_running:
            self._travel_timer.stop()     # 开菜单时先暂停，不然窗口会跑掉
        was_haki = self._haki and self._haki_timer.isActive()
        if was_haki:
            self._haki_timer.stop()
        self._build_menu().exec(e.globalPos())
        if was_running and self._travel is not None:
            self._travel_timer.start(16)
        if was_haki and self._haki:
            self._haki_timer.start(16)

    # ------------------------------------------------- 菜单
    def _build_menu(self):
        m = QMenu()
        m.setStyleSheet("""
            QMenu { background:#FFFDFA; border:1px solid #E3D5C8; border-radius:8px;
                    padding:6px; font-family:'Microsoft YaHei'; font-size:13px; color:#4A342A;}
            QMenu::item { padding:6px 26px 6px 18px; border-radius:5px; }
            QMenu::item:selected { background:#F3E4D8; }
            QMenu::separator { height:1px; background:#EFE2D6; margin:4px 8px; }
        """)
        items = [("打招呼", "wave"), ("玩手机", "phone"), ("吃棒棒糖", "lollipop"),
                 ("喝奶茶", "drink"), ("看书", "book"), ("伸懒腰", "stretch"),
                 ("跳绳", "rope"), ("举哑铃", "dumbbell"),
                 ("害羞", "shy"), ("生气", "angry"), ("跳一下", "jump"),
                 ("坐下", "sit"), ("打盹", "nap"), ("睡觉", "sleep")]
        for label, act in items:
            a = QAction(label, m)
            a.triggered.connect(lambda _=False, n=act: self._menu_action(n))
            m.addAction(a)

        m.addSeparator()
        running = self._travel["kind"] if self._travel else None
        a = QAction("停车（地铁）" if running == "subway" else "开地铁兜一圈", m)
        a.triggered.connect(lambda: self.do_travel("subway"))
        m.addAction(a)
        a = QAction("降落（飞机）" if running == "plane" else "开飞机兜一圈", m)
        a.triggered.connect(lambda: self.do_travel("plane"))
        m.addAction(a)

        a = QAction("退出哈基米形态" if self._haki else "哈基米形态（放歌乱弹）", m)
        a.triggered.connect(self.start_haki)
        m.addAction(a)
        a = QAction("打开 music 文件夹", m)
        a.triggered.connect(self._open_music_dir)
        m.addAction(a)

        m.addSeparator()

        size_menu = m.addMenu("大小")
        for label, h in [("小", 260), ("中", 380), ("大", 520)]:
            a = QAction(label, size_menu)
            a.triggered.connect(lambda _=False, v=h: self._set_height(v))
            size_menu.addAction(a)

        top = QAction("总在最前面", m)
        top.setCheckable(True)
        top.setChecked(bool(self.windowFlags() & Qt.WindowStaysOnTopHint))
        top.triggered.connect(self._toggle_top)
        m.addAction(top)

        rm = QAction("定时提醒喝水", m)
        rm.setCheckable(True)
        rm.setChecked(self._remind_on)
        rm.triggered.connect(self._toggle_remind)
        m.addAction(rm)

        a = QAction("回到右下角", m)
        a.triggered.connect(self._to_corner)
        m.addAction(a)

        a = QAction("藏到托盘", m)
        a.triggered.connect(self.hide)
        m.addAction(a)

        m.addSeparator()
        a = QAction("退出", m)
        a.triggered.connect(self._quit)
        m.addAction(a)
        return m

    def _menu_action(self, name):
        self._idle_seconds = 0
        self._cancel_current()          # 换动作前先把当前动作取消，不叠加
        if name == "jump":
            self.do_jump()
            return
        if name == "wave":
            self.set_state("wave", "idle", 2400)
            self.say(greet_text())
            return
        sleep_like = name == "sleep"
        self.set_state(name, "idle", None if sleep_like else 3000)
        self.say(random.choice(LINES.get(name, LINES["idle"])))

    def _toggle_remind(self, checked):
        self._remind_on = checked

    def _set_height(self, h):
        self.display_h = h
        self._apply_size()
        self._save_config()

    def _toggle_top(self, checked):
        self.setWindowFlag(Qt.WindowStaysOnTopHint, checked)
        self.show()

    def _to_corner(self):
        scr = self.screen().availableGeometry()
        self.move(scr.right() - self.width() - 40,
                  scr.bottom() - self.height() + 20)
        self._save_config()

    def _open_music_dir(self):
        try:
            os.makedirs(self.music_dir, exist_ok=True)
            os.startfile(self.music_dir)      # 打开资源管理器
        except Exception:
            pass

    def _quit(self):
        self._save_config()
        self.music.close()
        self.tray.hide()
        QApplication.quit()

    def closeEvent(self, e):
        e.ignore()
        self.hide()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("白蕾丝小姐")

    pet = DeskPet()
    if pet.saved_pos and pet.saved_pos.x() > -1:
        pet.move(pet.saved_pos)
    else:
        scr = pet.screen().availableGeometry()
        pet.move(scr.right() - pet.width() - 40,
                 scr.bottom() - pet.height() + 20)
    pet.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
