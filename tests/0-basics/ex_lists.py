import spira.all as spira


# TypedList
# ---------


print('\nElementalList')
print('-------------')
el = spira.ElementList()
el += spira.Polygon(alias='P1')
el.append(spira.Polygon(alias='P2'))
el.extend([spira.Polygon(alias='P2'), spira.Polygon(alias='P3')])
el = el + spira.Polygon(alias='P2')
# el = [spira.Polygon(alias='P1'), spira.Polygon(alias='P2')]
# el = set([spira.Polygon(alias='P1'), spira.Polygon(alias='P2')])
print(el)


print('\nPortList')
print('--------')
pl = spira.PortList()
pl += spira.Terminal(midpoint=(0,0))
pl.append(spira.Terminal(midpoint=(10,0)))
pl.extend([spira.Terminal(midpoint=(20,0)), spira.Terminal(midpoint=(30,0))])
pl = pl + spira.Terminal(midpoint=(40,0))
print(pl)
print('')
for e in pl:
    print(e)


# CellList
# --------


# Netlist
# -------