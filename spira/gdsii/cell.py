import gdspy
import numpy as np
import networkx as nx
from copy import copy, deepcopy

from spira import param

from spira.core.lists import ElementList
from spira.lne import *
from spira.gdsii import *

from spira.core.initializer import CellInitializer
from spira.core.mixin.property import CellMixin
from spira.core.mixin.gdsii_output import OutputMixin
from spira.gdsii.elemental.port import __Port__
from spira.core.mixin.transform import TranformationMixin


class __Cell__(gdspy.Cell, CellInitializer):

    __mixins__ = [OutputMixin, CellMixin, TranformationMixin]

    def __init__(self, name=None, elementals=None, ports=None, library=None, **kwargs):
        CellInitializer.__init__(self, **kwargs)
        gdspy.Cell.__init__(self, name, exclude_from_current=True)

        self.g = nx.Graph()

        if name is not None:
            self.__dict__['__name__'] = name
            Cell.name.__set__(self, name)
        if library is not None:
            self.library = library
        if elementals is not None:
            self.elementals = elementals
        if ports is not None:
            self.ports = ports

        # self.move(midpoint=self.center, destination=(0,0))
        # self.center = (0,0)

    def __add__(self, other):
        if other is None:
            return self
        if issubclass(type(other), __Port__):
            self.ports += other
        else:
            self.elementals += other
        return self

        # if issubclass(type(other), Cell):
        #     print(other)
        #     self.elementals += SRef(other)
        #     # for e in other.elementals:
        #     #     self.elementals += e
        #     # for p in other.ports:
        #     #     self.ports += p

    def __sub__(self, other):
        pass

    def __deepcopy__(self, memo):
        return Cell(name=self.name+'awe',
            ports=deepcopy(self.ports),
            elementals=deepcopy(self.elementals)
        )


class Netlist(__Cell__):

    nets = param.ElementListField(fdef_name='create_nets')

    netlist = param.DataField(fdef_name='create_netlist')

    merge = param.DataField(fdef_name='create_merge_nets')
    combine = param.DataField(fdef_name='create_combine_nodes')
    connect = param.DataField(fdef_name='create_connect_subgraphs')

    def create_nets(self, nets):
        return nets

    def create_merge_nets(self):
        g = nx.disjoint_union_all(self.nets)
        return g

    def create_combine_nodes(self):
        """
        Combine all nodes of the same type into one node.
        """

        def partition_nodes(u, v):

            if ('surface' in self.g.node[u]) and ('surface' in self.g.node[v]):
                if ('pin' not in self.g.node[u]) and ('pin' not in self.g.node[v]):
                    if self.g.node[u]['surface'].id0 == self.g.node[v]['surface'].id0:
                    # if self.g.node[u]['surface'] == self.g.node[v]['surface']:
                        return True

            if ('pin' in self.g.node[u]) and ('pin' in self.g.node[v]):
                # if self.g.node[u]['pin'].id0 == self.g.node[v]['pin'].id0:
                if self.g.node[u]['pin'] == self.g.node[v]['pin']:
                    return True

        def sub_nodes(b):
            S = self.g.subgraph(b)

            pin = nx.get_node_attributes(S, 'pin')
            surface = nx.get_node_attributes(S, 'surface')
            center = nx.get_node_attributes(S, 'pos')

            sub_pos = list()
            for key, value in center.items():
                sub_pos = [value[0], value[1]]

            return dict(pin=pin, surface=surface, pos=sub_pos)

        Q = nx.quotient_graph(self.g, partition_nodes, node_data=sub_nodes)

        Pos = nx.get_node_attributes(Q, 'pos')
        Label = nx.get_node_attributes(Q, 'pin')
        Polygon = nx.get_node_attributes(Q, 'surface')

        Edges = nx.get_edge_attributes(Q, 'weight')

        g1 = nx.Graph()

        for key, value in Edges.items():
            n1, n2 = list(key[0]), list(key[1])
            g1.add_edge(n1[0], n2[0])

        for n in g1.nodes():
            for key, value in Pos.items():
                if n == list(key)[0]:
                    g1.node[n]['pos'] = [value[0], value[1]]

            for key, value in Label.items():
                if n == list(key)[0]:
                    if n in value:
                        g1.node[n]['pin'] = value[n]

            for key, value in Polygon.items():
                if n == list(key)[0]:
                    g1.node[n]['surface'] = value[n]
        return g1

    def create_connect_subgraphs(self):
        graphs = list(nx.connected_component_subgraphs(self.g))
        g = nx.disjoint_union_all(graphs)
        return g

    def create_netlist(self):

        self.g = self.merge
        # self.g = self.combine

        self._plotly_graph(G=self.g, graphname=self.name, labeltext='id')


