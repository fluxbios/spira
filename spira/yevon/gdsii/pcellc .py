from spira.yevon.gdsii.cell import Cell
from spira.yevon.utils import netlist
from spira.yevon.gdsii.elem_list import ElementListParameter, ElementList
from spira.yevon.geometry.ports import PortList
from spira.yevon.geometry.ports import Port as Port
from spira.core.parameters.descriptor import Parameter
from copy import deepcopy
import numpy as np
import networkx as networkx
from spira.core.parameters.variables import *
from spira.yevon.process import get_rule_deck


RDD = get_rule_deck()


__all__ = ['PCell', 'Device', 'Circuit']


class PCell(Cell):
    """  """

    pcell = BoolParameter(default=True)
    routes = ElementListParameter(doc='List of `Route` elements connected to the cell.')
    structures = ElementListParameter(doc='List of cell structures that coalesces the top-level cell.')
    extract_netlist = Parameter(fdef_name='create_extract_netlist')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Device(PCell):
    """  """

    # lcar = NumberParameter(default=RDD.PCELL.LCAR_DEVICE)
    lcar = NumberParameter(default=1)

    def __init__(self, pcell=True, **kwargs):
        super().__init__(**kwargs)
        self.pcell = pcell

    def __repr__(self):
        class_string = "[SPiRA: Device(\'{}\')] (elements {}, ports {})"
        return class_string.format(self.name, self.elements.__len__(), self.ports.__len__())

    def __str__(self):
        return self.__repr__()

    def __create_elements__(self, elems):

        elems = self.create_elements(elems)
        elems += self.structures
        elems += self.routes

        if self.pcell is True:
            D = Cell(elements=elems.flat_copy())
            elems = RDD.FILTERS.PCELL.DEVICE(D).elements

        return elems

    def create_netlist(self):

        print('Device netlist')

        net = super().create_netlist()
        net = netlist.combine_net_nodes(net=net, algorithm=['d2d'])
        net = netlist.combine_net_nodes(net=net, algorithm=['s2s'])

        return net

    def create_extract_netlist(self):
        return self.netlist


class Circuit(PCell):
    """  """

    corners = StringParameter(default='miter', doc='Define the type of path joins.')
    bend_radius = NumberParameter(allow_none=True, default=None, doc='Bend radius of path joins.')

    # lcar = NumberParameter(default=RDD.LCAR_CIRCUIT)
    lcar = NumberParameter(default=100)

    def __repr__(self):
        class_string = "[SPiRA: Circuit(\'{}\')] (elements {}, ports {})"
        return class_string.format(self.name, self.elements.__len__(), self.ports.__len__())

    def __str__(self):
        return self.__repr__()

    def __create_elements__(self, elems):
        from spira.yevon.gdsii.sref import SRef

        elems = self.create_elements(elems)
        elems += self.structures
        elems += self.routes

        def wrap_references(cell, c2dmap, devices):
            for e in cell.elements.sref:
                if isinstance(e.reference, Device):
                    D = deepcopy(e.reference)
                    D.elements.transform(e.transformation)
                    D.ports.transform(e.transformation)
                    devices[D] = D.elements

                    D.elements = ElementList()
                    S = deepcopy(e)
                    S.reference = D
                    c2dmap[cell] += S
                else:
                    S = deepcopy(e)
                    S.reference = c2dmap[e.reference]
                    c2dmap[cell] += S

        if self.pcell is True:

            ex_elems = elems.expand_transform()

            C = Cell(elements=ex_elems)

            c2dmap, devices = {}, {}

            for cell in C.dependencies():
                D = Cell(name=cell.name,
                    elements=deepcopy(cell.elements.polygons),
                    ports=deepcopy(cell.ports))
                c2dmap.update({cell: D})

            for cell in C.dependencies():
                wrap_references(cell, c2dmap, devices)

            D = c2dmap[C]
            
            # for e in D.elements.polygons:
            #     if e.layer.purpose.symbol == 'METAL':
            #         e.layer.purpose = RDD.PURPOSE.CIRCUIT_METAL

            F = RDD.FILTERS.PCELL.CIRCUIT

            # from spira.yevon import filters
            # F = filters.ToggledCompositeFilter(filters=[])
            # F += filters.ProcessBooleanFilter(name='boolean')

            Df = F(D)

            # NOTE: Add devices back into the circuit.
            for d in Df.dependencies():
                if d in devices.keys():
                    d.elements = devices[d]
                    # for e in d.elements.polygons:
                    #     if e.layer.purpose.symbol == 'METAL':
                    #         e.layer.purpose = RDD.PURPOSE.DEVICE_METAL

            elems = Df.elements

        return elems

    def create_netlist(self):
        from spira.yevon import filters

        print('Circuit netlist')

        net = super().create_netlist()
        net = netlist.combine_net_nodes(net=net, algorithm=['d2d'])
        net = netlist.combine_net_nodes(net=net, algorithm=['s2s'])
        
        return net

    def create_extract_netlist(self):

        net = self.netlist

        net = net.convert_pins()
        net = net.del_branch_attrs()

        from spira.yevon import filters
        f = filters.ToggledCompositeFilter(filters=[])
        f += filters.NetBranchCircuitFilter()
        f += filters.NetDummyFilter()
        f += filters.NetBranchCircuitFilter()

        net = f(net)[0]

        from spira.yevon.utils import netlist
        net = netlist.combine_net_nodes(net=net, algorithm=['b2b'])
        nodes = net.g.nodes.data()
        create_electrical_netlist(nodes,net.g)
        return net

