import spira.all as spira
from spira.yevon.vmodel.virtual import *
from tests._03_structures.jtl_bias import JtlBias
from tests._03_structures.jtl_bias_ports import JtlBiasPorts
from spira.yevon.process import get_rule_deck


RDD = get_rule_deck()


class B(spira.Cell):
    """ Cell with boxes to stretch a SRef containing two polygons. """

    def create_elementals(self, elems):

        p1 = spira.Rectangle(alias='P0', p1=(0, 0), p2=(12*1e6, 2*1e6), layer=RDD.PLAYER.M1.METAL)
        p2 = spira.Rectangle(alias='P1', p1=(5*1e6, 0), p2=(7*1e6, 15*1e6), layer=RDD.PLAYER.M1.METAL)
        p3 = spira.Rectangle(alias='P3', p1=(2*1e6, 4*1e6), p2=(6*1e6, 6*1e6), layer=RDD.PLAYER.M1.METAL)
        p4 = spira.Rectangle(alias='P4', p1=(6*1e6, 7*1e6), p2=(10*1e6, 9*1e6), layer=RDD.PLAYER.M1.METAL)
        c = spira.Cell(name='Cs1')
        c += spira.Rectangle(alias='P2', p1=(0,0), p2=(12*1e6, 2*1e6), layer=RDD.PLAYER.M1.METAL)
        S = spira.SRef(c, midpoint=(10*1e6, 0))

        elems += p1
        elems += p2
        elems += p3
        elems += p4
        elems += S

        return elems

    def create_ports(self, ports):
        
        ports += spira.Port(name='P1', midpoint=(0, 1*1e6), orientation=180, process=RDD.PROCESS.M3)
        ports += spira.Port(name='P2', midpoint=(22*1e6, 1*1e6), orientation=0, process=RDD.PROCESS.M3)
        ports += spira.Port(name='P3', midpoint=(6*1e6, 15*1e6), orientation=90, process=RDD.PROCESS.M3)
        ports += spira.Port(name='P4', midpoint=(2*1e6, 5*1e6), orientation=180, process=RDD.PROCESS.M3)
        ports += spira.Port(name='P5', midpoint=(10*1e6, 8*1e6), orientation=0, process=RDD.PROCESS.M3)
        
        return ports


# -------------------------------------------------------------------------------------------------------------


D = B()

D.output()
# D.write_gdsii_mask()


# vp = virtual_process_model(device=D, process_flow=RDD.VMODEL.PROCESS_FLOW)
# vp.write_gdsii_vmodel()

vp = virtual_process_intersection(device=D, process_flow=RDD.VMODEL.PROCESS_FLOW)
# vp.write_gdsii_vinter()

# E = D.expand_transform()
E = D.pcell.expand_flat_copy()

contacts = vp.contact_ports

for p in E.ports:
    if p.locked is False:
        contacts += p

nets = E.nets(contacts=contacts)

# --- Step 1:
g_cell = nets.disjoint()
E.plotly_netlist(G=g_cell, graphname='metal', labeltext='id')






