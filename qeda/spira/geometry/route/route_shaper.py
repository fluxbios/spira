import spira
import gdspy
import numpy as np
from core import param
from spira import shapes
from spira import pc
from numpy.linalg import norm
from numpy import sqrt, pi, cos, sin, log, exp, sinh, mod


RDD = spira.get_rule_deck()


class __RouteSimple__(shapes.Shape):
    """ Interface class for shaping route patterns. """

    m1 = param.DataField(fdef_name='create_midpoint1')
    m2 = param.DataField(fdef_name='create_midpoint2')

    w1 = param.DataField(fdef_name='create_width1')
    w2 = param.DataField(fdef_name='create_width2')

    o1 = param.DataField(fdef_name='create_orientation1')
    o2 = param.DataField(fdef_name='create_orientation2')

    def create_midpoint1(self):
        pass

    def create_midpoint2(self):
        pass

    def create_width1(self):
        pass

    def create_width2(self):
        pass

    def create_orientation1(self):
        pass

    def create_orientation2(self):
        pass


class RouteArcShape(__RouteSimple__):

    radius = param.NumberField(default=5*1e6)
    width = param.NumberField(default=1*1e6)
    theta = param.NumberField(default=45)
    start_angle = param.NumberField(default=0)
    angle_resolution = param.NumberField(default=15)
    angle1 = param.DataField(fdef_name='create_angle1')
    angle2 = param.DataField(fdef_name='create_angle2')

    def create_midpoint1(self):
        x = np.cos(self.angle1)
        y = np.sin(self.angle1)
        midpoint = [self.radius*x, self.radius*y]
        return midpoint

    def create_midpoint2(self):
        x = np.cos(self.angle2)
        y = np.sin(self.angle2)
        midpoint = [self.radius*x, self.radius*y]
        return midpoint

    def create_width1(self):
        return self.width

    def create_width2(self):
        return self.width

    def create_orientation1(self):
        return self.start_angle - 0 + 180*(self.theta<0)

    def create_orientation2(self):
        return self.start_angle + self.theta + 180 - 180*(self.theta<0)

    def create_angle1(self):
        angle1 = (self.start_angle + 0) * np.pi/180
        return angle1

    def create_angle2(self):
        angle2 = (self.start_angle + self.theta + 0) * np.pi/180
        return angle2

    def create_points(self, points):

        inner_radius = self.radius - self.width/2.0
        outer_radius = self.radius + self.width/2.0
        z = int(np.ceil(abs(self.theta) / self.angle_resolution))
        t = np.linspace(self.angle1, self.angle2, z)

        inner_points_x = (inner_radius*np.cos(t)).tolist()
        inner_points_y = (inner_radius*np.sin(t)).tolist()
        outer_points_x = (outer_radius*np.cos(t)).tolist()
        outer_points_y = (outer_radius*np.sin(t)).tolist()
        xpts = np.array(inner_points_x + outer_points_x[::-1])
        ypts = np.array(inner_points_y + outer_points_y[::-1])

        points = [[list(p) for p in list(zip(xpts, ypts))]]

        return points


class RouteSquareShape(__RouteSimple__):

    gds_layer = param.LayerField(name='ArcLayer', number=91)
    radius = param.NumberField(default=5*1e6)
    width = param.NumberField(default=1*1e6)
    size = param.MidPointField(default=(3*1e6,3*1e6))

    def create_midpoint1(self):
        return [-self.size[0], 0]

    def create_midpoint2(self):
        return [0, self.size[1]]
    
    def create_width1(self):
        return self.width

    def create_width2(self):
        return self.width

    def create_orientation1(self):
        return 90

    def create_orientation2(self):
        return 0

    def create_points(self, points):
        w = self.width/2
        s1, s2 = self.size
        pts = [[w,-w], [-s1,-w], [-s1,w], [-w,w], [-w,s2], [w,s2]]
        points = np.array([pts])
        return points


