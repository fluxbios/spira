import gdspy
import numpy as np
import networkx as nx
from copy import copy, deepcopy
from spira.yevon import utils

from spira.core.parameters.restrictions import RestrictType
from spira.core.parameters.initializer import FieldInitializer
from spira.core.parameters.descriptor import DataFieldDescriptor, FunctionField, DataField
from spira.yevon.gdsii.elem_list import ElementalList, ElementalListField
from spira.yevon.geometry.coord import CoordField, Coord
from spira.yevon.visualization.color import ColorField
from spira.yevon.visualization import color
from spira.core.parameters.variables import NumberField
from spira.core.parameters.initializer import MetaInitializer
from spira.yevon.geometry.ports.port_list import PortList
from spira.yevon.gdsii import *
from spira.core.mixin import MixinBowl
from spira.yevon.gdsii.sref import SRef
from spira.yevon.process import get_rule_deck


RDD = get_rule_deck()


__all__ = ['Cell', 'Connector', 'CellField']


class MetaCell(MetaInitializer):
    """
    Called when an instance of a SPiRA class is
    created. Pareses all kwargs and passes it to
    the FieldInitializer for storing.

    class Via(spira.Cell):
        layer = param.LayerField()

    Gets called here and passes
    kwargs['layer': 50] to FieldInitializer.
    >>> via = Via(layer=50)
    """

    def __call__(cls, *params, **keyword_params):

        kwargs = cls.__map_parameters__(*params, **keyword_params)

        from spira import settings
        lib = None
        if 'library' in kwargs:
            lib = kwargs['library']
            del(kwargs['library'])
        if lib is None:
            lib = settings.get_current_library()

        if 'name' in kwargs:
            if kwargs['name'] is None:
                kwargs['__name_prefix__'] = cls.__name__

        cls.__keywords__ = kwargs
        cls = super().__call__(**kwargs)

        retrieved_cell = lib.get_cell(cell_name=cls.name)
        if retrieved_cell is None:
            lib += cls
            return cls
        else:
            del cls
            return retrieved_cell


class __Cell__(FieldInitializer, metaclass=MetaCell):

    __name_generator__ = RDD.ADMIN.NAME_GENERATOR

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __add__(self, other):
        from spira.yevon.geometry.ports.port import __Port__
        if other is None:
            return self
        if issubclass(type(other), __Port__):
            self.ports += other
        else:
            self.elementals += other
        return self


class CellAbstract(gdspy.Cell, __Cell__):

    def create_name(self):
        if not hasattr(self, '__name__'):
            self.__name__ = self.__name_generator__(self)
        return self.__name__

    def dependencies(self):
        deps = self.elementals.dependencies()
        deps += self
        return deps

    def flat_copy(self, level=-1):
        name = '{}_{}'.format(self.name, 'Flat'),
        return Cell(name, self.elementals.flat_copy(level=level))
    
    def is_layer_in_cell(self, layer):
        D = deepcopy(self)
        for e in D.flatten():
            return (e.layer == layer)
        return False

    @property
    def alias_cells(self):
        childs = {}
        for c in self.dependencies():
            childs[c.alias] = c
        return childs

    @property
    def alias_elems(self):
        elems = {}
        for e in self.elementals.polygons:
            elems[e.alias] = e
        return elems

    def __getitem__(self, key):
        from spira.yevon.gdsii.sref import SRef
        from spira.yevon.gdsii.polygon import Polygon
        keys = key.split(':')

        item = None
        if keys[0] in self.alias_cells:
            item = self.alias_cells[keys[0]]
        elif keys[0] in self.alias_elems:
            item = self.alias_elems[keys[0]]
        else:
            raise ValueError('Alias {} key not found!'.format(keys[0]))

        return item


