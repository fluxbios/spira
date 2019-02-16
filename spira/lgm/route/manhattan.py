import spira
import numpy as np
from spira import param
from spira.lgm.route.arc_bend import ArcRoute, Arc, Rect, RectRoute, RectRouteTwo
from spira.lgm.route.basic import RouteShape
from spira.lgm.route.basic import RouteBasic


class __Manhattan__(spira.Cell):

    port1 = param.PortField()
    port2 = param.PortField()

    length = param.FloatField(default=20*1e6)
    gdslayer = param.LayerField(number=13)
    radius = param.IntegerField(default=1*1e6)
    bend_type = param.StringField(default='circular')

    b1 = param.DataField(fdef_name='create_arc_bend_1')
    b2 = param.DataField(fdef_name='create_arc_bend_2')

    p1 = param.DataField(fdef_name='create_port1_position')
    p2 = param.DataField(fdef_name='create_port2_position')

    quadrant_one = param.DataField(fdef_name='create_quadrant_one')
    quadrant_two = param.DataField(fdef_name='create_quadrant_two')
    quadrant_three = param.DataField(fdef_name='create_quadrant_three')
    quadrant_four = param.DataField(fdef_name='create_quadrant_four')

    def _generate_route(self, p1, p2):
        route = RouteShape(
            port1=p1, port2=p2,
            path_type='straight',
            width_type='straight'
        )
        R1 = RouteBasic(route=route, connect_layer=self.gdslayer)
        r1 = spira.SRef(R1)
        r1.rotate(angle=p2.orientation-180, center=R1.port1.midpoint)
        r1.move(midpoint=(0,0), destination=p1.midpoint)
        return r1

    def create_port1_position(self):

        angle = np.mod(self.port1.orientation, 360)

        p1 = [self.port1.midpoint[0], self.port1.midpoint[1]]
        if angle == 90:
            p1 = [self.port1.midpoint[1], -self.port1.midpoint[0]]
        if angle == 180:
            p1 = [-self.port1.midpoint[0], -self.port1.midpoint[1]]
        if angle == 270:
            p1 = [-self.port1.midpoint[1], self.port1.midpoint[0]]

        # p1 = [self.port1.midpoint[0], self.port1.midpoint[1]]
        # if self.port1.orientation == 90:
        #     p1 = [self.port1.midpoint[1], -self.port1.midpoint[0]]
        # if self.port1.orientation == 180:
        #     p1 = [-self.port1.midpoint[0], -self.port1.midpoint[1]]
        # if self.port1.orientation == 270:
        #     p1 = [-self.port1.midpoint[1], self.port1.midpoint[0]]

        return p1

    def create_port2_position(self):

        angle = np.mod(self.port1.orientation, 360)

        p2 = [self.port2.midpoint[0], self.port2.midpoint[1]]
        if angle == 90:
            p2 = [self.port2.midpoint[1], -self.port2.midpoint[0]]
        if angle == 180:
            p2 = [-self.port2.midpoint[0], -self.port2.midpoint[1]]
        if angle == 270:
            p2 = [-self.port2.midpoint[1], self.port2.midpoint[0]]

        # p2 = [self.port2.midpoint[0], self.port2.midpoint[1]]
        # if self.port1.orientation == 90:
        #     p2 = [self.port2.midpoint[1], -self.port2.midpoint[0]]
        # if self.port1.orientation == 180:
        #     p2 = [-self.port2.midpoint[0], -self.port2.midpoint[1]]
        # if self.port1.orientation == 270:
        #     p2 = [-self.port2.midpoint[1], self.port2.midpoint[0]]

        return p2

    def create_arc_bend_1(self):
        if self.bend_type == 'circular':
            # B1 = Rect(shape=RectRoute(
            #         width=self.port1.width,
            #         gdslayer=self.gdslayer,
            #     )
            # )
            # return spira.SRef(B1)

            B1 = Arc(shape=ArcRoute(
                radius=self.radius,
                width=self.port1.width,
                gdslayer=self.gdslayer,
                start_angle=0, theta=90)
            )
            return spira.SRef(B1)

    def create_arc_bend_2(self):
        if self.bend_type == 'circular':
            # B2 = Rect(shape=RectRouteTwo(
            #         width=self.port1.width,
            #         gdslayer=self.gdslayer,
            #     )
            # )
            # return spira.SRef(B2)

            B2 = Arc(shape=ArcRoute(
                radius=self.radius,
                width=self.port1.width,
                gdslayer=self.gdslayer,
                start_angle=0, theta=-90)
            )
            return spira.SRef(B2)