class RouteSimple(__RouteSimple__):

    port1 = param.DataField()
    port2 = param.DataField()

    num_path_pts = param.IntegerField(default=99)

    path_type = param.StringField(default='sine')
    width_type = param.StringField(default='straight')
    width_input = param.NumberField(allow_none=True, default=None)
    width_output = param.NumberField(allow_none=True, default=None)

    x_dist = param.FloatField()
    y_dist = param.FloatField()

    def create_midpoint1(self):
        return (0,0)

    def create_midpoint2(self):
        return [self.x_dist, self.y_dist]

    def create_width1(self):
        return self.width_input

    def create_width2(self):
        return self.width_output

    def create_orientation1(self):
        return -90
        # return 180

    def create_orientation2(self):
        return 90
        # return 0

    def create_points(self, points):

        point_a = np.array(self.port1.midpoint)
        if self.width_input is None:
            self.width_input = self.port1.width
        point_b = np.array(self.port2.midpoint)
        if self.width_output is None:
            self.width_output = self.port2.width

        if round(abs(mod(self.port1.orientation - self.port2.orientation, 360)), 3) != 180:
            raise ValueError('Ports do not face eachother.')
        orientation = self.port1.orientation - 90

        separation = point_b - point_a
        distance = norm(separation)
        rotation = np.arctan2(separation[1], separation[0]) * 180/pi
        angle = rotation - orientation
        forward_distance = distance*cos(angle*pi/180)
        lateral_distance = distance*sin(angle*pi/180)

        xf = forward_distance
        yf = lateral_distance

        self.x_dist = xf
        self.y_dist = yf

        if self.path_type == 'straight':
            curve_fun = lambda t: [xf*t, yf*t]
            curve_deriv_fun = lambda t: [xf + t*0, 0 + t*0]
        if self.path_type == 'sine':
            curve_fun = lambda t: [xf*t, yf*(1-cos(t*pi))/2]
            curve_deriv_fun = lambda t: [xf + t*0, yf*(sin(t*pi)*pi)/2]

        if self.width_type == 'straight':
            width_fun = lambda t: (self.width_output - self.width_input)*t + self.width_input
        if self.width_type == 'sine':
            width_fun = lambda t: (self.width_output - self.width_input)*(1-cos(t*pi))/2 + self.width_input

        route_path = gdspy.Path(width=self.width_input, initial_point=(0,0))
        route_path.parametric(
            curve_fun, curve_deriv_fun,
            number_of_evaluations=self.num_path_pts,
            max_points=199,
            final_width=width_fun,
            final_distance=None
        )
        points = route_path.polygons
        return points


class RoutePointShape(__RouteSimple__):

    width = param.FloatField(default=1*1e8)
    angles = param.DataField(fdef_name='create_angles')

    def get_path(self):
        try:
            return self.__path__
        except:
            raise ValueError('Path not set for {}'.format(self.__class__.__name__))

    def set_path(self, value):
        self.__path__ = np.asarray(value)
    
    path = param.FunctionField(get_path, set_path)

    def create_midpoint1(self):
        return self.path[0]

    def create_midpoint2(self):
        return self.path[-1]

    def create_width1(self):
        return self.width

    def create_width2(self):
        return self.width

    def create_orientation1(self):
        return self.angles[0]*180/pi+90

    def create_orientation2(self):
        return self.angles[-1]*180/pi-90

    def create_angles(self):
        dxdy = self.path[1:] - self.path[:-1]
        angles = (np.arctan2(dxdy[:,1], dxdy[:,0])).tolist()
        angles = np.array([angles[0]] + angles + [angles[-1]])
        return angles

    def create_points(self, points):
        diff_angles = (self.angles[1:] - self.angles[:-1])
        mean_angles = (self.angles[1:] + self.angles[:-1])/2
        dx = self.width/2*np.cos((mean_angles - pi/2))/np.cos((diff_angles/2))
        dy = self.width/2*np.sin((mean_angles - pi/2))/np.cos((diff_angles/2))
        left_points = self.path.T - np.array([dx,dy])
        right_points = self.path.T + np.array([dx,dy])
        all_points = np.concatenate([left_points.T, right_points.T[::-1]])
        points = np.array([all_points])
        return points


class RouteGeneral(spira.Cell):

    route_shape = param.ShapeField(doc='Shape of the routing polygon.')
    connect_layer = param.PhysicalLayerField(default=RDD.DEF.PDEFAULT)

    port_input = param.DataField(fdef_name='create_port_input')
    port_output = param.DataField(fdef_name='create_port_output')

    gds_layer = param.DataField(fdef_name='create_gds_layer')

    def create_gds_layer(self):
        ll = spira.Layer(
            number=self.connect_layer.layer.number,
            datatype=RDD.PURPOSE.TERM.datatype
        )
        return ll

    def create_port_input(self):
        term = spira.Term(name='P1',
            midpoint=self.route_shape.m1,
            width=self.route_shape.w1,
            orientation=self.route_shape.o1,
            gds_layer=self.gds_layer
        )
        return term

    def create_port_output(self):
        term = spira.Term(name='P2',
            midpoint=self.route_shape.m2,
            width=self.route_shape.w2,
            orientation=self.route_shape.o2,
            gds_layer=self.gds_layer
        )
        return term

    def create_elementals(self, elems):
        poly = pc.Polygon(
            points=self.route_shape.points, 
            ps_layer=self.connect_layer, 
            enable_edges=False
        )
        elems += poly
        return elems

    def create_ports(self, ports):
        ports += [self.port_input, self.port_output]
        return ports


if __name__ == '__main__':
    p1 = spira.Term(midpoint=(0,0), orientation=-90)
    p2 = spira.Term(midpoint=(30*1e6,20*1e6), orientation=90)
    rs = RouteSimple(port1=p1, port2=p2, path_type='straight')
    pp = spira.Polygon(shape=rs)
    pp.rotate(angle=180)
    cell = spira.Cell()
    cell += pp
    cell += [p1, p2]
    cell.output()
    