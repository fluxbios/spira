import spira.all as spira
from spira.technologies.mit.process.database import RDD
from spira.technologies.mit import devices as dev



class jjs200(spira.Device):

    __name_prefix__ = 'JJ'

    length = spira.NumberParameter(default=1, doc='Length of the shunt resistance.')

    width = spira.NumberParameter(
        default=RDD.R5.MIN_SIZE,
        restriction=spira.RestrictRange(lower=RDD.R5.MIN_SIZE, upper=RDD.R5.MAX_WIDTH),
        doc='Width of the shunt resistance.')

    radius = spira.NumberParameter(
        default=RDD.J5.MIN_SIZE,
        restriction=spira.RestrictRange(lower=RDD.J5.MIN_SIZE, upper=RDD.J5.MAX_SIZE),
        doc='Radius of the circular junction layer.')
    def create_elements(self,elems):

        elems += spira.Circle(box_size=((self.radius-0.1)*2,(self.radius-0.1)*2),center = (0,0), layer = spira.RDD.PLAYER.C5J.VIA)
        elems += spira.Circle(box_size = (self.radius*2,self.radius*2),center = (0,0), layer = spira.RDD.PLAYER.J5.JUNCTION)
        elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL,width=2.35,height=3.8,center=(0,0.76))
        elems += spira.Box(layer = spira.RDD.PLAYER.C5R.VIA,width=self.width+0.1,height=0.7,center=(0,1.925))
        elems += spira.Box(layer = spira.RDD.PLAYER.R5.METAL,width=self.width,height=self.length,center=(0,1.275+(self.length/2)))
        elems += spira.Box(layer = spira.RDD.PLAYER.C5R.VIA,width=self.width+0.1,height=0.7,center=(0,(1.275+self.length-0.65)))
        elems += spira.Box(layer = spira.RDD.PLAYER.M6.METAL,width=2,height=3,center=(0,1.275+self.length))
        elems += spira.Box(layer = spira.RDD.PLAYER.M5.METAL,width=2.7,height=7.75,center=(0,1.275+(self.length/2)-0.5))
        return elems

    def create_ports(self,ports):

        return ports

D = jjs200(radius = 0.8,length = 3.5,width = 1)
D.gdsii_output('tests/circle')