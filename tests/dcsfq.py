import spira.all as spira
from spira.technologies.mit.process.database import RDD
from spira.technologies.mit import devices as dev

class Dcsfq(spira.PCell):
    print("Creating instances of required devices")
    jj1 = spira.Parameter(fdef_name ='create_jj1')
    jj2 = spira.Parameter(fdef_name = "create_jj2")
    jj3 = spira.Parameter(fdef_name = 'create_jj3')
    conjjs = spira.Parameter(fdef_name = "create_jjcon12")
    viam5m6 = spira.Parameter(fdef_name = "create_viam5m61")
    box1 = spira.Parameter(fdef_name = "create_box")
    p1 = spira.Parameter(fdef_name = "create_p1")
    p2 = spira.Parameter(fdef_name ='create_p2')
    u1 = spira.Parameter(fdef_name = "create_u1")
    conport = spira.Parameter(fdef_name = "create_conport")
    #this is VERYYYY redundant and done merely to demonstrate - will be done with 1 via class, accepting midpoint and transform as param
    via1 = spira.Parameter(fdef_name  = 'create_r5m6via1')
    via2 = spira.Parameter(fdef_name  = 'create_r5m6via2')
    via3 = spira.Parameter(fdef_name = 'create_r5m6via3')
    via4 = spira.Parameter(fdef_name = 'create_r5m6via4')

    def create_r5m6via1(self):
        via = R5M6con()
        T = spira.Rotation(270)
        x,y = midpoint = (self.jj3.ports["M6:P2_M6"].midpoint)
        return spira.SRef(via, midpoint = (x,y+4.4),transformation = T)

    def create_r5m6via2(self):
        via = R5M6con()
        T = spira.Rotation(270)
        x,y = midpoint = (self.via1.midpoint)
        return spira.SRef(via, midpoint = (x,y+8),transformation = T)
    
    def create_r5m6via3(self):
        via = R5M6con()
        T = spira.Rotation(270)
        x,y = self.jj2.ports['M6:P2_M6'].midpoint
        return spira.SRef(via,midpoint = (x+6.2,y+6.1),transformation = T)
    
    def create_r5m6via4(self):
        via = R5M6con()
        T = spira.Rotation(270)
        x,y = self.via3.ports['R5:E1'].midpoint
        return spira.SRef(via,midpoint = (x,y+6.3),transformation = T)

    def create_p1(self):
        return spira.Port(name = "P1", process = spira.RDD.PROCESS.M6, midpoint = (-12.15,0),width = 1.3,orientation = 180)
    
    def create_p2(self):
        return spira.Port(name = "P2", process =spira.RDD.PROCESS.M6, midpoint = ((self.jj3.ports['M6:P1_M6'].midpoint[0]+5.8,self.jj3.ports['M6:P1_M6'].midpoint[1])),width = 1)
    
    def create_conport(self):
        return spira.Port(name = "P3",process = spira.RDD.PROCESS.M6, midpoint =((self.jj3.ports['M6:P1_M6'].midpoint[0]+3.8-0.225,self.jj3.ports['M6:P1_M6'].midpoint[1])) , width = 1, orientation = 180)
    #right jj
    def create_jj1(self):
        jj = jjs200()
        T = spira.Rotation(180)
        return spira.SRef(jj, midpoint=(3.25,0),transformation=T)
    #left jj
    def create_jj2(self):
        jj = jjs200()
        T = spira.Rotation(180)
        return spira.SRef(jj, midpoint=(-3.25,0),transformation=T)

    def create_jjcon12(self):
        return spira.RouteStraight(p1 =self.jj1.ports['M6:P3_M6'],p2 = self.jj2.ports['M6:P1_M6'] ,layer = spira.RDD.PLAYER.M6.METAL)

    def create_jj3(self):
        jj = jjs200()
        T = spira.Rotation(180)
        return spira.SRef(jj,midpoint = (self.u1.ports['M6:E1'].midpoint[0]+1,self.u1.ports['M6:E1'].midpoint[1]-0.4),transformation=T)

    def create_viam5m61(self):
        via = m5m6via()
        return spira.SRef(via,midpoint = (-7.15,0))
    def create_box(self):
        b = boxdevice()
        return spira.SRef(b, midpoint =(-5.35,0))

    def create_u1(self):
        u = u_inductor()
        x,y = (self.jj1.ports['M6:P1_M6'].midpoint)
        return spira.SRef(u, midpoint = (x+3,y-4.2))

    def create_elements(self,elems):
       print("Adding elements to layout and routing")
       elems += [self.jj1,self.jj2]
       elems += self.conjjs
       elems += self.viam5m6
       elems += self.box1
       elems += spira.RouteStraight(p1 = self.box1.ports['M5:E1'],p2 = self.viam5m6.ports['M5:E3'],layer = spira.RDD.PLAYER.M5.METAL)
       x,y = self.viam5m6.ports["M6:E1"].midpoint[0], self.viam5m6.ports["M6:E1"].midpoint[1]
       elems += spira.Wedge(alias="M6",layer = spira.RDD.PLAYER.M6.METAL,transformation=spira.Rotation(180),begin_width=(1.4),end_width=(1), end_coord=(8.05,0),begin_coord=(-x,0))     
       elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL,width=4.1,height=1,center=(elems["M6"].center[0]-2.1,0))
       elems += self.u1
       elems += self.jj3
       elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL, width=3.2,height=2.15,center= (self.jj3.ports['M6:P1_M6'].midpoint[0]+1.6-0.255,self.jj3.ports['M6:P1_M6'].midpoint[1]))
       elems += spira.Wedge(layer = spira.RDD.PLAYER.M6.METAL,begin_coord=(self.jj3.ports['M6:P1_M6'].midpoint[0]+3.2-0.275,self.jj3.ports['M6:P1_M6'].midpoint[1]),end_coord=(self.jj3.ports['M6:P1_M6'].midpoint[0]+3.8-0.275,self.jj3.ports['M6:P1_M6'].midpoint[1]),begin_width=2.15,end_width=1)
       elems += spira.RouteStraight(p1 = self.conport,p2 = self.p2,layer = spira.RDD.PLAYER.M6.METAL)
       elems += self.via1
       elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL,width= 1.5,height= 3.95,center= (self.jj3.ports['M6:P2_M6'].midpoint[0],self.jj3.ports['M6:P2_M6'].midpoint[1]+1.7))
       elems += self.via2
       elems += spira.RouteStraight(p1 = self.via1.ports['R5:E1'],p2 = self.via2.ports['R5:E3'],layer = spira.RDD.PLAYER.R5.METAL)
       elems += self.via3
       elems += spira.RouteManhattan(ports = [self.jj2.ports['M6:P2_M6'],self.via3.ports['M6:E3']],layer = spira.RDD.PLAYER.M6.METAL,width=1.6)
       elems += self.via4
       elems += spira.RouteStraight(p1 = self.via3.ports['R5:E1'],p2 = self.via4.ports['R5:E3'],layer = spira.RDD.PLAYER.R5.METAL)
       elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL, width = 2, height=6.6,center=(self.via4.ports['M6:E1'].midpoint[0],self.via4.ports['M6:E1'].midpoint[1]+3.3))
       elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL,width = 10, height=1.5,center=(self.via4.ports['M6:E1'].midpoint[0]+4.7,self.via4.ports['M6:E1'].midpoint[1]+1.8))
       elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL,width=2, height=2.3,center=(self.via2.ports['M6:E1'].midpoint[0],self.via2.ports['M6:E1'].midpoint[1]+1.1))
       #ground connection
       elems += spira.Box(layer = spira.RDD.PLAYER.R5.METAL,width=1.3,height=7.2,center=(self.viam5m6.ports['M5:E0'].midpoint[0],self.viam5m6.ports['M5:E1'].midpoint[1]+(7.2/2+0.8)))
       elems += spira.Box(layer = spira.RDD.PLAYER.R5.METAL, width = 2.4,height=1.3, center=(self.viam5m6.ports['M5:E0'].midpoint[0]-1.8,self.viam5m6.ports['M5:E0'].midpoint[1]+(6.5)))
       elems += spira.Box(layer = spira.RDD.PLAYER.R5.METAL,width=  1.3,height=3.2,center=(self.viam5m6.ports['M5:E0'].midpoint[0]-2.35,self.viam5m6.ports['M5:E0'].midpoint[1]+(8.7)))
       elems += spira.Box(layer = spira.RDD.PLAYER.R5.METAL,width=8.4,height=1.3, center=(self.viam5m6.ports['M5:E0'].midpoint[0]+1.2,self.viam5m6.ports['M5:E0'].midpoint[1]+(10.95)))
       elems += spira.Box(layer = spira.RDD.PLAYER.I4.VIA,width=0.8,height=0.8,center=(-2.5,11.8))
       return elems

    

    def create_ports(self,ports):
        print("Adding to ports to layout")
        ports += self.p1
        ports += self.p2
        ports += self.conport
        print("Writing GDSII output")
        return ports
    