class CellAbstract(Netlist):

    name = param.StringField()
    ports = param.ElementListField(fdef_name='create_ports')
    elementals = param.ElementListField(fdef_name='create_elementals')

    def create_elementals(self, elems):
        result = ElementList()
        return result

    def create_ports(self, ports):
        return ports

    def flatten(self):
        self.elementals = self.elementals.flatten()
        return self.elementals

    def flat_copy(self, level=-1, commit_to_gdspy=False):
        self.elementals = self.elementals.flat_copy(level, commit_to_gdspy)
        return self.elementals

    def dependencies(self):
        deps = self.elementals.dependencies()
        deps += self
        return deps

    @property
    def pbox(self):
        # from spira.gdsii.elemental.polygons import Polygons
        (a,b), (c,d) = self.bbox
        points = [[[a,b], [c,b], [c,d], [a,d]]]
        return points
        # return Polygons(shape=points)

    def commit_to_gdspy(self):
        cell = gdspy.Cell(self.name, exclude_from_current=True)
        for e in self.elementals:
            if issubclass(type(e), Cell):
                # pass
                for elem in e.elementals:
                    elem.commit_to_gdspy(cell=cell)
                for port in e.ports:
                    port.commit_to_gdspy(cell=cell)
            elif not isinstance(e, (SRef, ElementList, Graph, Mesh)):
                e.commit_to_gdspy(cell=cell)
        return cell

    def move(self, midpoint=(0,0), destination=None, axis=None):
        """
        Moves elements of the Device from the midpoint point to
        the destination. Both midpoint and destination can be 1x2
        array-like, Port, or a key corresponding to
        one of the Ports in this device
        """

        if destination is None:
            destination = midpoint
            midpoint = [0,0]

        if issubclass(type(midpoint), __Port__):
            o = midpoint.midpoint
        elif np.array(midpoint).size == 2:
            o = midpoint
        elif midpoint in self.ports:
            o = self.ports[midpoint].midpoint
        else:
            raise ValueError('[DeviceReference.move()] ``midpoint`` ' + \
                             'not array-like, a port, or port name')

        if issubclass(type(destination), __Port__):
            d = destination.midpoint
        elif np.array(destination).size == 2:
            d = destination
        elif destination in self.ports:
            d = self.ports[destination].midpoint
        else:
            raise ValueError('[DeviceReference.move()] ``destination`` ' + \
                             'not array-like, a port, or port name')

        if axis == 'x':
            d = (d[0], o[1])
        if axis == 'y':
            d = (o[0], d[1])

        dx, dy = np.array(d) - o

        for e in self.elementals:
            if issubclass(type(e), (LabelAbstract, PolygonAbstract)):
                e.translate(dx, dy)
            if isinstance(e, (Cell, SRef)):
                e.move(destination=d, midpoint=o)

        for p in self.ports:
            mc = np.array(p.midpoint) + np.array(d) - np.array(o)
            p.move(midpoint=p.midpoint, destination=mc)

        return self

    def reflect(self, p1=(0,1), p2=(0,0)):
        """ Reflects the cell around the line [p1, p2]. """
        for e in self.elementals:
            if not issubclass(type(e), (LabelAbstract, __Port__)):
                e.reflect(p1, p2)
        for p in self.ports:
            p.midpoint = self.__reflect__(p.midpoint, p1, p2)
            phi = np.arctan2(p2[1]-p1[1], p2[0]-p1[0])*180 / np.pi
            p.orientation = 2*phi - p.orientation
        return self

    def rotate(self, angle=45, center=(0,0)):
        """ Rotates the cell with angle around a center. """
        if angle == 0:
            return self
        for e in self.elementals:
            if issubclass(type(e), PolygonAbstract):
                e.rotate(angle=angle, center=center)
            elif isinstance(e, SRef):
                e.rotate(angle, center)
        ports = self.ports
        self.ports = ElementList()
        for p in ports:
            if issubclass(type(p), __Port__):
                p.midpoint = self.__rotate__(p.midpoint, angle, center)
                p.orientation = np.mod(p.orientation + angle, 360)
                self.ports += p
        return self

    def get_ports(self, level=None):
        """ Returns copies of all the ports of the Device """
        port_list = [p._copy() for p in self.ports]
        if level is None or level > 0:
            for r in self.elementals.sref:
                if level is None:
                    new_level = None
                else:
                    new_level = level - 1

                ref_ports = r.ref.get_ports(level=new_level)

                tf = {
                    'midpoint': r.midpoint,
                    'rotation': r.rotation,
                    'magnification': r.magnification,
                    'reflection': r.reflection
                }

                ref_ports_transformed = []
                for rp in ref_ports:
                    new_port = rp._copy()
                    new_port = new_port.transform(tf)
                    ref_ports_transformed.append(new_port)
                port_list += ref_ports_transformed
        return port_list


class Cell(CellAbstract):
    """ A Cell encapsulates a set of elementals that
    describes the layout being generated. """

    def __repr__(self):
        if hasattr(self, 'elementals'):
            elems = self.elementals
            return ("[SPiRA: Cell(\'{}\')] " +
                    "({} elementals: {} sref, {} cells, {} polygons, " +
                    "{} labels, {} ports)").format(
                        self.name,
                        elems.__len__(),
                        elems.sref.__len__(),
                        elems.cells.__len__(),
                        elems.polygons.__len__(),
                        elems.labels.__len__(),
                        self.ports.__len__()
                    )
        else:
            return "[SPiRA: Cell(\'{}\')]".format(self.__class__.__name__)

    def __str__(self):
        return self.__repr__()

    @property
    def id(self):
        return self.__str__()











