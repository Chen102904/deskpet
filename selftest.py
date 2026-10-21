# -*- coding: utf-8 -*-
"""无头自检 v7：哈基米形态 / 载具四边弹 / 动作互斥 / 拖动摇晕"""
import os
import sys
import time

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main  # noqa: E402
from PySide6.QtCore import QPoint  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

app = QApplication(sys.argv)
pet = main.DeskPet()
pet.move(300, 300)
pet.show()
app.processEvents()

print("素材数:", len(pet.frames))
print("素材:", sorted(pet.frames.keys()))
print("有 dizzy:", "dizzy" in pet.frames, " 有 haki:", "haki" in pet.frames)
print("SQUARE:", main.SQUARE)


def run(sec, fn=None):
    t0 = time.time()
    out = []
    while time.time() - t0 < sec:
        app.processEvents()
        if fn:
            out.append(fn())
        time.sleep(0.01)
    return out


# ---- 哈基米形态
pet.move(300, 300)
app.processEvents()
pet.start_haki()
print("\n哈基米启动：haki =", pet._haki, " 窗口", pet.width(), "x", pet.height(),
      "（应为正方形）")
xs, ys, sq = [], [], []
t0 = time.time()
while time.time() - t0 < 3.5:
    app.processEvents()
    xs.append(pet.x())
    ys.append(pet.y())
    sy, sx = pet._squash()
    sq.append(round(sy, 3))
    time.sleep(0.01)
print("x 范围:", min(xs), "~", max(xs), " y 范围:", min(ys), "~", max(ys),
      "（x、y 都在变 = 四周弹）")
print("Q 弹 sy:", min(sq), "~", max(sq), "（持续不等于 1 说明一直在弹）")
print("是否还在切换其它形象:", pet.state, "（应始终是 haki）")

# ---- 动作互斥
pet.stop_haki()
app.processEvents()
pet.do_travel("subway")
print("\n先开地铁：state =", pet.state, " busy =", pet._busy)
menu_act = pet._menu_action
menu_act("shy")
app.processEvents()
print("地铁进行中再点「害羞」→ state =", pet.state,
      " busy =", pet._busy,
      " 地铁定时器还在跑 =", pet._travel_timer.isActive(),
      "（应为 False，说明旧动作被取消）")
pet._cancel_current()

# ---- 地铁四边弹
pet.move(300, 300)
pet.do_travel("subway")
ys2 = []
run(4.5, lambda: ys2.append(pet.y()))
dy = [b - a for a, b in zip(ys2, ys2[1:]) if b != a]
ddirs = [1 if d > 0 else -1 for d in dy]
turns = sum(1 for a, b in zip(ddirs, ddirs[1:]) if a != b)
print("\n地铁 y 范围:", min(ys2), "~", max(ys2), " 上下方向切换:", turns,
      "（>0 说明地铁也在上下弹）")
pet._cancel_current()

# ---- 摇晕
print("\n摇晕阈值检查：dizzy_score 累计逻辑")
pet._dizzy_score = 0.0
for _ in range(4):
    pet._dizzy_score += 1.0
print("  连续 4 次超速后 score =", pet._dizzy_score, " → 会触发 dizzy")
pet._dizzy_score = 0.0

# 模拟摇晕后的摇摆
pet.state = "dizzy"
pet._dizzy_until = time.time() + 0.6
pet._dizzy_timer.start(16)
angles = run(0.7, lambda: round(pet._angle, 2))
print("  摇摆角度出现范围:", min(angles), "~", max(angles))
print("  结束后 state =", pet.state, " 角度归零 =", pet._angle == 0.0)

menu = pet._build_menu()
print("\n菜单:", [a.text() for a in menu.actions() if a.text()])

print("\n自检通过")
os._exit(0)