class jjs200(spira.Device):

    width = spira.NumberParameter(default = spira.NUMBER(7.75))#hight
    length = spira.NumberParameter(default = spira.NUMBER(2.65))
    def create_elements(self,elems):
        elems += spira.Rectangle(alias = "M5",p1 = (-1.325,-1.325),p2=(1.325,6.425),layer = spira.RDD.PLAYER.M5.METAL)
        elems += spira.Rectangle(p1 = (-1.175,-1.175),p2 = (1.175,2.625), layer = spira.RDD.PLAYER.M6.METAL)
        elems += spira.Rectangle(p1 = (-0.95,3.325), p2 = (0.95,6.275), layer = spira.RDD.PLAYER.M6.METAL)
        elems += spira.Rectangle(p1 = (-0.35,5.225), p2 = (0.35,5.925), layer = spira.RDD.PLAYER.I5.VIA)
        elems += spira.Rectangle(p1 = (-0.45,3.675), p2 = (0.45,4.38), layer = spira.RDD.PLAYER.C5R.VIA)
        elems += spira.Rectangle(p1 = (-0.4,1.275),p2 = (0.4,4.675),layer = spira.RDD.PLAYER.R5.METAL)
        elems += spira.Rectangle(p1 = (-0.45,1.575),p2 = (0.45,2.275),layer = spira.RDD.PLAYER.C5R.VIA)
        elems += spira.Circle(box_size=(0.718*2,0.718*2),center = (0,0), layer = spira.RDD.PLAYER.C5J.VIA)
        elems += spira.Circle(box_size = (0.82*2,0.82*2),center = (0,0), layer = spira.RDD.PLAYER.J5.JUNCTION)
        return elems

    def create_ports(self,ports):
        ports += spira.Port(name = "P1_M6", midpoint = (-1.175,0),process = spira.RDD.PROCESS.M6,orientation = 180, width = 1.6875)
        ports += spira.Port(name = "P2_M6", midpoint = (0,-1.175), process = spira.RDD.PROCESS.M6, orientation = 270,width = 1.6875)
        ports += spira.Port(name = "P3_M6", midpoint = (1.175,0), process = spira.RDD.PROCESS.M6, orientation = 0,width = 1.6875)
        return ports

