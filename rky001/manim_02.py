from manim import *
from numpy import size, square

class Test(Scene):
    def construct(self):
        # bgt = Rectangle(height=5,width=2,stroke_color=GREEN,fill_opacity=0.25).set_color(BLUE).to_edge(LEFT)
        # xx = Rectangle(height=1.5,width=2,stroke_color=GREEN,fill_opacity=0.50).set_color(BLUE).to_edge(LEFT)
        # txt = Write(Text("Ceci est un petit message de e-Coucou",font_size=16).to_edge(DL))
        # self.play(Create(VGroup(bgt,xx)), run_time=3)
        # self.play(txt)
        # self.wait()

        plane = NumberPlane(x_range=[-4,4,2], x_length=4,y_range=[0,16,4],y_length=3).set_color(BLUE).to_edge(UL).add_coordinates()
        parab = plane.plot(lambda x: x**2, x_range = [-4,4], color = GREEN)

        labels = plane.get_axis_labels(x_label='x', y_label='f(x)')
        func_label = MathTex("f(x) = {x}^{2}").scale(0.6).next_to(parab,RIGHT,buff=0.3)


        self.play(DrawBorderThenFill(plane))
        self.play(Create(VGroup(parab,labels,func_label)))
        # self.wait()

        k = ValueTracker(-4)
        inc = ValueTracker(1)

        # x= k.get_value()
        x = 1
        y= x**2
        ci = Circle(0.2,fill_opacity=1).set_x(x).set_y(y)
        self.play(Create(ci))

        num = always_redraw( lambda:  DecimalNumber().set_value(k.get_value()))

        area = always_redraw(lambda : plane.get_riemann_rectangles(graph=parab, x_range=[-4,4], dx = inc.get_value(),stroke_width=0.1,stroke_color=BLUE))

        tan = always_redraw(lambda : plane.get_secant_slope_group(x=k.get_value(),dx=0.01, graph=parab,secant_line_color=RED,secant_line_length=3))

        pt = always_redraw( lambda : Dot().move_to(plane.c2p(k.get_value(), k.get_value()**2)) )

        self.play(FadeIn(num))
        # self.play(Create(VGroup(area,tan)))
        self.add(tan,pt)
        self.play( k.animate.set_value(4),run_time=2,rate_functions = linear)
        self.wait()
        self.play(Create(area))
        self.play( inc.animate.set_value(0.1),run_time=2,rate_functions = smooth)
        self.wait()
