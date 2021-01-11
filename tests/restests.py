import spira.all as spira
from spira.technologies.mit.process.database import RDD
from spira.technologies.mit import devices as dev

class JTL(spira.PCell):
    p1 = spira.Parameter(fdef_name = "create_p1")
    p2 = spira.Parameter(fdef_name = "create_p2")
    jj1 = spira.Parameter(fdef_name ='create_jjs200')
    jj2 = spira.Parameter(fdef_name = 'create_jjs201')
    con = spira.Parameter(fdef_name = "create_connection")
    r5m6 = spira.Parameter(fdef_name = "create_r5m6con")
    

    def create_p1(self):
        return spira.Port(name='M6:T1', midpoint = (-11,-1.5), orientation=0, width=1)

    def create_p2(self):
        return spira.Port(name = 'M6:T2',midpoint = (11,-1.5),orientation = 180, width = 1)
    def create_r5m6con(self):
        con = R5M6con()
        T = spira.Rotation(270)
        return spira.SRef(con,midpoint = (0,5.255+0.7),transformation = T)


    def create_connection(self):
        con = Jjcon()
        return spira.SRef(con,midpoint= (0,-0.225),transformation=None)

    def create_jjs201(self):
        jj = jjs200()
        T = spira.Rotation(180)
        return spira.SRef(jj, midpoint=(-4.5,-5),transformation=T)
    def create_jjs200(self):
        jj = jjs200()
        T = spira.Rotation(180)
        return spira.SRef(jj, midpoint=(4.5,-5),transformation=T)


    def create_elements(self,elems):
        #add inductor on m6
        #add the 2 jjs
        elems += self.jj1#right jj
        elems += self.jj2#left jj
        elems += self.con
        elems += self.r5m6
        #top resistor of jtk
        elems += spira.Box(layer = spira.RDD.PLAYER.R5.METAL,width= 1, height=3.7,center=(0,(6.5+0.6)))
        elems += spira.RouteManhattan(ports=[self.jj2.ports['M6:P3_M6'],self.p1],layer = spira.RDD.PLAYER.M6.METAL,width= 1)
        elems += spira.RouteManhattan(ports =[self.jj1.ports['M6:P1_M6'],self.p2],layer = spira.RDD.PLAYER.M6.METAL,width = 1)
        
        return elems



    def create_ports(self,ports):
        ports += [self.p1,self.p2]
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


class Jjcon(spira.Device):

    distance = spira.NumberParameter(restriction=spira.RestrictRange(lower = spira.RDD.M6.MIN_SIZE, upper= spira.RDD.M6.MAX_WIDTH))
    l1 = spira.Parameter(fdef_name = "create_leftleg")
    l2 = spira.Parameter(fdef_name = "create_rightleg")
    p1 = spira.Parameter(fdef_name = "create_p1")

    def create_leftleg(self):
        return spira.Rectangle(layer = spira.RDD.PLAYER.M6.METAL,p1 = (-4,0.5),p2 = (-5,-4))

    def create_rightleg(self):
        return spira.Rectangle(layer = spira.RDD.PLAYER.M6.METAL,p1 = (4,0.5), p2 = (5,-4))
    
    def create_elements(self,elems):
        shape = spira.Shape(points=[(-3.925	,22.775),(-3.925	,17.150),(-2.875	,17.150),(-2.875	,21.775),(2.875	,21.775),(2.875	,17.150),(3.925	,17.150),(3.925	,22.775),(0.500	,22.775),(0.500	,26.775),(-0.500,26.775),(-0.500 ,22.775),(-3.925 ,22.775)])
        #elems += spira.Polygon(shape = shape, layer = spira.RDD.PLAYER.M6.METAL)
        elems += spira.Rectangle(layer = spira.RDD.PLAYER.M6.METAL,p1 = (-4,0.5),p2 = (-5,-4))
        elems += spira.Rectangle(layer = spira.RDD.PLAYER.M6.METAL,p1 = (4,0.5), p2 = (5,-4))
        elems += spira.Rectangle(layer = spira.RDD.PLAYER.M6.METAL,p1 = (-4,0.5),p2= (4, -0.5))
        elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL, width= 1, height= 5, center= (0,3))
        return elems

    def create_ports(self,ports):
        ports += spira.Port(name = "P1_M6",midpoint = (0,5.5),process = spira.RDD.PROCESS.M6,orientation = 90, width = 1)
        return ports

class R5M6con(spira.Device):

    def create_elements(self,elems):
        elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL,width= 1.4,height= 2.1,center=(0.35,0))
        elems += spira.Box(layer = spira.RDD.PLAYER.C5R.VIA, width= 0.7, height= 1.1,center=(0.35,0))
        elems += spira.Box(layer = spira.RDD.PLAYER.R5.METAL, width= 1, height= 1, center= (0.5,0))
        return elems





D = JTL()
D.gdsii_output("tests/jtl")
#D = jjs200()
#D.gdsii_output("tests/jjs")
#j = Jjcon()
#j.gdsii_output("tests/jjcon")

#D = R5M6con()
#D.gdsii_output("tests/rmcon")