class boxdevice(spira.Device):
    def create_elements(self,elems):
        elems +=spira.Box(center = (0,0), layer = spira.RDD.PLAYER.M5.METAL,height=1.6,width=1.6)
        return elems
class m5m6via(spira.Device):
    def create_elements(self,elems):
        elems += spira.Box(layer = spira.RDD.PLAYER.M5.METAL,width = 1.7, height= 1.7)
        elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL, width= 1.4, height= 1.4)
        elems += spira.Box(layer = spira.RDD.PLAYER.I5.VIA, width= 0.7, height= 0.7)
        return elems

class u_inductor(spira.Device):
    def create_elements(self,elems):
        elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL,width = 3.35,height=1,center=(0,0))
        elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL,width=1,height=4.625,center = (-1.3+0.125,2.8125))
        elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL,width=(1.52),height= 1, center= ((-2.5+0.065),4.625))
        elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL,width=1,height=4.625,center = (+1.3-0.125,2.8125))
        elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL,width=(1.52),height= 1, center= ((+2.5-0.065),4.625))
    
        return elems

class R5M6con(spira.Device):

    def create_elements(self,elems):
        elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL,width= 1.4,height= 2.1,center=(0.35,0))
        elems += spira.Box(layer = spira.RDD.PLAYER.C5R.VIA, width= 0.7, height= 1.1,center=(0.35,0))
        elems += spira.Box(layer = spira.RDD.PLAYER.R5.METAL, width= 1, height= 1, center= (0.5,0))
        return elems

F = RDD.FILTERS.OUTPUT.PORTS
F['cell_ports'] = False
F['edge_ports'] = False
F['contact_ports'] = False
F = RDD.FILTERS.PCELL.DEVICE
F['boolean'] = True
F['contact_attach'] = True
F = RDD.FILTERS.PCELL.CIRCUIT
F['boolean'] = False

D = Dcsfq()
D = RDD.FILTERS.PCELL.MASK(D)

D.gdsii_output('tests/dcsfq')
#D = u_inductor()
#D.gdsii_output('tests/uinductor')