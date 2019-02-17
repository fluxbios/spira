import spira
import pyclipper
import numpy as np

from spira import param
from copy import copy, deepcopy
from spira.gdsii.elemental.port import PortAbstract, __Port__
from spira.core.initializer import ElementalInitializer
from spira.gdsii.group import GroupElementals


RDD = spira.get_rule_deck()


class Term(PortAbstract):
    """
    Terminals are horizontal ports that connect SRef instances
    in the horizontal plane. They typcially represents the
    i/o ports of a components.

    Examples
    --------
    >>> term = spira.Term()
    """

    edgelayer = param.LayerField(name='Edge', number=63)
    arrowlayer = param.LayerField(name='Arrow', number=77)

    width = param.FloatField(default=2*1e6)
    length = param.FloatField(default=0.1*1e6)

    layer1 = param.LayerField()
    layer2 = param.LayerField()

    is_edge = param.BoolField(default=False)

    port1 = param.DataField(fdef_name='create_port1')
    port2 = param.DataField(fdef_name='create_port2')

    def get_edge_polygon(self):
        if not hasattr(self, '__edge__'):
            from spira import shapes
            rect_shape = shapes.RectangleShape(
                p1=[0, 0],
                p2=[self.width, self.length]
            )

            ply = spira.Polygons(
                shape=rect_shape,
                gdslayer=self.edgelayer,
            )

            if self.reflection:
                ply.reflect()
            ply.rotate(angle=self.orientation+90)
            ply.move(midpoint=ply.center, destination=self.midpoint)

            _edge = ply
        else:
            _edge = self.__edge__
        return _edge
        
    def set_edge_polygon(self, value):

        if self.reflection:
            value.reflect()
        value.rotate(angle=self.orientation)
        value.move(midpoint=value.center, destination=self.midpoint)

        self.__edge__ = value

    def get_arrow_polygon(self):
        if not hasattr(self, '__arrow__'):
            # print('jqkdwqdk')
            print(self.orientation)
            from spira import shapes
            arrow_shape = shapes.ArrowShape(
                a = self.length,
                b = self.length/2,
                c = self.length*2
            )

            # arrow_shape.apply_merge
            ply = spira.Polygons(
                shape=arrow_shape,
                gdslayer=self.arrowlayer,
                direction=-90
            )

            if not self.is_edge:
                ply.rotate(angle=self.orientation-90)

            # if self.reflection:
            #     ply.reflect()
            ply.rotate(angle=self.orientation)
            ply.move(midpoint=ply.center, destination=self.midpoint)

            self.__arrow__ = ply
        return self.__arrow__

    def set_arrow_polygon(self, value):

        if self.reflection:
            value.reflect()
        value.rotate(angle=self.orientation+180)
        value.move(midpoint=value.center, destination=self.midpoint)

        self.__arrow__ = value

    def get_label(self):
        if not hasattr(self, '__label__'):
            label = spira.Label(
                position=self.midpoint,
                text=self.name,
                gdslayer=self.gdslayer,
                texttype=64,
                color='#808080'
            )
            self.__label__ = label
        return self.__label__

    def set_label(self, value):
        self.__label__ = value

    edge = param.FunctionField(get_edge_polygon, set_edge_polygon, doc='The edge of a polygon that the terminal connects to.')
    arrow = param.FunctionField(get_arrow_polygon, set_arrow_polygon, doc='Arrow polygon that shows the terminal direction.')
    label = param.FunctionField(get_label, set_label, doc='The terminal label to filtering purposes.')

    def __init__(self, port=None, elementals=None, polygon=None, **kwargs):
        ElementalInitializer.__init__(self, **kwargs)

        if elementals is not None:
            self.elementals = elementals

    def __repr__(self):
        return ("[SPiRA: Term] (name {}, number {}, midpoint {}, " +
            "width {}, orientation {}, length {})").format(self.name,
            self.gdslayer.number, self.midpoint,
            self.width, self.orientation, self.length
        )

    def __str__(self):
        return self.__repr__()

    def create_port1(self):
        port = spira.Port(name='P1', midpoint=self.midpoint, gdslayer=self.layer1)
        return port

    def create_port2(self):
        port = spira.Port(name='P2', midpoint=self.midpoint, gdslayer=self.layer2)
        return port

    def encloses(self, polygon):
        if pyclipper.PointInPolygon(self.endpoints[0], polygon) != 0:
            return True
        elif pyclipper.PointInPolygon(self.endpoints[1], polygon) != 0:
            return True

    @property
    def endpoints(self):
        dx = self.width/2*np.cos((self.orientation - 90)*np.pi/180)
        dy = self.width/2*np.sin((self.orientation - 90)*np.pi/180)
        left_point = self.midpoint - np.array([dx,dy])
        right_point = self.midpoint + np.array([dx,dy])
        return np.array([left_point, right_point])

    @endpoints.setter
    def endpoints(self, points):
        p1, p2 = np.array(points[0]), np.array(points[1])
        self.midpoint = (p1+p2)/2
        dx, dy = p2-p1
        self.orientation = np.arctan2(dx,dy)*180/np.pi
        self.width = np.sqrt(dx**2 + dy**2)

    def create_elementals(self, elems):
        elems += self.edge
        elems += self.arrow
        # elems += self.label
        return elems

    def _copy(self):
        new_port = Term(
            parent=self.parent,
            name=self.name,
            midpoint=deepcopy(self.midpoint),
            orientation=self.orientation,
            reflection=self.reflection,
            # elementals=deepcopy(self.elementals),
            edge=deepcopy(self.edge),
            arrow=deepcopy(self.arrow),
            width=self.width,
            length=self.length,
            gdslayer=deepcopy(self.gdslayer),
            edgelayer=deepcopy(self.edgelayer),
            arrowlayer=deepcopy(self.arrowlayer),
            color=self.color,
            is_edge=self.is_edge
        )
        return new_port


class Dummy(Term):
    """
    Terminals are horizontal ports that connect SRef instances
    in the horizontal plane. They typcially represents the
    i/o ports of a components.

    Examples
    --------
    >>> term = spira.Term()
    """

    def __repr__(self):
        return ("[SPiRA: Dummy] (name {}, number {}, midpoint {}, " +
            "width {}, orientation {})").format(self.name,
            self.gdslayer.number, self.midpoint,
            self.width, self.orientation
        )

    # def _copy(self):
    #     new_port = Dummy(parent=self.parent,
    #         name=self.name,
    #         midpoint=self.midpoint,
    #         width=self.width,
    #         length=self.length,
    #         gdslayer=deepcopy(self.gdslayer),
    #         orientation=self.orientation)
    #     return new_port


if __name__ == '__main__':

    cell = spira.Cell('Terminal Test')

    term = Term()

    cell += term

    # print(cell.ports)
    cell.output()