def create_electrical_netlist(nodes,netgraph):
    
    #in format ([name,nodenr,midpoint])
    terminal_nodes = []
    inductor_nodes = []
    jj_nodes = []
    #this keeps track of node numbers globally
    L = 0
    P = 0
    R = 0
    P = 0
    J = 0
    for n in nodes:
    
        try:
            current_node_attributes = n[1]
            dev_ref_node = current_node_attributes['device_reference']
            if(isinstance(dev_ref_node, Port)):
                
                purpose = dev_ref_node.purpose
                portname = purpose.__repr__()
                if("PinPort" in portname):
                    #print(str('P')+str(P),n[0],0)
                    P += 1
                    terminal_nodes.append([str('P')+str(P),n[0],0])
                    #terminal_nodes.append([dev_ref_node.name.split(":")[1],n[0],dev_ref_node.midpoint])
        except Exception as e:
            print(e)
            continue
    
    #print(nodes[176])
    #now we have to find out to what terminals are connected - determine of it is a resistor,inductor etc
    
    for port in terminal_nodes:
        edge = netgraph.edges([int(port[1])])
        non_term_node = None
        for e in edge:
            #we know the the first enter in (1,2) tuple is the terminal node, and 2nd is connected node
            connected_to_term_node = np.asarray(e)[1]
            next_edge = list(netgraph.edges(connected_to_term_node))
            for e1, e2  in next_edge:
                
                if e1 == int(port[1]) and non_term_node is None:
                    non_term_node = e2
                if e2 == int(port[1]) and non_term_node is None:
                    non_term_node = e1
                

        non_term_node_info = nodes[(int(non_term_node))]
        
        process_polygon = (non_term_node_info['process_polygon'])
        layer = process_polygon.layer.process.symbol
        
        if "M" in layer:
            #print("L"+str(L),port[1],non_term_node,200)
            inductor_nodes.append(["L"+str(L),port[1],non_term_node,2])
            L += 1

    for n in nodes:

        try:
            current_node_attributes = n[1]
            node_nr = n[0]
            dev_ref_node = current_node_attributes['device_reference']
            process = dev_ref_node.process
            symbol = process.symbol
            if(symbol == 'J5'):
                connected_j5_nodes = []
                #print(node_nr,symbol)
                connected_nodes = list(netgraph.edges([int(node_nr)]))
                for e1, e2 in connected_nodes:
                    
                    if e1 == int(node_nr):
                        connected_j5_nodes.append(e2)
                    if e2 == int(node_nr):
                        connected_j5_nodes.append(e1)
                #now we have the nodes to which the Josephson layer is connected.
                #Now  we need to establish that the entire JJ model fits - i.e making sure all connections are present so we can 
                # say for certain a JJ is present and know where it begins and ends. this will allow us to get the following format
                # Pjj1 node1 node2 250 $jjmodal
                # Ljj1 node2 node0 2    $pulldowninductor
                
                connected_j5_nodes = np.asarray(connected_j5_nodes)
                for node in connected_j5_nodes:
                    port = []
                    node_info = nodes[node]
                    for key in node_info:
                        if "device_reference" in key:
                            # THIS IS THE M6 DUMMYPORT IN THE VIRTUAL JJ MODAL
                            port = node_info[key]
                            process_info = port.__repr__()
                            process = node_info['process_polygon'].layer.process.symbol
                            # NOW DETERMINE SHORTEST PATH TO AND WHICH TERMINAL
                            adjacent_edge = netgraph.edges([int(node)])
                            #print(node, process_info)
                            jj = (path_to_terminal(node,terminal_nodes,netgraph,nodes))
                            
                            jj[0][0] = jj[0][0]+str(J)
                            jj_nodes.append(jj)
                            #print(jj[0][0], jj[0][1], jj[0][2],200)
                            #print("L"+str(L), jj[0][2], 0, 0.2)
                            inductor_nodes.append(["L"+str(L), jj[0][2], 0, 0.2])
                            L += 1
                            J = J+1
                        if "branch_node" in key:
                            # THIS IS THE FIRST ADJACENT M5 BRANCH PORT IN THE JJ MODAL
                            port = node_info[key]
                            process_info = port.__repr__()
                            process = node_info['process_polygon'].layer.process.symbol
                            

                            #### AT THIS POINT IN THE ALGORITHM WE HAVE ALL JJS LOCATED, TERMINALS AND THEIR CONNECTED INCDUTORS!
    return



        

























        
def is_node(begin_node,destination_node,netgraph,path):

    begin_node_edges = netgraph.edges(int(begin_node))
    print("beginning iteration of is_node with params: ",begin_node,destination_node,path)
    
    for edges in begin_node_edges:
        
        edge_arr = np.asarray(edges)
        if edge_arr[0] != destination_node and edge_arr[0] != begin_node and edge_arr[0] not in path:
            print("directly adjacent nodes was not the destination node edge1", edge_arr[0])
            path.append(edge_arr[0])
            is_node(edge_arr[0],destination_node,netgraph,path)
        if edge_arr[1] != destination_node and edge_arr[1] != begin_node and edge_arr[1] not in path:
            print("directly adjacent nodes was not the destination node edge2", edge_arr[1])
            path.append(edge_arr[1])
            is_node(edge_arr[1],destination_node,netgraph,path)
            #print(netgraph.edge(edge_arr[1]))
        if edge_arr[0] == destination_node:
            path.append(edge_arr[0])
            print("path found to destination node")
            return
        if edge_arr[1] == destination_node:
            print("path found to destination node")
            path.append(edge_arr[1])
            return
        

        
        #elif edge_arr[1] == destination_node:  #this means the edge is a member  or the destination node
        #    print("path found to destination node")
        #    path.append(edge_arr[1])
        #    return path
        #else:
        #    print("edge_arr[0] is now being processed")
        #    is_node(edge_arr[0],destination_node,netgraph,path)
    return