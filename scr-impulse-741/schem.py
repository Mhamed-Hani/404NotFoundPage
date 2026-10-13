import schemdraw, schemdraw.elements as elm
schemdraw.use('matplotlib')
with schemdraw.Drawing(file='schematic.png', show=False, dpi=140) as d:
    d.config(fontsize=11, unit=2.5)
    op = elm.Opamp(leads=True); d += op
    d += elm.Label().at((op.center.x, op.center.y)).label('741')
    d += elm.Line().at(op.out).right(0.8); o = d.here; d += elm.Dot()
    # inverting input: R to out (above), C to ground
    d += elm.Line().at(op.in1).left(0.75); m = d.here; d += elm.Dot()
    d += elm.Line().up(2.0)
    d += elm.Resistor().tox(o.x).label('R 91k')
    d += elm.Line().toy(o)
    d += elm.Line().at(m).left(3.0)
    d += elm.Capacitor().down(3.0).label('C 0.1µF', loc='bottom'); d += elm.Ground()
    # non-inverting input: R1 to out (below), R2 to ground
    d += elm.Line().at(op.in2).left(0.75); p = d.here; d += elm.Dot()
    d += elm.Line().down(2.0)
    d += elm.Resistor().tox(o.x).label('R1 10k', loc='bottom')
    d += elm.Line().toy(o)
    d += elm.Line().at(p).left(1.5)
    d += elm.Resistor().down(2.5).label('R2 10k', loc='bottom'); d += elm.Ground()
    # differentiator + gate drive
    d += elm.Line().at(o).right(0.5)
    d += elm.Capacitor().right().label('Cd 0.1µF'); x = d.here
    d += elm.Dot().label('X', loc='top')
    d += elm.Resistor().at(x).down(2.0).label('Rd 1k', loc='bottom'); d += elm.Ground()
    d += elm.Line().at(x).right(2.0); x2 = d.here; d += elm.Dot()
    d += elm.Diode().at(x2).down(2.0).reverse().label('D2', loc='bottom'); d += elm.Ground()
    d += elm.Diode().at(x2).right().label('D1 1N4148')
    d += elm.Resistor().right().label('RG 220Ω')
    d += elm.Dot().label('Gate', loc='bottom')
    d += elm.Line().right(0.5)
    s = elm.SCR().down().anchor('gate').label('SCR', loc='bottom', ofst=0.6); d += s
    d += elm.Ground().at(s.end)
    d += elm.Line().at(s.start).up(0.5)
    d += elm.Lamp().up(2).label('Lamp', loc='bottom')
    d += elm.Vdd().label('+12V')
    d += elm.Label().at((op.center.x + 0.3, op.center.y + 1.2)).label('pin7 +12V / pin4 -12V', fontsize=9)