class Cell(CellAbstract):
    """ A Cell encapsulates a set of elementals that
    describes the layout being generated. """

    name = DataField(fdef_name='create_name', doc='Name of the cell instance.')

    _next_uid = 0

    def get_alias(self):
        if not hasattr(self, '__alias__'):
            self.__alias__ = self.name.split('__')[0]
        return self.__alias__

    def set_alias(self, value):
        self.__alias__ = value

    alias = FunctionField(get_alias, set_alias, doc='Functions to generate an alias for cell name.')

    def __init__(self, name=None, elementals=None, ports=None, nets=None, library=None, **kwargs):

        __Cell__.__init__(self, **kwargs)
        gdspy.Cell.__init__(self, self.name, exclude_from_current=True)

        if name is not None:
            # s = '{}_{}'.format(name, self.__class__._ID)
            s = '{}_{}'.format(name, Cell._next_uid)
            self.__dict__['__name__'] = s
            Cell.name.__set__(self, s)
            # self.__class__._ID += 1

        if library is not None:
            self.library = library
        if elementals is not None:
            self.elementals = ElementalList(elementals)
        if ports is not None:
            self.ports = PortList(ports)

        self.uid = Cell._next_uid
        Cell._next_uid += 1

    def __repr__(self):
        class_string = "[SPiRA: Cell(\'{}\')] (elementals {}, ports {})"
        return class_string.format(self.name, self.elementals.__len__(), self.ports.__len__())

    def __str__(self):
        return self.__repr__()

    def transform(self, transformation=None):
        self.elementals.transform(transformation)
        self.ports.transform(transformation)
        return self

    def expand_transform(self):
        for S in self.elementals.sref:
            S.expand_transform()
        return self

    def expand_flat_copy(self, exclude_devices=False):
        from spira.yevon.gdsii.polygon import Polygon
        from spira.yevon.geometry.ports.port import Port
        from spira.yevon.gdsii.pcell import Device
        
        # FIXME: Check this.
        # D = deepcopy(self)
        S = self.expand_transform()
        C = Cell(name=S.name + '_ExpandedCell')
        def flat_polygons(subj, cell):
            for e in cell.elementals:
                if isinstance(e, Polygon):
                    subj += e
                elif isinstance(e, SRef):
                    if exclude_devices is True:
                        if isinstance(e.ref, Device):
                            subj += e
                        else:
                            flat_polygons(subj=subj, cell=e.ref)
                    else: 
                        flat_polygons(subj=subj, cell=e.ref)

            for p in cell.ports:
                port = Port(
                    name=p.name + "_" + cell.name,
                    midpoint=deepcopy(p.midpoint),
                    orientation=deepcopy(p.orientation),
                    process=deepcopy(p.process),
                    purpose=deepcopy(p.purpose),
                    width=deepcopy(p.width),
                    port_type=p.port_type,
                    local_pid=p.local_pid
                )
                subj.ports += port

            return subj

        D = flat_polygons(C, S)

        return D

    def move(self, midpoint=(0,0), destination=None, axis=None):
        """  """
        from spira.yevon.geometry.ports.base import __Port__

        if destination is None:
            destination = midpoint
            midpoint = [0,0]
    
        if issubclass(type(midpoint), __Port__):
            o = midpoint.midpoint
        elif isinstance(midpoint, Coord):
            o = midpoint
        elif np.array(midpoint).size == 2:
            o = midpoint
        elif midpoint in obj.ports:
            o = obj.ports[midpoint].midpoint
        else:
            raise ValueError("[PHIDL] [DeviceReference.move()] ``midpoint`` " +
                                "not array-like, a port, or port name")
    
        if issubclass(type(destination), __Port__):
            d = destination.midpoint
        elif isinstance(destination, Coord):
            d = destination
        elif np.array(destination).size == 2:
            d = destination
        elif destination in obj.ports:
            d = obj.ports[destination].midpoint
        else:
            raise ValueError("[PHIDL] [DeviceReference.move()] ``destination`` " +
                                "not array-like, a port, or port name")
    
        if axis == 'x':
            d = (d[0], o[1])
        if axis == 'y':
            d = (o[0], d[1])

        d = Coord(d[0], d[1])
        o = Coord(o[0], o[1])

        for e in self.elementals:
            e.move(midpoint=o, destination=d)

        for p in self.ports:
            mc = np.array(p.midpoint) + np.array(d) - np.array(o)
            p.move(midpoint=p.midpoint, destination=mc)

        return self

    def stretch_port(self, port, destination):
        """
        The elemental by moving the subject port, without
        distorting the entire elemental. Note: The opposite
        port position is used as the stretching center. 
        """
        from spira.core.transforms import stretching
        from spira.yevon.geometry import bbox_info
        from spira.yevon.gdsii.polygon import Polygon
        opposite_port = bbox_info.get_opposite_boundary_port(self, port)
        T = stretching.stretch_elemental_by_port(self, opposite_port, port, destination)
        if port.bbox is True:
            self = T(self)
        else:
            for i, e in enumerate(self.elementals):
                if isinstance(e, Polygon):
                    if e.id_string() == port.local_pid:
                        self.elementals[i] = T(e)
        return self

    def nets(self, lcar, contacts=None):
        return self.elementals.nets(lcar=lcar, contacts=contacts)


class Connector(Cell):
    """
    Ports are horizontal ports that connect SRef instances
    in the horizontal plane. They typcially represents the
    i/o ports of a components.

    Examples
    --------
    >>> term = spira.Port()
    """

    midpoint = CoordField()
    orientation = NumberField(default=0.0)
    width = NumberField(default=2)

    def __repr__(self):
        return ("[SPiRA: Connector] (name {}, midpoint {}, " +
            "width {}, orientation {})").format(self.name,
            self.midpoint, self.width, self.orientation
        )

    def create_ports(self, ports):
        ports += Port(name='P1', midpoint=self.midpoint, width=self.width, orientation=self.orientation)
        ports += Port(name='P2', midpoint=self.midpoint, width=self.width, orientation=self.orientation-180)
        return ports


# FIXME: Add restriction parameter.
def CellField(name=None, elementals=None, ports=None, library=None, **kwargs):
    from spira.yevon.gdsii.cell import Cell
    if 'default' not in kwargs:
        kwargs['default'] = Cell(name=name, elementals=elementals, library=library)
    R = RestrictType(Cell)
    return DataFieldDescriptor(restrictions=R, **kwargs)

