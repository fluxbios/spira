import spira
from spira import param
from spira import shapes
from spira.lpe.layers import *
from spira.lrc.rules import *
from spira.lrc.checking import Rules
from spira.lpe.containers import __CellContainer__

from spira.lne.graph import Graph
from spira.lne.mesh import Mesh
from spira.lne.geometry import Geometry
from demo.pdks import ply
from spira.lpe import mask


RDD = spira.get_rule_deck()


class __ProcessLayer__(__CellContainer__):

    cell_elems = param.ElementListField()
    level = param.IntegerField(default=1)


class MetalLayers(__ProcessLayer__):
    """
    Decorates all elementas with purpose metal with
    LCells and add them as elementals to the new class.
    """

    metal_layers = param.DataField(fdef_name='create_metal_layers')

    def create_metal_layers(self):
        elems = spira.ElementList()
        for pl in RDD.PLAYER.get_physical_layers(purposes='METAL'):
            metal = mask.Metal(
                cell=self.cell,
                cell_elems=self.cell_elems,
                player=pl,
                level=self.level
            )
            elems += spira.SRef(metal)
        return elems

    def create_elementals(self, elems):
        # TODO: Apply DRC checking between metals, before being placed.
        for lcell in self.metal_layers:
            elems += lcell
        return elems


class NativeLayers(MetalLayers):
    """
    Decorates all elementas with purpose via with
    LCells and add them as elementals to the new class.
    """

    native_layers = param.DataField(fdef_name='create_native_layers')

    def create_native_layers(self):
        elems = spira.ElementList()
        for pl in RDD.PLAYER.get_physical_layers(purposes=['VIA', 'JUNCTION']):
            native = mask.Native(
                cell=self.cell,
                cell_elems=self.cell_elems,
                player=pl,
                level=self.level
            )
            elems += spira.SRef(native)
        return elems

    def create_elementals(self, elems):
        super().create_elementals(elems)
        # Only add it if its a Device.
        if self.level == 1:
            for lcell in self.native_layers:
                elems += lcell
        return elems


class GroundLayers(NativeLayers):

    plane_elems = param.ElementListField() # Elementals like skyplanes and groundplanes.
    ground_layer = param.DataField(fdef_name='create_merged_ground_layers')

    def create_merged_ground_layers(self):
        points = []
        for p in self.plane_elems.flat_copy():
            for pp in p.polygons:
                points.append(pp)
        if points:
            ll = Layer(number=RDD.GDSII.GPLAYER, datatype=6)
            merged_ply = UnionPolygons(polygons=points, gdslayer=ll)
            return merged_ply
        return None

    def create_elementals(self, elems):
        super().create_elementals(elems)

        # if self.level == 1:
        #     if self.ground_layer:
        #         box = self.cell.bbox
        #         # box.move(midpoint=box.center, destination=(0,0))

        #         gnd = self.ground_layer | box
        #         if gnd:
        #             c_glayer = CGLayers(layer=gnd.gdslayer)
        #             name = 'GLayer_{}_{}'.format(self.cell.name, gnd.gdslayer.number)
        #             gnd_layer = GLayer(name=name, layer=gnd.gdslayer, player=gnd)
        #             c_glayer += spira.SRef(gnd_layer)
        #             elems += spira.SRef(c_glayer)

        return elems


class ConnectDesignRules(GroundLayers):

    metal_elems = param.ElementListField()

    def create_elementals(self, elems):
        super().create_elementals(elems)

        # incorrect_elems = ElementList()
        # correct_elems = ElementList()

        # for rule in RDD.RULES.elementals:
        #     if not rule.apply(elems):
        #         for composed_lcell in elems:
        #             for lcell in composed_lcell.ref.elementals.sref:
        #                 if lcell.ref.layer.number == rule.layer1.number:
        #                     correct_elems += lcell

        return elems


class __StructureCell__(ConnectDesignRules):
    """ Add a GROUND bbox to Device for primitive and DRC 
    detection, since GROUND is only in Mask Cell. """

    def create_elementals(self, elems):
        super().create_elementals(elems)
        return elems

    def create_ports(self, ports):
        flat_elems = self.cell_elems.flat_copy()
        port_elems = flat_elems.get_polygons(layer=RDD.PURPOSE.TERM)
        label_elems = flat_elems.labels

        for port in port_elems:
            for label in label_elems:

                lbls = label.text.split(' ')
                s_p1, s_p2 = lbls[1], lbls[2]
                p1, p2 = None, None

                for m1 in RDD.PLAYER.get_physical_layers(purposes=['METAL', 'GND']):
                    if m1.layer.name == s_p1:
                        p1 = spira.Layer(name=lbls[0], 
                            number=m1.layer.number, 
                            datatype=RDD.GDSII.TEXT
                        )
                        if label.point_inside(ply=port.polygons[0]):
                            ports += spira.Term(
                                name=lbls[0],
                                layer1=p1,
                                layer2=p2,
                                midpoint=label.position,
                                width=port.dx,
                                length=port.dy
                            )
                    if m1.layer.name == s_p2:
                        p2 = spira.Layer(name=lbls[0], 
                            number=m1.layer.number, 
                            datatype=RDD.GDSII.TEXT
                        )
                        if label.point_inside(ply=port.polygons[0]):
                            ports += spira.Term(
                                name=lbls[1],
                                layer1=p1,
                                layer2=p2,
                                midpoint=label.position,
                                width=port.dy
                            )
        return ports












