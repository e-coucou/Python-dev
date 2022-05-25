from lib2to3.pgen2.token import LEFTSHIFT
from tkinter import CENTER, TOP
from manim import *
from numpy import place
from scipy.fftpack import shift


class Network(Scene):
    def construct(self):
        ech=0.5
        ci = Circle(1, color=BLUE, stroke_width=1).scale(ech*1.15)
        ent = MathTex("W_{i} b_{i}").scale(ech).align_to(ci,LEFT)
        ent.add_updater( lambda x: x.move_to(ci,[-1,0,0]).shift([0.07,0,0]))
        sor = MathTex("A_{i}").move_to(RIGHT).scale(ech)
        sor.add_updater( lambda x: x.move_to(ci,[1,0,0]).shift([-0.1,0,0]))
        li = always_redraw(lambda : Line(start=ci.get_top(),end=ci.get_bottom(),color=BLUE,stroke_width=1))

        self.play(Create(VGroup(ci,ent,sor,li)))
        self.wait()
        self.play(ci.animate.shift(RIGHT+2),run_time=4)