"""Quick numerical check of the 741 impulse generator (astable + RC differentiator + diode).

741 modelled as a comparator with +/-10.5 V saturation (on +/-12 V rails) and 0.5 V/us slew rate.
"""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

VSAT, SLEW = 10.5, 0.5e6           # V, V/s
R1 = R2 = 10e3                     # feedback divider -> beta = 0.5
R, C = 91e3, 0.1e-6                # timing network
CD, RD = 0.1e-6, 1e3               # differentiator
RG, VD, VGK = 220.0, 0.7, 0.7      # gate resistor, diode drop, SCR gate-cathode drop

beta = R2 / (R1 + R2)
T = 2 * R * C * math.log((1 + beta) / (1 - beta))
print(f"theoretical period T = {T*1e3:.2f} ms  ->  f = {1/T:.1f} Hz")

dt, t_end = 0.2e-6, 60e-3
vo, vc, vcd = VSAT, 0.0, 0.0       # op-amp out, timing cap, differentiator cap
ts, vos, vcs, vxs, vgs = [], [], [], [], []
t = 0.0
while t < t_end:
    target = VSAT if beta * vo > vc else -VSAT
    vo += max(-SLEW * dt, min(SLEW * dt, target - vo))
    vc += (vo - vc) / (R * C) * dt
    # node X: vx = vo - vcd ; currents through RD and (when forward biased) diode + RG
    vx = vo - vcd
    ig = max(0.0, (vx - VD - VGK) / RG)
    vcd += (vx / RD + ig) / CD * dt
    if int(t / dt) % 25 == 0:
        ts.append(t * 1e3); vos.append(vo); vcs.append(vc); vxs.append(vx); vgs.append(ig * 1e3)
    t += dt

pk = max(vgs)
print(f"peak gate current = {pk:.1f} mA, peak differentiator voltage = {max(vxs):.1f} V")

fig, ax = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
ax[0].plot(ts, vos, label="741 output (square)"); ax[0].plot(ts, vcs, label="V(C) timing cap")
ax[0].set_ylabel("V"); ax[0].legend(loc="upper right")
ax[1].plot(ts, vxs, color="tab:green"); ax[1].set_ylabel("V differentiator")
ax[2].plot(ts, vgs, color="tab:red"); ax[2].set_ylabel("Gate current (mA)")
ax[2].set_xlabel("time (ms)")
fig.suptitle("SCR firing impulse generator - 741 astable + RC differentiator")
fig.tight_layout()
fig.savefig(__file__.replace("simulate.py", "waveforms.png"), dpi=110)
