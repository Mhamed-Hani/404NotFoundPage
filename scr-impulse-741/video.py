import math, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import arabic_reshaper
from bidi.algorithm import get_display

def ar(s): return get_display(arabic_reshaper.reshape(s))

# ---- simulation (same model as simulate.py, plus D2 clamp) ----
VSAT, SLEW = 10.5, 0.5e6
R, C, beta = 91e3, 0.1e-6, 0.5
CD, RD, RG, VD, VGK = 0.1e-6, 1e3, 220.0, 0.7, 0.7
dt, t_end = 0.2e-6, 100e-3
n = int(t_end / dt)
vo, vc, vcd = VSAT, 0.0, 0.0
T = np.empty(n); VO = np.empty(n); VC = np.empty(n); VX = np.empty(n); IG = np.empty(n)
for k in range(n):
    target = VSAT if beta * vo > vc else -VSAT
    vo += max(-SLEW*dt, min(SLEW*dt, target - vo))
    vc += (vo - vc) / (R*C) * dt
    vx = vo - vcd
    if vx < -VD:                       # D2 conducts: clamp node X
        vcd = vo + VD; vx = -VD
    ig = max(0.0, (vx - VD - VGK) / RG)
    vcd += (vx/RD + ig) / CD * dt
    T[k], VO[k], VC[k], VX[k], IG[k] = k*dt*1e3, vo, vc, vx, ig*1e3
VG = np.where(IG > 0, VGK + IG*0, np.clip(VX - VD, 0, VGK))  # gate voltage
# decimate for the full view, keep fine data for zoom
s = 10
Td, VOd, VCd, VXd, IGd = T[::s], VO[::s], VC[::s], VX[::s], IG[::s]

# ---- figure ----
plt.rcParams["font.family"] = "DejaVu Sans"
fig = plt.figure(figsize=(16, 9), dpi=120, facecolor="#10141c")
fig.text(0.49, 0.963, "Mohamed Hani Mohamed Khafagy   |", ha="right", va="center",
         color="white", fontsize=22, weight="bold")
fig.text(0.50, 0.963, ar("محمد هاني محمد خفاجي"), ha="left", va="center",
         color="white", fontsize=26, weight="bold", family="FreeSerif")
fig.text(0.5, 0.925, "Power Electronics Task: SCR firing impulse generator using op-amp 741 "
         "(astable multivibrator + RC differentiator)", ha="center", color="#9fb3c8", fontsize=14)
fig.text(0.995, 0.005, "Waveforms: numerical circuit simulation (Python), not Proteus",
         ha="right", va="bottom", color="#56657a", fontsize=9)

axs = fig.add_axes([0.01, 0.50, 0.98, 0.40]); axs.axis("off")
axs.imshow(plt.imread("schematic.png"))

colors = ["#ffd400", "#00e5ff", "#ff4fd8", "#3dff6e"]
labels = ["A: 741 output (V)", "B: timing cap C (V)", "C: node X differentiator (V)", "D: gate current (mA)"]
data = [VOd, VCd, VXd, IGd]
ylims = [(-13, 13), (-7, 7), (-13, 13), (-5, 45)]
axes, lines = [], []
for i in range(4):
    a = fig.add_axes([0.06, 0.38 - i*0.11, 0.62, 0.10], facecolor="black")
    a.set_xlim(0, 100); a.set_ylim(*ylims[i])
    a.grid(color="#1f3a1f", lw=0.8)
    a.tick_params(colors="#9fb3c8", labelsize=8)
    if i < 3: a.set_xticklabels([])
    a.text(0.005, 0.92, labels[i], transform=a.transAxes, color=colors[i], fontsize=10, va="top")
    for sp in a.spines.values(): sp.set_color("#2c3e50")
    ln, = a.plot([], [], color=colors[i], lw=1.4); axes.append(a); lines.append(ln)
axes[-1].set_xlabel("time (ms)", color="#9fb3c8")

# zoom panel on one firing pulse
az = fig.add_axes([0.73, 0.06, 0.25, 0.39], facecolor="black")
az.tick_params(colors="#9fb3c8", labelsize=8); az.grid(color="#1f3a1f")
for sp in az.spines.values(): sp.set_color("#2c3e50")
edge = np.argmax((T > 30) & (np.diff(np.r_[VO[0], VO]) > 0))
t0 = T[edge]; win = (T > t0 - 0.1) & (T < t0 + 0.6)
az.set_xlim(-100, 600); az.set_ylim(-2, 45)
az.set_title("Zoom: one firing impulse", color="white", fontsize=11)
az.set_xlabel("time from edge (µs)", color="#9fb3c8")
zl1, = az.plot([], [], color=colors[3], lw=2, label="gate current (mA)")
zl2, = az.plot([], [], color=colors[2], lw=1.2, label="node X (V)")
az.legend(loc="upper right", fontsize=8, facecolor="black", labelcolor="white")
info = az.text(0.97, 0.55, "", transform=az.transAxes, color="white", fontsize=10, ha="right")
status = fig.text(0.06, 0.475, "", color="#3dff6e", fontsize=12, weight="bold")

FPS, SWEEP, HOLD = 25, 14 * 25, 6 * 25
def frame(f):
    k = min(len(Td), int(len(Td) * (f + 1) / SWEEP))
    for ln, y in zip(lines, data): ln.set_data(Td[:k], y[:k])
    tnow = Td[k-1]
    pulses = int(np.sum(np.diff((IGd[:k] > 5).astype(int)) == 1))
    status.set_text(f"RUNNING  t = {tnow:6.1f} ms   |  firing pulses: {pulses}")
    if f >= SWEEP:
        p = min(1.0, (f - SWEEP) / (HOLD * 0.6))
        tz = (T[win] - t0) * 1e3; m = max(2, int(len(tz) * p))
        zl1.set_data(tz[:m], IG[win][:m]); zl2.set_data(tz[:m], VX[win][:m])
        info.set_text(f"f = 50 Hz (T = 20 ms)\nIg peak = {IG[win].max():.0f} mA\n"
                      f"pulse width ≈ {np.sum(IG[win] > 5) * dt * 1e6:.0f} µs (Ig > 5 mA)")
    return lines

anim = FuncAnimation(fig, frame, frames=SWEEP + HOLD, blit=False)
anim.save("scr_impulse_741.mp4", writer=FFMpegWriter(fps=FPS, bitrate=4000, codec="libx264",
          extra_args=["-pix_fmt", "yuv420p"]), dpi=120)
fig.savefig("last_frame.png", dpi=80)
print("done")
