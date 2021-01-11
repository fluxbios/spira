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
    net_dummies = []
    dummy_nodes = []
    tested_dummy_nodes = []
    not_tested_dummy_nodes = []
    not_tested_term_nodes = []
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
            #print(e)
            continue

    #PRINT PURPOSE REMOVE LATER
    for pasd in terminal_nodes:
        print(pasd[0],pasd[1],pasd[2])

    ################REMOVE TILL HERE ###############
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
                print("L"+str(L),port[1],non_term_node,2)
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
                connected_nodes = list(netgraph.edges([int(node_nr)]))
                for e1, e2 in connected_nodes:
                    
                    if e1 == int(node_nr):
                        connected_j5_nodes.append(e2)
                    if e2 == int(node_nr):
                        connected_j5_nodes.append(e1)
                
                connected_j5_nodes = np.asarray(connected_j5_nodes)
                for node in connected_j5_nodes:
                    port = []
                    node_info = nodes[node]
                    for key in node_info:
                        if "device_reference" in key:
                            # THIS IS THE M6 DUMMYPORT IN THE VIRTUAL JJ MODAL
                            # It's important to note here the that Node Y, in JJx Node X Node Y JunctionArea, is the DUMMY NODE from netgraph
                            port = node_info[key]
                            process_info = port.__repr__()
                            process = node_info['process_polygon'].layer.process.symbol
                            # NOW DETERMINE SHORTEST PATH TO AND WHICH TERMINAL
                            adjacent_edge = netgraph.edges([int(node)])
                            #print(node, process_info)
                            jj = (path_to_terminal(node,terminal_nodes,netgraph,nodes))
                            
                            jj[0][0] = jj[0][0]+str(J)
                            jj_nodes.append(jj)
                            print(jj[0][0], jj[0][1], jj[0][2],200)
                            print("L"+str(L), jj[0][2], 0, 0.2)
                            inductor_nodes.append(["L"+str(L), jj[0][2], 0, 0.2])
                            net_dummies.append(jj[0][1])
                            L += 1
                            J = J+1
                        if "branch_node" in key:
                            # THIS IS THE FIRST ADJACENT M5 BRANCH PORT IN THE JJ MODAL
                            port = node_info[key]
                            process_info = port.__repr__()
                            process = node_info['process_polygon'].layer.process.symbol

        except Exception as e:
            #print(e)
            continue

    #########################################################
    # Now we will start to look at the ramaining dummy nodes and determine the path to already ananlyzed
    for n in nodes:

        try:
            
            current_node_attributes = n[1]
            node_nr = n[0]
            dev_ref_node = current_node_attributes['device_reference']
            port = dev_ref_node.__repr__()
            if "DummyPort" in port:
                dummy_nodes.append([node_nr])
        except Exception as e:
            #print(e)
            continue



    # Find out what nodes (dummy) have been used during JJ calculations already
    for jj in jj_nodes:
        tested_dummy_nodes.append(jj[0][2])
    
    for nodes1 in dummy_nodes:
        if nodes1 not in tested_dummy_nodes:
            not_tested_dummy_nodes.append(nodes1)






    for noded in not_tested_dummy_nodes:
        ni = np.asarray(noded)
        for tested_node in tested_dummy_nodes:          
            path = networkx.algorithms.shortest_paths.generic.shortest_path(netgraph,source = ni[0],target = tested_node)
            yedges = list(netgraph.edges(path[-1]))

            for edges in path:
                if edges != ni and edges != tested_node:
                    for d in yedges:
                        if edges in d:
                            print("L"+str(L),d[0],noded[0], 2)
                            inductor_nodes.append(["L"+str(L),d[0],noded[0], 2])
                            L = L+1

        for te in terminal_nodes:
            path = networkx.algorithms.shortest_paths.generic.shortest_path(netgraph,source = ni[0],target = te[1])
            #print("Terminal ",te," is being analyzed")
            flag = False
            del path[0]
            del path[-1]
            for induc in inductor_nodes:

                n1,n2 = induc[1],induc[2]
                if n1 in path and n1 != 0:
                    flag = True
                if n2 in path and n2 != 0:
                    flag = True
            #print(flag)
            if flag == False:
                #we know the resistors/inductors have not been added for this terminal as it is unanalyzed (there are no components containing nodes connected to this terminal)

                try:
                    flipflop = True  # just used to determine which node lies first || Flip is true, flop is false
                    disjoint_detected_node = None
                    for p in path:
                        node_val = nodes[p]

                        for key in node_val:
                            if "branch_node" in key:
                                pa = (node_val[key])
                                proc = pa.__repr__()
                                pdf = node_val['process_polygon'].layer.process.symbol
                                if "M" in pdf:
                                    edge_pair = netgraph.edges(p)
                                    thispair = 0
                                    for pairs in edge_pair:
                                        da = nodes[pairs[1]] #adjacent nodes
                                        for key2 in da:
                                            if "device_reference" in key2:
                                                pr = da[key2].__repr__()
                                                if "ContactPort" in pr:
                                                    thispair += 1
                                    if thispair == 2:

                                        #print("via i believe...")
                                        pda = netgraph.edges(p)
                                        lf = list(pda)
                                        asd = np.asarray(lf)
                                        disjoint_detected_node = asd[0,1]
                                        if flipflop == True:
                                            #print("disjointed via FLIP",disjoint_detected_node)
                                            flipflop = False
                                        else:
                                            #print("disjointed via FLOP", disjoint_detected_node)
                                            flipflop = True

                                        continue
                                    else:
                                        #print(pa)
                                        la = list(netgraph.edges(p))
                                        la = np.asarray(la)
                                        if disjoint_detected_node is not None:

                                            if flipflop == True:
                                                #print(la[0,1],la[1,1],"FLIP")
                                                print("L"+str(L),la[0,1],disjoint_detected_node,2)
                                                L += 1
                                                flipflop = False
                                            else:
                                                #print("L"+str(L),disjoint_detected_node,la[0,1],"FLOP")
                                                print("L" + str(L), disjoint_detected_node, la[0, 1],2)
                                                flipflop = True
                                                L += 1
                                        else:
                                            if flipflop == True:
                                                #print(la[0,1],la[1,1],"FLIP")
                                                print("L"+str(L),la[1, 1], la[0, 1],2)
                                                flipflop = False
                                                L += 1
                                            else:
                                                print("L"+str(L),la[1,1],la[0,1],"FLOP")
                                                flipflop = True
                                                L += 1



                                if "R" in pdf:
                                    #print(pa)
                                    la = list(netgraph.edges(p))
                                    la = np.asarray(la)
                                    if disjoint_detected_node is not None:
                                        if flipflop == True:
                                            flipflop = False
                                        else:
                                            #print(disjoint_detected_node, "dj node FLOP")
                                            flipflop = True
                                    else:
                                        if flipflop == True:
                                            print("R"+str(R),la[1,1],la[0,1],2)
                                            R += 1
                                            flipflop = False

                                        else:
                                            print("R"+str(R),la[0,1],la[1,1],2)
                                            R += 1
                                            flipflop = True




                except Exception as e:
                    #print(e)
                    continue




    return


def path_to_terminal(node,terminal_nodes,netgraph,nodes):
    
    length = 0
    path = []
    checked = []
    nodes_to_be_added = []
    latest = []
    #print("finding shortest path... length reset to :" ,length, " for node ", node)


    for term in terminal_nodes:
        #print("Terminal to which the path is being calculated: ",term, "from node" , node)
        shortest_path = networkx.algorithms.shortest_paths.generic.shortest_path(netgraph,source = term[1],target = node)
        #print("shortest path: ", shortest_path)
        current_len = len(shortest_path)

        if current_len >= length and length != 0:
            continue
        if length == 0:
            length = current_len
        
            

        for path_node in shortest_path:
            
            node_info = nodes[int(path_node)]
            for key in node_info:
                if "branch_node" in key:
                    #determine if it is a resistor or inductor
                    port = node_info[key]
                    process_info = port.__repr__()
                    process = node_info['process_polygon'].layer.process.symbol
                    if 'M' in process:
                        #print(process,path_node, term, node," this is an inductor")
                        latest = (["JJ",path_node,node,200])
                       
                    if 'R' in process:
                        print(process, path_node,term, node, " this is a resistor")

    nodes_to_be_added.append(latest)

    return nodes_to_be_added
