# -*- coding: utf-8 -*-

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import copy

import re
import math
import numbers

_re_num = re.compile(r'[+-]?\d+(\.\d*)?')
_re_args = re.compile(r'[a-zA-Z] *([+-]?\d*(\.\d*)?[ ,]?)+')

SEMICIRCLE = (4/3)*math.tan(math.pi/8)

def arcMagicNumber(radian):
    return (4/3) * math.tan(radian/4)

def strToNum(str):
    m = re.fullmatch(_re_num, str)
    if m:
        if m.group(1):
            return float(m.group(0))
        else:
            return int(m.group(0))
    else:
        raise ValueError("Str Not number!")

class Point(object):
    def __init__(self, x=0, y=0) -> None:
        if isinstance(x, str):
            x = strToNum(x)
        if isinstance(y, str):
            y = strToNum(y)
        if isinstance(x, numbers.Real) and isinstance(y, numbers.Real):
            self._x = x
            self._y = y
        else:
            raise ValueError('Point Value must be numeric: {} and {}'.format(type(x), type(y)))

    def __add__(self, pos):
        return Point(self._x + pos.x, self._y + pos.y)

    def __sub__(self, pos):
        return Point(self._x - pos.x, self._y - pos.y)

    def __mul__(self, value):
        if isinstance(value, numbers.Real):
            return Point(self._x*value, self.y*value)
        else:
            raise ValueError('Value must be numeric!')

    def __truediv__(self, value):
        if isinstance(value, numbers.Real):
            return Point(self._x/value, self.y/value)
        else:
            raise ValueError('Value must be numeric!')

    def __neg__(self):
        return Point(-self.x, -self.y)
    
    def print(self, f=3):
        return print('({}, {})'.format(round(self.x, f), round(self.y, f)))

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, value):
        if isinstance(value, numbers.Real):
            self._x = value
        else:
            raise ValueError('X value must be numeric!')

    @y.setter
    def y(self, value):
        if isinstance(value, numbers.Real):
            self._y = value
        else:
            raise ValueError('Y value must be numeric!')

    def isOrigin(self):
        return not (self._x or self._y)

    def normalization(self, len=1):
        if self.isOrigin():
            return None
        return self / math.sqrt(math.pow(self._x, 2) + math.pow(self._y, 2)) * len

    def perpendicular(self, pos=None):
        if not pos : pos = Point()
        v = self - pos
        return Point(v.y, -v.x)

    def radian(self, pos=None):
        if not pos : pos = Point()
        v = (self - pos).normalization()
        if v.y < 0:
            return -math.acos(v.x)
        else:
            return math.acos(v.x)

    def rotate(self, radian, center=None):
        if not center : center = Point()
        v = self - center
        cos = math.cos(radian)
        sin = math.sin(radian)
        return Point(v.x*cos - v.y*sin, v.x*sin + v.y*cos) + center

    def mirror(self, center=None):
        if not center : center = Point()
        return center - self

    def distance(self, pos=None):
        if not pos : pos = Point()
        v = pos - self
        return math.sqrt(v.x**2 + v.y**2)

    def distanceOffset(self, pos=None, value=0):
        if not pos : pos = Point()
        v = pos - self
        
        return (v.x**2 + v.y**2) < value**2

    def scale(self, value, pos=None):
        if not pos : pos = Point()
        return ((self-pos) * value) + pos

    def dotProduct(self, pos):
        return self.x*pos.x + self.y*pos.y

class Rect(object):
    def __init__(self, lbPos:Point=Point(), rtPos:Point=Point()):
        self._lb = lbPos
        self._rt = rtPos

    @property
    def leftBottom(self):
        return self._lb
        
    @property
    def rightTop(self):
        return self._rt

    @property
    def left(self):
        return self._lb.x

    @left.setter
    def left(self, left):
        self._lb.x = left

    @property
    def top(self):
        return self._rt.y

    @top.setter
    def top(self, top):
        self._rt.y = top

    @property
    def right(self):
        return self._rt.x
    
    @right.setter
    def right(self, right):
        self._rt.x = right

    @property
    def bottom(self):
        return self._lb.y

    @bottom.setter
    def bottom(self, bottom):
        self._lb.y = bottom

    @property
    def width(self):
        return self._rt.x - self._lb.x
    
    @width.setter
    def width(self, width):
        self.right = self.left + width

    @property
    def height(self):
        return self._rt.y - self._lb.y

    @height.setter
    def height(self, height):
        self.top = self.bottom + height

    def intersects(self, rect, offset=0):
        return rect.right-self.left > offset and self.right-rect.left > offset and self.top-rect.bottom > offset and rect.top-self.bottom > offset

    def contains(self, rect, offset=0):
        return rect.left-self.left > offset and rect.bottom-self.bottom > offset and self.right-rect.right > offset and self.top-rect.top > offset

    def center(self):
        return Point((self.left+self.right) / 2, (self.bottom+self.top) / 2)

    def area(self):
        return self.width * self.height

def intersection(ps1, pe1, ps2, pe2, offset=0.002):
    def lineareQuation(p1, p2):
        A = p2.y - p1.y
        B = p1.x - p2.x
        if A or B:
            C = -(p1.x*A + p1.y*B)
            return [A, B, C]
        else:
            return None

    A1, B1, C1 = lineareQuation(ps1, pe1)
    A2, B2, C2 = lineareQuation(ps2, pe2)
    if abs(A1*B2 - A2*B1) > abs(offset*B1*B2):
        return Point((B1*C2-C1*B2) / (A1*B2-A2*B1), (A2*C1-A1*C2) / (A1*B2-A2*B1))
    else:
        return abs(A1*ps2.x + B1*ps2.y + C1) / math.sqrt(A1**2 + B1**2)

def intersectBezier3Bezier3(a1, a2, a3, a4, b1, b2, b3, b4, offset = .001):
    # Code from http://www.kevlindev.com/geometry/2D/intersections/intersect_bezier3_bezier3.svg
    
    a = a1 * -1
    b = a2 * 3
    c = a3 * - 3
    d = a + b + c + a4

    c13 = Point(d.x, d.y)
    a = a1 * 3
    b = a2 * -6
    c = a3 * 3
    d = a + b + c

    c12 = Point(d.x, d.y)
    a = a1 * -3
    b = a2 * 3
    c = a + b

    c11 = Point(c.x, c.y)
    c10 = Point(a1.x, a1.y)

    a = b1 * -1
    b = b2 * 3
    c = b3 * - 3
    d = a + b + c + b4
    c23 = Point(d.x, d.y)
    a = b1 * 3
    b = b2 * - 6
    c = b3 * 3
    d = a + b + c
    c22 = Point(d.x, d.y)
    a = b1 * - 3
    b = b2 * 3
    c = a + b
    c21 = Point(c.x, c.y)
    c20 = Point(b1.x, b1.y)
    c10x2 = c10.x * c10.x
    c10x3 = c10.x * c10.x * c10.x
    c10y2 = c10.y * c10.y
    c10y3 = c10.y * c10.y * c10.y
    c11x2 = c11.x * c11.x
    c11x3 = c11.x * c11.x * c11.x
    c11y2 = c11.y * c11.y
    c11y3 = c11.y * c11.y * c11.y
    c12x2 = c12.x * c12.x
    c12x3 = c12.x * c12.x * c12.x
    c12y2 = c12.y * c12.y
    c12y3 = c12.y * c12.y * c12.y
    c13x2 = c13.x * c13.x
    c13x3 = c13.x * c13.x * c13.x
    c13y2 = c13.y * c13.y
    c13y3 = c13.y * c13.y * c13.y
    c20x2 = c20.x * c20.x
    c20x3 = c20.x * c20.x * c20.x
    c20y2 = c20.y * c20.y
    c20y3 = c20.y * c20.y * c20.y
    c21x2 = c21.x * c21.x
    c21x3 = c21.x * c21.x * c21.x
    c21y2 = c21.y * c21.y
    c22x2 = c22.x * c22.x
    c22x3 = c22.x * c22.x * c22.x
    c22y2 = c22.y * c22.y
    c23x2 = c23.x * c23.x
    c23x3 = c23.x * c23.x * c23.x
    c23y2 = c23.y * c23.y
    c23y3 = c23.y * c23.y * c23.y

    poly = [ - c13x3 * c23y3 + c13y3 * c23x3 - 3 * c13.x * c13y2 * c23x2 * c23.y + 3 * c13x2 * c13.y * c23.x * c23y2, - 6 * c13.x * c22.x * c13y2 * c23.x * c23.y + 6 * c13x2 * c13.y * c22.y * c23.x * c23.y + 3 * c22.x * c13y3 * c23x2 - 3 * c13x3 * c22.y * c23y2 - 3 * c13.x * c13y2 * c22.y * c23x2 + 3 * c13x2 * c22.x * c13.y * c23y2, - 6 * c21.x * c13.x * c13y2 * c23.x * c23.y - 6 * c13.x * c22.x * c13y2 * c22.y * c23.x + 6 * c13x2 * c22.x * c13.y * c22.y * c23.y + 3 * c21.x * c13y3 * c23x2 + 3 * c22x2 * c13y3 * c23.x + 3 * c21.x * c13x2 * c13.y * c23y2 - 3 * c13.x * c21.y * c13y2 * c23x2 - 3 * c13.x * c22x2 * c13y2 * c23.y + c13x2 * c13.y * c23.x * (6 * c21.y * c23.y + 3 * c22y2) + c13x3 * ( - c21.y * c23y2 - 2 * c22y2 * c23.y - c23.y * (2 * c21.y * c23.y + c22y2)), c11.x * c12.y * c13.x * c13.y * c23.x * c23.y - c11.y * c12.x * c13.x * c13.y * c23.x * c23.y + 6 * c21.x * c22.x * c13y3 * c23.x + 3 * c11.x * c12.x * c13.x * c13.y * c23y2 + 6 * c10.x * c13.x * c13y2 * c23.x * c23.y - 3 * c11.x * c12.x * c13y2 * c23.x * c23.y - 3 * c11.y * c12.y * c13.x * c13.y * c23x2 - 6 * c10.y * c13x2 * c13.y * c23.x * c23.y - 6 * c20.x * c13.x * c13y2 * c23.x * c23.y + 3 * c11.y * c12.y * c13x2 * c23.x * c23.y - 2 * c12.x * c12y2 * c13.x * c23.x * c23.y - 6 * c21.x * c13.x * c22.x * c13y2 * c23.y - 6 * c21.x * c13.x * c13y2 * c22.y * c23.x - 6 * c13.x * c21.y * c22.x * c13y2 * c23.x + 6 * c21.x * c13x2 * c13.y * c22.y * c23.y + 2 * c12x2 * c12.y * c13.y * c23.x * c23.y + c22x3 * c13y3 - 3 * c10.x * c13y3 * c23x2 + 3 * c10.y * c13x3 * c23y2 + 3 * c20.x * c13y3 * c23x2 + c12y3 * c13.x * c23x2 - c12x3 * c13.y * c23y2 - 3 * c10.x * c13x2 * c13.y * c23y2 + 3 * c10.y * c13.x * c13y2 * c23x2 - 2 * c11.x * c12.y * c13x2 * c23y2 + c11.x * c12.y * c13y2 * c23x2 - c11.y * c12.x * c13x2 * c23y2 + 2 * c11.y * c12.x * c13y2 * c23x2 + 3 * c20.x * c13x2 * c13.y * c23y2 - c12.x * c12y2 * c13.y * c23x2 - 3 * c20.y * c13.x * c13y2 * c23x2 + c12x2 * c12.y * c13.x * c23y2 - 3 * c13.x * c22x2 * c13y2 * c22.y + c13x2 * c13.y * c23.x * (6 * c20.y * c23.y + 6 * c21.y * c22.y) + c13x2 * c22.x * c13.y * (6 * c21.y * c23.y + 3 * c22y2) + c13x3 * ( - 2 * c21.y * c22.y * c23.y - c20.y * c23y2 - c22.y * (2 * c21.y * c23.y + c22y2) - c23.y * (2 * c20.y * c23.y + 2 * c21.y * c22.y)), 6 * c11.x * c12.x * c13.x * c13.y * c22.y * c23.y + c11.x * c12.y * c13.x * c22.x * c13.y * c23.y + c11.x * c12.y * c13.x * c13.y * c22.y * c23.x - c11.y * c12.x * c13.x * c22.x * c13.y * c23.y - c11.y * c12.x * c13.x * c13.y * c22.y * c23.x - 6 * c11.y * c12.y * c13.x * c22.x * c13.y * c23.x - 6 * c10.x * c22.x * c13y3 * c23.x + 6 * c20.x * c22.x * c13y3 * c23.x + 6 * c10.y * c13x3 * c22.y * c23.y + 2 * c12y3 * c13.x * c22.x * c23.x - 2 * c12x3 * c13.y * c22.y * c23.y + 6 * c10.x * c13.x * c22.x * c13y2 * c23.y + 6 * c10.x * c13.x * c13y2 * c22.y * c23.x + 6 * c10.y * c13.x * c22.x * c13y2 * c23.x - 3 * c11.x * c12.x * c22.x * c13y2 * c23.y - 3 * c11.x * c12.x * c13y2 * c22.y * c23.x + 2 * c11.x * c12.y * c22.x * c13y2 * c23.x + 4 * c11.y * c12.x * c22.x * c13y2 * c23.x - 6 * c10.x * c13x2 * c13.y * c22.y * c23.y - 6 * c10.y * c13x2 * c22.x * c13.y * c23.y - 6 * c10.y * c13x2 * c13.y * c22.y * c23.x - 4 * c11.x * c12.y * c13x2 * c22.y * c23.y - 6 * c20.x * c13.x * c22.x * c13y2 * c23.y - 6 * c20.x * c13.x * c13y2 * c22.y * c23.x - 2 * c11.y * c12.x * c13x2 * c22.y * c23.y + 3 * c11.y * c12.y * c13x2 * c22.x * c23.y + 3 * c11.y * c12.y * c13x2 * c22.y * c23.x - 2 * c12.x * c12y2 * c13.x * c22.x * c23.y - 2 * c12.x * c12y2 * c13.x * c22.y * c23.x - 2 * c12.x * c12y2 * c22.x * c13.y * c23.x - 6 * c20.y * c13.x * c22.x * c13y2 * c23.x - 6 * c21.x * c13.x * c21.y * c13y2 * c23.x - 6 * c21.x * c13.x * c22.x * c13y2 * c22.y + 6 * c20.x * c13x2 * c13.y * c22.y * c23.y + 2 * c12x2 * c12.y * c13.x * c22.y * c23.y + 2 * c12x2 * c12.y * c22.x * c13.y * c23.y + 2 * c12x2 * c12.y * c13.y * c22.y * c23.x + 3 * c21.x * c22x2 * c13y3 + 3 * c21x2 * c13y3 * c23.x - 3 * c13.x * c21.y * c22x2 * c13y2 - 3 * c21x2 * c13.x * c13y2 * c23.y + c13x2 * c22.x * c13.y * (6 * c20.y * c23.y + 6 * c21.y * c22.y) + c13x2 * c13.y * c23.x * (6 * c20.y * c22.y + 3 * c21y2) + c21.x * c13x2 * c13.y * (6 * c21.y * c23.y + 3 * c22y2) + c13x3 * ( - 2 * c20.y * c22.y * c23.y - c23.y * (2 * c20.y * c22.y + c21y2) - c21.y * (2 * c21.y * c23.y + c22y2) - c22.y * (2 * c20.y * c23.y + 2 * c21.y * c22.y)), c11.x * c21.x * c12.y * c13.x * c13.y * c23.y + c11.x * c12.y * c13.x * c21.y * c13.y * c23.x + c11.x * c12.y * c13.x * c22.x * c13.y * c22.y - c11.y * c12.x * c21.x * c13.x * c13.y * c23.y - c11.y * c12.x * c13.x * c21.y * c13.y * c23.x - c11.y * c12.x * c13.x * c22.x * c13.y * c22.y - 6 * c11.y * c21.x * c12.y * c13.x * c13.y * c23.x - 6 * c10.x * c21.x * c13y3 * c23.x + 6 * c20.x * c21.x * c13y3 * c23.x + 2 * c21.x * c12y3 * c13.x * c23.x + 6 * c10.x * c21.x * c13.x * c13y2 * c23.y + 6 * c10.x * c13.x * c21.y * c13y2 * c23.x + 6 * c10.x * c13.x * c22.x * c13y2 * c22.y + 6 * c10.y * c21.x * c13.x * c13y2 * c23.x - 3 * c11.x * c12.x * c21.x * c13y2 * c23.y - 3 * c11.x * c12.x * c21.y * c13y2 * c23.x - 3 * c11.x * c12.x * c22.x * c13y2 * c22.y + 2 * c11.x * c21.x * c12.y * c13y2 * c23.x + 4 * c11.y * c12.x * c21.x * c13y2 * c23.x - 6 * c10.y * c21.x * c13x2 * c13.y * c23.y - 6 * c10.y * c13x2 * c21.y * c13.y * c23.x - 6 * c10.y * c13x2 * c22.x * c13.y * c22.y - 6 * c20.x * c21.x * c13.x * c13y2 * c23.y - 6 * c20.x * c13.x * c21.y * c13y2 * c23.x - 6 * c20.x * c13.x * c22.x * c13y2 * c22.y + 3 * c11.y * c21.x * c12.y * c13x2 * c23.y - 3 * c11.y * c12.y * c13.x * c22x2 * c13.y + 3 * c11.y * c12.y * c13x2 * c21.y * c23.x + 3 * c11.y * c12.y * c13x2 * c22.x * c22.y - 2 * c12.x * c21.x * c12y2 * c13.x * c23.y - 2 * c12.x * c21.x * c12y2 * c13.y * c23.x - 2 * c12.x * c12y2 * c13.x * c21.y * c23.x - 2 * c12.x * c12y2 * c13.x * c22.x * c22.y - 6 * c20.y * c21.x * c13.x * c13y2 * c23.x - 6 * c21.x * c13.x * c21.y * c22.x * c13y2 + 6 * c20.y * c13x2 * c21.y * c13.y * c23.x + 2 * c12x2 * c21.x * c12.y * c13.y * c23.y + 2 * c12x2 * c12.y * c21.y * c13.y * c23.x + 2 * c12x2 * c12.y * c22.x * c13.y * c22.y - 3 * c10.x * c22x2 * c13y3 + 3 * c20.x * c22x2 * c13y3 + 3 * c21x2 * c22.x * c13y3 + c12y3 * c13.x * c22x2 + 3 * c10.y * c13.x * c22x2 * c13y2 + c11.x * c12.y * c22x2 * c13y2 + 2 * c11.y * c12.x * c22x2 * c13y2 - c12.x * c12y2 * c22x2 * c13.y - 3 * c20.y * c13.x * c22x2 * c13y2 - 3 * c21x2 * c13.x * c13y2 * c22.y + c12x2 * c12.y * c13.x * (2 * c21.y * c23.y + c22y2) + c11.x * c12.x * c13.x * c13.y * (6 * c21.y * c23.y + 3 * c22y2) + c21.x * c13x2 * c13.y * (6 * c20.y * c23.y + 6 * c21.y * c22.y) + c12x3 * c13.y * ( - 2 * c21.y * c23.y - c22y2) + c10.y * c13x3 * (6 * c21.y * c23.y + 3 * c22y2) + c11.y * c12.x * c13x2 * ( - 2 * c21.y * c23.y - c22y2) + c11.x * c12.y * c13x2 * ( - 4 * c21.y * c23.y - 2 * c22y2) + c10.x * c13x2 * c13.y * ( - 6 * c21.y * c23.y - 3 * c22y2) + c13x2 * c22.x * c13.y * (6 * c20.y * c22.y + 3 * c21y2) + c20.x * c13x2 * c13.y * (6 * c21.y * c23.y + 3 * c22y2) + c13x3 * ( - 2 * c20.y * c21.y * c23.y - c22.y * (2 * c20.y * c22.y + c21y2) - c20.y * (2 * c21.y * c23.y + c22y2) - c21.y * (2 * c20.y * c23.y + 2 * c21.y * c22.y)), - c10.x * c11.x * c12.y * c13.x * c13.y * c23.y + c10.x * c11.y * c12.x * c13.x * c13.y * c23.y + 6 * c10.x * c11.y * c12.y * c13.x * c13.y * c23.x - 6 * c10.y * c11.x * c12.x * c13.x * c13.y * c23.y - c10.y * c11.x * c12.y * c13.x * c13.y * c23.x + c10.y * c11.y * c12.x * c13.x * c13.y * c23.x + c11.x * c11.y * c12.x * c12.y * c13.x * c23.y - c11.x * c11.y * c12.x * c12.y * c13.y * c23.x + c11.x * c20.x * c12.y * c13.x * c13.y * c23.y + c11.x * c20.y * c12.y * c13.x * c13.y * c23.x + c11.x * c21.x * c12.y * c13.x * c13.y * c22.y + c11.x * c12.y * c13.x * c21.y * c22.x * c13.y - c20.x * c11.y * c12.x * c13.x * c13.y * c23.y - 6 * c20.x * c11.y * c12.y * c13.x * c13.y * c23.x - c11.y * c12.x * c20.y * c13.x * c13.y * c23.x - c11.y * c12.x * c21.x * c13.x * c13.y * c22.y - c11.y * c12.x * c13.x * c21.y * c22.x * c13.y - 6 * c11.y * c21.x * c12.y * c13.x * c22.x * c13.y - 6 * c10.x * c20.x * c13y3 * c23.x - 6 * c10.x * c21.x * c22.x * c13y3 - 2 * c10.x * c12y3 * c13.x * c23.x + 6 * c20.x * c21.x * c22.x * c13y3 + 2 * c20.x * c12y3 * c13.x * c23.x + 2 * c21.x * c12y3 * c13.x * c22.x + 2 * c10.y * c12x3 * c13.y * c23.y - 6 * c10.x * c10.y * c13.x * c13y2 * c23.x + 3 * c10.x * c11.x * c12.x * c13y2 * c23.y - 2 * c10.x * c11.x * c12.y * c13y2 * c23.x - 4 * c10.x * c11.y * c12.x * c13y2 * c23.x + 3 * c10.y * c11.x * c12.x * c13y2 * c23.x + 6 * c10.x * c10.y * c13x2 * c13.y * c23.y + 6 * c10.x * c20.x * c13.x * c13y2 * c23.y - 3 * c10.x * c11.y * c12.y * c13x2 * c23.y + 2 * c10.x * c12.x * c12y2 * c13.x * c23.y + 2 * c10.x * c12.x * c12y2 * c13.y * c23.x + 6 * c10.x * c20.y * c13.x * c13y2 * c23.x + 6 * c10.x * c21.x * c13.x * c13y2 * c22.y + 6 * c10.x * c13.x * c21.y * c22.x * c13y2 + 4 * c10.y * c11.x * c12.y * c13x2 * c23.y + 6 * c10.y * c20.x * c13.x * c13y2 * c23.x + 2 * c10.y * c11.y * c12.x * c13x2 * c23.y - 3 * c10.y * c11.y * c12.y * c13x2 * c23.x + 2 * c10.y * c12.x * c12y2 * c13.x * c23.x + 6 * c10.y * c21.x * c13.x * c22.x * c13y2 - 3 * c11.x * c20.x * c12.x * c13y2 * c23.y + 2 * c11.x * c20.x * c12.y * c13y2 * c23.x + c11.x * c11.y * c12y2 * c13.x * c23.x - 3 * c11.x * c12.x * c20.y * c13y2 * c23.x - 3 * c11.x * c12.x * c21.x * c13y2 * c22.y - 3 * c11.x * c12.x * c21.y * c22.x * c13y2 + 2 * c11.x * c21.x * c12.y * c22.x * c13y2 + 4 * c20.x * c11.y * c12.x * c13y2 * c23.x + 4 * c11.y * c12.x * c21.x * c22.x * c13y2 - 2 * c10.x * c12x2 * c12.y * c13.y * c23.y - 6 * c10.y * c20.x * c13x2 * c13.y * c23.y - 6 * c10.y * c20.y * c13x2 * c13.y * c23.x - 6 * c10.y * c21.x * c13x2 * c13.y * c22.y - 2 * c10.y * c12x2 * c12.y * c13.x * c23.y - 2 * c10.y * c12x2 * c12.y * c13.y * c23.x - 6 * c10.y * c13x2 * c21.y * c22.x * c13.y - c11.x * c11.y * c12x2 * c13.y * c23.y - 2 * c11.x * c11y2 * c13.x * c13.y * c23.x + 3 * c20.x * c11.y * c12.y * c13x2 * c23.y - 2 * c20.x * c12.x * c12y2 * c13.x * c23.y - 2 * c20.x * c12.x * c12y2 * c13.y * c23.x - 6 * c20.x * c20.y * c13.x * c13y2 * c23.x - 6 * c20.x * c21.x * c13.x * c13y2 * c22.y - 6 * c20.x * c13.x * c21.y * c22.x * c13y2 + 3 * c11.y * c20.y * c12.y * c13x2 * c23.x + 3 * c11.y * c21.x * c12.y * c13x2 * c22.y + 3 * c11.y * c12.y * c13x2 * c21.y * c22.x - 2 * c12.x * c20.y * c12y2 * c13.x * c23.x - 2 * c12.x * c21.x * c12y2 * c13.x * c22.y - 2 * c12.x * c21.x * c12y2 * c22.x * c13.y - 2 * c12.x * c12y2 * c13.x * c21.y * c22.x - 6 * c20.y * c21.x * c13.x * c22.x * c13y2 - c11y2 * c12.x * c12.y * c13.x * c23.x + 2 * c20.x * c12x2 * c12.y * c13.y * c23.y + 6 * c20.y * c13x2 * c21.y * c22.x * c13.y + 2 * c11x2 * c11.y * c13.x * c13.y * c23.y + c11x2 * c12.x * c12.y * c13.y * c23.y + 2 * c12x2 * c20.y * c12.y * c13.y * c23.x + 2 * c12x2 * c21.x * c12.y * c13.y * c22.y + 2 * c12x2 * c12.y * c21.y * c22.x * c13.y + c21x3 * c13y3 + 3 * c10x2 * c13y3 * c23.x - 3 * c10y2 * c13x3 * c23.y + 3 * c20x2 * c13y3 * c23.x + c11y3 * c13x2 * c23.x - c11x3 * c13y2 * c23.y - c11.x * c11y2 * c13x2 * c23.y + c11x2 * c11.y * c13y2 * c23.x - 3 * c10x2 * c13.x * c13y2 * c23.y + 3 * c10y2 * c13x2 * c13.y * c23.x - c11x2 * c12y2 * c13.x * c23.y + c11y2 * c12x2 * c13.y * c23.x - 3 * c21x2 * c13.x * c21.y * c13y2 - 3 * c20x2 * c13.x * c13y2 * c23.y + 3 * c20y2 * c13x2 * c13.y * c23.x + c11.x * c12.x * c13.x * c13.y * (6 * c20.y * c23.y + 6 * c21.y * c22.y) + c12x3 * c13.y * ( - 2 * c20.y * c23.y - 2 * c21.y * c22.y) + c10.y * c13x3 * (6 * c20.y * c23.y + 6 * c21.y * c22.y) + c11.y * c12.x * c13x2 * ( - 2 * c20.y * c23.y - 2 * c21.y * c22.y) + c12x2 * c12.y * c13.x * (2 * c20.y * c23.y + 2 * c21.y * c22.y) + c11.x * c12.y * c13x2 * ( - 4 * c20.y * c23.y - 4 * c21.y * c22.y) + c10.x * c13x2 * c13.y * ( - 6 * c20.y * c23.y - 6 * c21.y * c22.y) + c20.x * c13x2 * c13.y * (6 * c20.y * c23.y + 6 * c21.y * c22.y) + c21.x * c13x2 * c13.y * (6 * c20.y * c22.y + 3 * c21y2) + c13x3 * ( - 2 * c20.y * c21.y * c22.y - c20y2 * c23.y - c21.y * (2 * c20.y * c22.y + c21y2) - c20.y * (2 * c20.y * c23.y + 2 * c21.y * c22.y)), - c10.x * c11.x * c12.y * c13.x * c13.y * c22.y + c10.x * c11.y * c12.x * c13.x * c13.y * c22.y + 6 * c10.x * c11.y * c12.y * c13.x * c22.x * c13.y - 6 * c10.y * c11.x * c12.x * c13.x * c13.y * c22.y - c10.y * c11.x * c12.y * c13.x * c22.x * c13.y + c10.y * c11.y * c12.x * c13.x * c22.x * c13.y + c11.x * c11.y * c12.x * c12.y * c13.x * c22.y - c11.x * c11.y * c12.x * c12.y * c22.x * c13.y + c11.x * c20.x * c12.y * c13.x * c13.y * c22.y + c11.x * c20.y * c12.y * c13.x * c22.x * c13.y + c11.x * c21.x * c12.y * c13.x * c21.y * c13.y - c20.x * c11.y * c12.x * c13.x * c13.y * c22.y - 6 * c20.x * c11.y * c12.y * c13.x * c22.x * c13.y - c11.y * c12.x * c20.y * c13.x * c22.x * c13.y - c11.y * c12.x * c21.x * c13.x * c21.y * c13.y - 6 * c10.x * c20.x * c22.x * c13y3 - 2 * c10.x * c12y3 * c13.x * c22.x + 2 * c20.x * c12y3 * c13.x * c22.x + 2 * c10.y * c12x3 * c13.y * c22.y - 6 * c10.x * c10.y * c13.x * c22.x * c13y2 + 3 * c10.x * c11.x * c12.x * c13y2 * c22.y - 2 * c10.x * c11.x * c12.y * c22.x * c13y2 - 4 * c10.x * c11.y * c12.x * c22.x * c13y2 + 3 * c10.y * c11.x * c12.x * c22.x * c13y2 + 6 * c10.x * c10.y * c13x2 * c13.y * c22.y + 6 * c10.x * c20.x * c13.x * c13y2 * c22.y - 3 * c10.x * c11.y * c12.y * c13x2 * c22.y + 2 * c10.x * c12.x * c12y2 * c13.x * c22.y + 2 * c10.x * c12.x * c12y2 * c22.x * c13.y + 6 * c10.x * c20.y * c13.x * c22.x * c13y2 + 6 * c10.x * c21.x * c13.x * c21.y * c13y2 + 4 * c10.y * c11.x * c12.y * c13x2 * c22.y + 6 * c10.y * c20.x * c13.x * c22.x * c13y2 + 2 * c10.y * c11.y * c12.x * c13x2 * c22.y - 3 * c10.y * c11.y * c12.y * c13x2 * c22.x + 2 * c10.y * c12.x * c12y2 * c13.x * c22.x - 3 * c11.x * c20.x * c12.x * c13y2 * c22.y + 2 * c11.x * c20.x * c12.y * c22.x * c13y2 + c11.x * c11.y * c12y2 * c13.x * c22.x - 3 * c11.x * c12.x * c20.y * c22.x * c13y2 - 3 * c11.x * c12.x * c21.x * c21.y * c13y2 + 4 * c20.x * c11.y * c12.x * c22.x * c13y2 - 2 * c10.x * c12x2 * c12.y * c13.y * c22.y - 6 * c10.y * c20.x * c13x2 * c13.y * c22.y - 6 * c10.y * c20.y * c13x2 * c22.x * c13.y - 6 * c10.y * c21.x * c13x2 * c21.y * c13.y - 2 * c10.y * c12x2 * c12.y * c13.x * c22.y - 2 * c10.y * c12x2 * c12.y * c22.x * c13.y - c11.x * c11.y * c12x2 * c13.y * c22.y - 2 * c11.x * c11y2 * c13.x * c22.x * c13.y + 3 * c20.x * c11.y * c12.y * c13x2 * c22.y - 2 * c20.x * c12.x * c12y2 * c13.x * c22.y - 2 * c20.x * c12.x * c12y2 * c22.x * c13.y - 6 * c20.x * c20.y * c13.x * c22.x * c13y2 - 6 * c20.x * c21.x * c13.x * c21.y * c13y2 + 3 * c11.y * c20.y * c12.y * c13x2 * c22.x + 3 * c11.y * c21.x * c12.y * c13x2 * c21.y - 2 * c12.x * c20.y * c12y2 * c13.x * c22.x - 2 * c12.x * c21.x * c12y2 * c13.x * c21.y - c11y2 * c12.x * c12.y * c13.x * c22.x + 2 * c20.x * c12x2 * c12.y * c13.y * c22.y - 3 * c11.y * c21x2 * c12.y * c13.x * c13.y + 6 * c20.y * c21.x * c13x2 * c21.y * c13.y + 2 * c11x2 * c11.y * c13.x * c13.y * c22.y + c11x2 * c12.x * c12.y * c13.y * c22.y + 2 * c12x2 * c20.y * c12.y * c22.x * c13.y + 2 * c12x2 * c21.x * c12.y * c21.y * c13.y - 3 * c10.x * c21x2 * c13y3 + 3 * c20.x * c21x2 * c13y3 + 3 * c10x2 * c22.x * c13y3 - 3 * c10y2 * c13x3 * c22.y + 3 * c20x2 * c22.x * c13y3 + c21x2 * c12y3 * c13.x + c11y3 * c13x2 * c22.x - c11x3 * c13y2 * c22.y + 3 * c10.y * c21x2 * c13.x * c13y2 - c11.x * c11y2 * c13x2 * c22.y + c11.x * c21x2 * c12.y * c13y2 + 2 * c11.y * c12.x * c21x2 * c13y2 + c11x2 * c11.y * c22.x * c13y2 - c12.x * c21x2 * c12y2 * c13.y - 3 * c20.y * c21x2 * c13.x * c13y2 - 3 * c10x2 * c13.x * c13y2 * c22.y + 3 * c10y2 * c13x2 * c22.x * c13.y - c11x2 * c12y2 * c13.x * c22.y + c11y2 * c12x2 * c22.x * c13.y - 3 * c20x2 * c13.x * c13y2 * c22.y + 3 * c20y2 * c13x2 * c22.x * c13.y + c12x2 * c12.y * c13.x * (2 * c20.y * c22.y + c21y2) + c11.x * c12.x * c13.x * c13.y * (6 * c20.y * c22.y + 3 * c21y2) + c12x3 * c13.y * ( - 2 * c20.y * c22.y - c21y2) + c10.y * c13x3 * (6 * c20.y * c22.y + 3 * c21y2) + c11.y * c12.x * c13x2 * ( - 2 * c20.y * c22.y - c21y2) + c11.x * c12.y * c13x2 * ( - 4 * c20.y * c22.y - 2 * c21y2) + c10.x * c13x2 * c13.y * ( - 6 * c20.y * c22.y - 3 * c21y2) + c20.x * c13x2 * c13.y * (6 * c20.y * c22.y + 3 * c21y2) + c13x3 * ( - 2 * c20.y * c21y2 - c20y2 * c22.y - c20.y * (2 * c20.y * c22.y + c21y2)), - c10.x * c11.x * c12.y * c13.x * c21.y * c13.y + c10.x * c11.y * c12.x * c13.x * c21.y * c13.y + 6 * c10.x * c11.y * c21.x * c12.y * c13.x * c13.y - 6 * c10.y * c11.x * c12.x * c13.x * c21.y * c13.y - c10.y * c11.x * c21.x * c12.y * c13.x * c13.y + c10.y * c11.y * c12.x * c21.x * c13.x * c13.y - c11.x * c11.y * c12.x * c21.x * c12.y * c13.y + c11.x * c11.y * c12.x * c12.y * c13.x * c21.y + c11.x * c20.x * c12.y * c13.x * c21.y * c13.y + 6 * c11.x * c12.x * c20.y * c13.x * c21.y * c13.y + c11.x * c20.y * c21.x * c12.y * c13.x * c13.y - c20.x * c11.y * c12.x * c13.x * c21.y * c13.y - 6 * c20.x * c11.y * c21.x * c12.y * c13.x * c13.y - c11.y * c12.x * c20.y * c21.x * c13.x * c13.y - 6 * c10.x * c20.x * c21.x * c13y3 - 2 * c10.x * c21.x * c12y3 * c13.x + 6 * c10.y * c20.y * c13x3 * c21.y + 2 * c20.x * c21.x * c12y3 * c13.x + 2 * c10.y * c12x3 * c21.y * c13.y - 2 * c12x3 * c20.y * c21.y * c13.y - 6 * c10.x * c10.y * c21.x * c13.x * c13y2 + 3 * c10.x * c11.x * c12.x * c21.y * c13y2 - 2 * c10.x * c11.x * c21.x * c12.y * c13y2 - 4 * c10.x * c11.y * c12.x * c21.x * c13y2 + 3 * c10.y * c11.x * c12.x * c21.x * c13y2 + 6 * c10.x * c10.y * c13x2 * c21.y * c13.y + 6 * c10.x * c20.x * c13.x * c21.y * c13y2 - 3 * c10.x * c11.y * c12.y * c13x2 * c21.y + 2 * c10.x * c12.x * c21.x * c12y2 * c13.y + 2 * c10.x * c12.x * c12y2 * c13.x * c21.y + 6 * c10.x * c20.y * c21.x * c13.x * c13y2 + 4 * c10.y * c11.x * c12.y * c13x2 * c21.y + 6 * c10.y * c20.x * c21.x * c13.x * c13y2 + 2 * c10.y * c11.y * c12.x * c13x2 * c21.y - 3 * c10.y * c11.y * c21.x * c12.y * c13x2 + 2 * c10.y * c12.x * c21.x * c12y2 * c13.x - 3 * c11.x * c20.x * c12.x * c21.y * c13y2 + 2 * c11.x * c20.x * c21.x * c12.y * c13y2 + c11.x * c11.y * c21.x * c12y2 * c13.x - 3 * c11.x * c12.x * c20.y * c21.x * c13y2 + 4 * c20.x * c11.y * c12.x * c21.x * c13y2 - 6 * c10.x * c20.y * c13x2 * c21.y * c13.y - 2 * c10.x * c12x2 * c12.y * c21.y * c13.y - 6 * c10.y * c20.x * c13x2 * c21.y * c13.y - 6 * c10.y * c20.y * c21.x * c13x2 * c13.y - 2 * c10.y * c12x2 * c21.x * c12.y * c13.y - 2 * c10.y * c12x2 * c12.y * c13.x * c21.y - c11.x * c11.y * c12x2 * c21.y * c13.y - 4 * c11.x * c20.y * c12.y * c13x2 * c21.y - 2 * c11.x * c11y2 * c21.x * c13.x * c13.y + 3 * c20.x * c11.y * c12.y * c13x2 * c21.y - 2 * c20.x * c12.x * c21.x * c12y2 * c13.y - 2 * c20.x * c12.x * c12y2 * c13.x * c21.y - 6 * c20.x * c20.y * c21.x * c13.x * c13y2 - 2 * c11.y * c12.x * c20.y * c13x2 * c21.y + 3 * c11.y * c20.y * c21.x * c12.y * c13x2 - 2 * c12.x * c20.y * c21.x * c12y2 * c13.x - c11y2 * c12.x * c21.x * c12.y * c13.x + 6 * c20.x * c20.y * c13x2 * c21.y * c13.y + 2 * c20.x * c12x2 * c12.y * c21.y * c13.y + 2 * c11x2 * c11.y * c13.x * c21.y * c13.y + c11x2 * c12.x * c12.y * c21.y * c13.y + 2 * c12x2 * c20.y * c21.x * c12.y * c13.y + 2 * c12x2 * c20.y * c12.y * c13.x * c21.y + 3 * c10x2 * c21.x * c13y3 - 3 * c10y2 * c13x3 * c21.y + 3 * c20x2 * c21.x * c13y3 + c11y3 * c21.x * c13x2 - c11x3 * c21.y * c13y2 - 3 * c20y2 * c13x3 * c21.y - c11.x * c11y2 * c13x2 * c21.y + c11x2 * c11.y * c21.x * c13y2 - 3 * c10x2 * c13.x * c21.y * c13y2 + 3 * c10y2 * c21.x * c13x2 * c13.y - c11x2 * c12y2 * c13.x * c21.y + c11y2 * c12x2 * c21.x * c13.y - 3 * c20x2 * c13.x * c21.y * c13y2 + 3 * c20y2 * c21.x * c13x2 * c13.y, c10.x * c10.y * c11.x * c12.y * c13.x * c13.y - c10.x * c10.y * c11.y * c12.x * c13.x * c13.y + c10.x * c11.x * c11.y * c12.x * c12.y * c13.y - c10.y * c11.x * c11.y * c12.x * c12.y * c13.x - c10.x * c11.x * c20.y * c12.y * c13.x * c13.y + 6 * c10.x * c20.x * c11.y * c12.y * c13.x * c13.y + c10.x * c11.y * c12.x * c20.y * c13.x * c13.y - c10.y * c11.x * c20.x * c12.y * c13.x * c13.y - 6 * c10.y * c11.x * c12.x * c20.y * c13.x * c13.y + c10.y * c20.x * c11.y * c12.x * c13.x * c13.y - c11.x * c20.x * c11.y * c12.x * c12.y * c13.y + c11.x * c11.y * c12.x * c20.y * c12.y * c13.x + c11.x * c20.x * c20.y * c12.y * c13.x * c13.y - c20.x * c11.y * c12.x * c20.y * c13.x * c13.y - 2 * c10.x * c20.x * c12y3 * c13.x + 2 * c10.y * c12x3 * c20.y * c13.y - 3 * c10.x * c10.y * c11.x * c12.x * c13y2 - 6 * c10.x * c10.y * c20.x * c13.x * c13y2 + 3 * c10.x * c10.y * c11.y * c12.y * c13x2 - 2 * c10.x * c10.y * c12.x * c12y2 * c13.x - 2 * c10.x * c11.x * c20.x * c12.y * c13y2 - c10.x * c11.x * c11.y * c12y2 * c13.x + 3 * c10.x * c11.x * c12.x * c20.y * c13y2 - 4 * c10.x * c20.x * c11.y * c12.x * c13y2 + 3 * c10.y * c11.x * c20.x * c12.x * c13y2 + 6 * c10.x * c10.y * c20.y * c13x2 * c13.y + 2 * c10.x * c10.y * c12x2 * c12.y * c13.y + 2 * c10.x * c11.x * c11y2 * c13.x * c13.y + 2 * c10.x * c20.x * c12.x * c12y2 * c13.y + 6 * c10.x * c20.x * c20.y * c13.x * c13y2 - 3 * c10.x * c11.y * c20.y * c12.y * c13x2 + 2 * c10.x * c12.x * c20.y * c12y2 * c13.x + c10.x * c11y2 * c12.x * c12.y * c13.x + c10.y * c11.x * c11.y * c12x2 * c13.y + 4 * c10.y * c11.x * c20.y * c12.y * c13x2 - 3 * c10.y * c20.x * c11.y * c12.y * c13x2 + 2 * c10.y * c20.x * c12.x * c12y2 * c13.x + 2 * c10.y * c11.y * c12.x * c20.y * c13x2 + c11.x * c20.x * c11.y * c12y2 * c13.x - 3 * c11.x * c20.x * c12.x * c20.y * c13y2 - 2 * c10.x * c12x2 * c20.y * c12.y * c13.y - 6 * c10.y * c20.x * c20.y * c13x2 * c13.y - 2 * c10.y * c20.x * c12x2 * c12.y * c13.y - 2 * c10.y * c11x2 * c11.y * c13.x * c13.y - c10.y * c11x2 * c12.x * c12.y * c13.y - 2 * c10.y * c12x2 * c20.y * c12.y * c13.x - 2 * c11.x * c20.x * c11y2 * c13.x * c13.y - c11.x * c11.y * c12x2 * c20.y * c13.y + 3 * c20.x * c11.y * c20.y * c12.y * c13x2 - 2 * c20.x * c12.x * c20.y * c12y2 * c13.x - c20.x * c11y2 * c12.x * c12.y * c13.x + 3 * c10y2 * c11.x * c12.x * c13.x * c13.y + 3 * c11.x * c12.x * c20y2 * c13.x * c13.y + 2 * c20.x * c12x2 * c20.y * c12.y * c13.y - 3 * c10x2 * c11.y * c12.y * c13.x * c13.y + 2 * c11x2 * c11.y * c20.y * c13.x * c13.y + c11x2 * c12.x * c20.y * c12.y * c13.y - 3 * c20x2 * c11.y * c12.y * c13.x * c13.y - c10x3 * c13y3 + c10y3 * c13x3 + c20x3 * c13y3 - c20y3 * c13x3 - 3 * c10.x * c20x2 * c13y3 - c10.x * c11y3 * c13x2 + 3 * c10x2 * c20.x * c13y3 + c10.y * c11x3 * c13y2 + 3 * c10.y * c20y2 * c13x3 + c20.x * c11y3 * c13x2 + c10x2 * c12y3 * c13.x - 3 * c10y2 * c20.y * c13x3 - c10y2 * c12x3 * c13.y + c20x2 * c12y3 * c13.x - c11x3 * c20.y * c13y2 - c12x3 * c20y2 * c13.y - c10.x * c11x2 * c11.y * c13y2 + c10.y * c11.x * c11y2 * c13x2 - 3 * c10.x * c10y2 * c13x2 * c13.y - c10.x * c11y2 * c12x2 * c13.y + c10.y * c11x2 * c12y2 * c13.x - c11.x * c11y2 * c20.y * c13x2 + 3 * c10x2 * c10.y * c13.x * c13y2 + c10x2 * c11.x * c12.y * c13y2 + 2 * c10x2 * c11.y * c12.x * c13y2 - 2 * c10y2 * c11.x * c12.y * c13x2 - c10y2 * c11.y * c12.x * c13x2 + c11x2 * c20.x * c11.y * c13y2 - 3 * c10.x * c20y2 * c13x2 * c13.y + 3 * c10.y * c20x2 * c13.x * c13y2 + c11.x * c20x2 * c12.y * c13y2 - 2 * c11.x * c20y2 * c12.y * c13x2 + c20.x * c11y2 * c12x2 * c13.y - c11.y * c12.x * c20y2 * c13x2 - c10x2 * c12.x * c12y2 * c13.y - 3 * c10x2 * c20.y * c13.x * c13y2 + 3 * c10y2 * c20.x * c13x2 * c13.y + c10y2 * c12x2 * c12.y * c13.x - c11x2 * c20.y * c12y2 * c13.x + 2 * c20x2 * c11.y * c12.x * c13y2 + 3 * c20.x * c20y2 * c13x2 * c13.y - c20x2 * c12.x * c12y2 * c13.y - 3 * c20x2 * c20.y * c13.x * c13y2 + c12x2 * c20y2 * c12.y * c13.x]
    roots = equation(*poly, offset=offset)
    roots = list(roots)
    roots.sort()

    retsults = []
    pre = -999999999
    for t in roots:
        if t - pre < offset:
            pre = 0
            continue
        pre = t

        retsults.append(t)
        # xRoots = equation(c13.x, c12.x, c11.x, c10.x - c20.x - t * c21.x - t * t * c22.x - t * t * t * c23.x)
        # yRoots = equation(c13.y, c12.y, c11.y, c10.y - c20.y - t * c21.y - t * t * c22.y - t * t * t * c23.y)

        # if (len(xRoots) == 0) ^ (len(yRoots) == 0):
        #     retsults.append(t)
        #     continue

        # done = False
        # for xRoot in xRoots:
        #     for yRoot in yRoots:
        #         if abs(xRoot - yRoot) < offset:
        #             retsults.append(t)
        #             done = True
        #             break
        #     if done:
        #         break

    return retsults

def _getPointFromReMatch(match):
    return Point(next(match).group(), next(match).group())

def cInterpolation(t):
    if t < 0 or t > 1:
        raise ValueError("Require value is between 0 ~ 1!")
    return (1-t)**3 / (t**3 + (1-t)**3)

def abcRotate(t):
    if t < 0 or t > 1:
        raise ValueError("Require value is between 0 ~ 1!")
    return math.fabs((t**3 + (1-t)**3 - 1) / (t**3 + (1-t)**3))

def equation(*coefficient, offset=0):
    from numpy import roots
    from numpy import float64

    re = []
    for r in roots(coefficient):
        if isinstance(r, float64):
            re.append(r)
        elif abs(r.imag) < offset:
            re.append(r.real)
    return set(re)

class BezierCtrl(object):
    def __init__(self, pos:Point, p1:Point = Point(0,0), p2:Point = None) -> None:
        self.p1 = p1
        self.p2 = p2
        self.pos = pos

        # Test
        # if not self.isValid(1):
        #     if not (p1.isOrigin() and (p2 == None or p2.isOrigin()) and pos.isOrigin()):
        #         raise Exception('Empty bezier ctrl!')

    @property
    def p2(self):
        if self._p2:
            return self._p2
        else:
            return self.pos

    @p2.setter
    def p2(self, pos:Point):
        self._p2 = pos

    def casteljauPoints(self, t:float, pos:Point=Point(), limit=True):
        if limit and (t < 0 or t > 1):
            raise ValueError("Require value is between 0 ~ 1!")
        
        posList = { 'n3': [], 'n2': [], 'n1': Point() }
        posList['n3'].append(self.p1 * t + pos)
        posList['n3'].append((self.p2 - self.p1) * t + self.p1 + pos)
        posList['n3'].append((self.pos - self.p2) * t + self.p2 + pos)
        posList['n2'].append((posList['n3'][1] - posList['n3'][0]) * t + posList['n3'][0])
        posList['n2'].append((posList['n3'][2] - posList['n3'][1]) * t + posList['n3'][1])
        posList['n1'] = (posList['n2'][1] - posList['n2'][0]) * t + posList['n2'][0]
        return posList

    def valueAt(self, t:float, pos:Point=Point(), limit=True):
        return self.casteljauPoints(t, pos, limit)['n1']
        
    def posAt(self, pos:Point=Point(), sPos:Point=Point(), offset=.5, interval=[0,1]):
        ctrl = self
        radian = 0
        while ((ctrl.p1.x == 0) ^ (ctrl.p1.y == 0)) or ((ctrl.p2.x == 0) ^ (ctrl.p2.y == 0)):
            radian += math.pi/90
            ctrl = self.rotate(radian)
        if radian != 0:
            pos = pos.rotate(radian, sPos)
            
        tOffset = offset/self.approximatedLength(12)# max(min(offset/self.approximatedLength(12), .001), .1)
        values = ctrl.roots(x=pos.x, y=pos.y, pos=sPos, offset=tOffset, interval=interval)
        tList = []
        for t in values:
            if ctrl.valueAt(t, sPos).distanceOffset(pos, offset):
                tList.append(t)

        temp = []
        pre = -99999
        for t in tList:
            if t - pre > tOffset:
                temp.append(t)
            pre = t
        return temp
        
    def valueAtCalculus(self, t:float, pos:Point=Point()):
        if t < 0 or t > 1:
            raise ValueError("Require value is between 0 ~ 1!")
        t2 = t * t
        t3 = t2 * t
        mt = 1 - t
        mt2 = mt * mt
        mt3 = mt2 * mt
        return pos*mt3 + self.p1*3*mt2*t + self.p2*3*mt*t2 + (self.pos+pos)*t3

    def splitting(self, t:float, pos:Point = Point()):
        cPosList = self.casteljauPoints(t, pos)
        return [ BezierCtrl(p1=cPosList['n3'][0]-pos, p2=cPosList['n2'][0]-pos, pos=cPosList['n1']-pos), BezierCtrl(p1=cPosList['n2'][1]-cPosList['n1'], p2=cPosList['n3'][2]-cPosList['n1'], pos=self.pos-cPosList['n1']) ]

    def tangents(self, t:float, len=1, pos:Point = Point()):
        b1 = self.p1.isOrigin()
        b2 = self.p2.distance(self.pos) == 0
        if b1 and b2:
            return [self.pos*t + pos, self.pos.normalization(len) + self.pos*t + pos]

        cPosList = self.casteljauPoints(t, pos)

        tline = cPosList['n2'][1] - cPosList['n2'][0]
        if tline.isOrigin():
            if b1:
                tline = cPosList['n3'][2] - cPosList['n3'][1]
            elif b2:
                tline = cPosList['n3'][1] - cPosList['n3'][0]
        return [cPosList['n1'], tline.normalization(len) + cPosList['n1']]

    def normals(self, t:float, len=1, pos:Point = Point()):
        tLine = self.tangents(t, len, pos)
        return [(tLine[1] - tLine[0]).perpendicular(), tLine[0]]

    def roots(self, x=None, y=None, pos:Point=Point(), offset=0, interval=[-9999, 9999]):
        result = []
        
        three = (self.p1+pos)*3 - (self.p2+pos)*3 - pos + (self.pos+pos)
        two = pos*3 - (self.p1+pos)*6 + (self.p2+pos)*3
        one = (self.p1+pos)*3 - pos*3
        if x != None:
            result += equation(three.x, two.x, one.x, pos.x-x, offset=offset)
        if y != None:
            result += equation(three.y, two.y, one.y, pos.y-y, offset=offset)
        
        temp = []
        n = interval[0]-offset
        result.sort()
        for r in result:
            if abs(interval[0] - r) < offset:
                r = interval[0]
            elif abs(r - interval[1]) < offset:
                r = interval[1]
            if r >= interval[0] and r <= interval[1]:
                if len(temp) != 0:
                    if r - n > offset:
                        temp.append(r)
                else:
                    temp.append(r)
                n = r

        return temp

    def extermes(self, radian=0):
        ctrl = self.rotate(radian)
        def second(v1, v2, v3):
            a = 3*v1- 3*v2 + v3
            b = 2 * (v2 - 2*v1)
            c = v1

            results = []
            if a != 0:
                n = b**2 - 4*a*c
                if n > 0:
                    results = [ (-b + math.sqrt(n)) / (2*a), (-b - math.sqrt(n)) / (2*a) ]
                elif n == 0:
                    results = [ -b / (2*a) ]
                    
            return results

        def one(v1, v2):
            result = None
            if v2 -v1 != 0:
                result = -v1 / (v2 - v1)
            return result

        results = []
        results.append(second(ctrl.p1.x, ctrl.p2.x, ctrl.pos.x))
        results.append(second(ctrl.p1.y, ctrl.p2.y, ctrl.pos.y))
        results.append(one(ctrl.p2.x - 2*ctrl.p1.x, ctrl.pos.x - 2*ctrl.p2.x + ctrl.p1.x))
        results.append(one(ctrl.p2.y - 2*ctrl.p1.y, ctrl.pos.y - 2*ctrl.p2.y + self.p1.y))
        
        return results

    def boundingBox(self, startPos=Point()):
        roots = self.extermes()
        dotListX = []
        dotListY = []
        dotListX.extend([ startPos.x, startPos.x + self.pos.x ])
        dotListY.extend([ startPos.y, startPos.y + self.pos.y ])
        for t in roots[0]:
            if t < 0 or t > 1:
                continue
            aPos = self.valueAt(t, startPos)
            dotListX.append(aPos.x)
        for t in roots[1]:
            if t < 0 or t > 1:
                continue
            aPos = self.valueAt(t, startPos)
            dotListY.append(aPos.y)
            
        if roots[2] and roots[2] > 0 and roots[2] < 1:
            aPos = self.valueAt(roots[2], startPos)
            dotListX.append(aPos.x)
        if roots[3] and roots[3] > 0 and roots[3] < 1:
            aPos = self.valueAt(roots[3], startPos)
            dotListY.append(aPos.y)

        lbPos = Point(min(dotListX), min(dotListY))
        rtPos = Point(max(dotListX), max(dotListY))
        return Rect(lbPos, rtPos)

    def rotate(self, radian):
        return BezierCtrl(p1=self.p1.rotate(radian), p2=self.p2.rotate(radian), pos=self.pos.rotate(radian))

    def rotations(self):
        tangents = self.tangents(0)
        p1 = tangents[1] - tangents[0]
        tangents = self.tangents(1)
        p2 = tangents[1] - tangents[0]
        t = round(p1.x * p2.y - p2.x * p1.y, 3)
        if t < 0:
            return -1
        elif t > 0:
            return 1
        else:
            return 0

    def fromABC(t:float, tangents, start:Point, end:Point):
        ut = cInterpolation(t)
        c = start*ut + end*(1-ut)
        b = tangents[0]
        a = b - (c-b) / abcRotate(t)

        ts = tangents[1] - b
        v1 = ((b-(ts*t) / (1-t)) - a*t) / (1-t)
        v2 = ((b+ts) - a*(1-t)) / t

        p1 = (v1 - start*(1-t)) / t
        p2 = (v2 - end*t) / (1-t)

        return BezierCtrl(p1=p1-start, p2=p2-start, pos=end-start)

    def approximatedLength(self, segment=8):
        lenPos = []
        unit = 1 / segment
        for v in range(1, segment):
            lenPos.append(self.valueAt(v * unit))
        lenPos.append(self.pos)
        length = 0
        for i in range(0, len(lenPos)-1):
            length += lenPos[i].distance(lenPos[i+1])

        return length

    def simplifiedCheck(self, pos, other, otherPos:Point, offset=.5):
        def findTFromPos(ctrl, pos, sPos):
            # tOffset = offset/ctrl.approximatedLength()*1.1
            # r1 = ctrl.roots(x=pos.x, y=pos.y, pos=sPos, offset=tOffset, interval=[0, 1])
            r1 = ctrl.posAt(pos, sPos, .5, interval=[0, 1])
            if len(r1):
                r1 = [sum(r1) / len(r1)]
            return r1

        def pointInLine(pos, linep1, linep2, offset):
            sx = linep1.x
            ex = linep2.x
            if sx > ex:
                sx, ex = ex, sx
            sy = linep1.y
            ey = linep2.y
            if sy > ey:
                sy, ey = ey, sy

            return pos.x - sx > -offset and ex - pos.x > -offset and pos.y - sy > -offset and ey - pos.y > -offset

        posE = self.pos+pos
        otherPosE = other.pos+otherPos
        result = intersection(pos, posE, otherPos, otherPosE)
        if type(result) == Point:
            if pointInLine(result, pos, posE, offset) and pointInLine(result, otherPos, otherPosE, offset):
                ## Test start
                # check1 = findTFromPos(self, result, pos)
                # check2 = findTFromPos(other, result, otherPos)
                # if len(check1) != 1 or len(check2) != 1:
                #     check1 = findTFromPos(self, result, pos)
                #     check2 = findTFromPos(other, result, otherPos)
                #     raise Exception('Not found pos!')
                ## Test end
                return [findTFromPos(self, result, pos), findTFromPos(other, result, otherPos), False]
        elif result < offset:
            return [self.posAt(otherPos, pos, 1) + self.posAt(otherPosE, pos, 1), other.posAt(pos, otherPos, 1) + other.posAt(posE, otherPos, 1), True]

        return [[], [], False]

    def intersections(self, pos, other, otherPos:Point, interval=[0, 1]):
        PIX_OFFSET = 1

        rect1 = self.boundingBox(pos)
        rect2 = other.boundingBox(otherPos)
        if not rect1.intersects(rect2, -PIX_OFFSET/2):
            return [[], []]

        poslist = [[], []]
        tOffset = [PIX_OFFSET/self.approximatedLength(), PIX_OFFSET/other.approximatedLength()]

        l1 = self.isLine()
        l2 = other.isLine()
        if l1 and l2:
            poslist[0], poslist[1], _ = self.simplifiedCheck(pos, other, otherPos)
        elif l1:
            r =  -self.pos.radian()
            roots = other.rotate(r).roots(y=pos.y, pos=otherPos.rotate(r, pos), offset=tOffset[1], interval=[0, 1])
            for t in roots: 
                p = self.posAt(other.valueAt(t, otherPos), pos, .5)
                if len(p):
                    poslist[0].append(p[0])
                    poslist[1].append(t)
        elif l2:
            r =  -other.pos.radian()
            roots = self.rotate(r).roots(y=otherPos.y, pos=pos.rotate(r, otherPos), offset=tOffset[0], interval=[0, 1])
            for t in roots: 
                p = other.posAt(self.valueAt(t, pos), otherPos, .5)
                if len(p):
                    poslist[1].append(p[0])
                    poslist[0].append(t)
        else:
            roots = intersectBezier3Bezier3(pos, self.p1+pos, self.p2+pos, self.pos+pos, otherPos, other.p1+otherPos, other.p2+otherPos, other.pos+otherPos, tOffset[1])
            for t in roots:
                if t >= interval[0] and t <= interval[1]:
                    p = self.posAt(other.valueAt(t, otherPos), pos, .5)
                    if len(p):
                        poslist[0].append(p[0])
                        poslist[1].append(t)
            
            if len(poslist[1]) == 0:
                return [self.posAt(otherPos, pos, 5) + self.posAt(otherPos+other.pos, pos, 5), other.posAt(pos, otherPos, 5) + other.posAt(pos+self.pos, otherPos, 5)]

        return poslist

    def appIntersections(self, pos, other, otherPos:Point, interval=[0, 1], preCtrl1=None, preCtrl2=None):
        OVERLAP = -1
        INCREMENT = 2
        
        RADIANT = math.pi / 90
        PIX_OFFSET = 1

        def simplifiedCheck(ctrl1, pos1, list1, ctrl2, pos2, list2, preCtrl1=None, preCtrl2=None):
            OFFSET = .01
            
            if preCtrl1 == None:
                preCtrl1 = ctrl1.radianSegmentation(RADIANT)
            if preCtrl2 == None:
                preCtrl2 = ctrl2.radianSegmentation(RADIANT)

            temp = [[]]
            for i in range(0, len(preCtrl1[0])):
                temp[0].append([])
            temp.append([])
            for i in range(0, len(preCtrl2[0])):
                temp[1].append([])

            p1 = pos1
            for i1 in range(0, len(preCtrl1[0])):
                p2 = pos2
                for i2 in range(0, len(preCtrl2[0])):
                    r1, r2, overlap = preCtrl1[0][i1].simplifiedCheck(p1, preCtrl2[0][i2], p2, PIX_OFFSET)
                    if overlap:
                        temp[0][i1].append(OVERLAP)
                        for t in r1:
                            temp[0][i1].append(INCREMENT+t)
                        temp[1][i2].append(OVERLAP)
                        for t in r2:
                            temp[1][i2].append(INCREMENT+t)
                    else:
                        temp[0][i1].extend(r1)
                        temp[1][i2].extend(r2)
                    p2 += preCtrl2[0][i2].pos
                p1 += preCtrl1[0][i1].pos

            a = 0
            lists = [list1, list2]
            preCtrls = [preCtrl1, preCtrl2]
            for results in temp:
                for i in range(0, len(results)):
                    for r in results[i]:
                        if r != OVERLAP:
                            if r >= INCREMENT:
                                r -= INCREMENT
                                if r < 0+OFFSET:
                                    if i != 0 and results[i-1].count(OVERLAP) != 0:
                                        continue
                                elif r > 1-OFFSET:
                                    if i+1 != len(results) and results[i+1].count(OVERLAP) != 0:
                                        continue
                            
                            if i != 0:
                                preT = preCtrls[a][1][i-1]
                            else:
                                preT = 0
                            current = preCtrls[a][1][i] -preT

                            lists[a].append(r * current + preT)
                a += 1
            
            return len(list1)

        # binarySearch
        def binarySearch(ctrl1, pos1, list1, ctrl2, pos2, list2):
            rect1 = ctrl1.boundingBox(pos1)
            rect2 = ctrl2.boundingBox(pos2)

            if rect1.intersects(rect2, -PIX_OFFSET/2):
                if ctrl1.curve() > RADIANT and (rect1.width > PIX_OFFSET or rect1.height > PIX_OFFSET):
                    splitCtrl = ctrl1.splitting(.5)
                    ok = False

                    rList = []
                    if binarySearch(ctrl2, pos2, list2, splitCtrl[0], pos1, rList):
                        for i in range(0, len(rList)):
                            rList[i] *= .5
                        list1.extend(rList)
                        ok = True

                    rList = []
                    if binarySearch(ctrl2, pos2, list2, splitCtrl[1], splitCtrl[0].pos + pos1, rList):
                        for i in range(0, len(rList)):
                            rList[i] = rList[i]*.5 + .5
                        list1.extend(rList)
                        ok = True

                    return ok
                elif ctrl2.curve() > RADIANT and (rect2.width > PIX_OFFSET or rect2.height > PIX_OFFSET):
                    splitCtrl = ctrl2.splitting(.5)
                    ok = False

                    rList = []
                    if binarySearch(ctrl1, pos1, list1, splitCtrl[0], pos2, rList):
                        for i in range(0, len(rList)):
                            rList[i] *= .5
                        list2.extend(rList)
                        ok = True
                        
                    rList = []
                    if binarySearch(ctrl1, pos1, list1, splitCtrl[1], splitCtrl[0].pos + pos2, rList):
                        for i in range(0, len(rList)):
                            rList[i] = rList[i]*.5 + .5
                        list2.extend(rList)
                        ok = True

                    return ok
                else:
                    def findTFromPos(ctrl, pos, sPos):
                        r1 = ctrl.posAt(pos, sPos, 1, interval=[0, 1])
                        if len(r1):
                            r1 = [sum(r1) / len(r1)]
                        return r1

                    b1 = rect1.width > PIX_OFFSET or rect1.height > PIX_OFFSET
                    b2 = rect2.width > PIX_OFFSET or rect2.height > PIX_OFFSET
                    # b1 = ctrl1.curve() < RADIANT
                    # b2 = ctrl2.curve() < RADIANT
                    if b1 and b2:
                        r1, r2, _ = ctrl1.simplifiedCheck(pos1, ctrl2, pos2)
                        list1.extend(r1)
                        list2.extend(r2)
                        return len(r1)
                    elif b1:
                        r = findTFromPos(ctrl1, ctrl2.valueAt(.5, pos2), pos1)
                        if len(r):
                            list1 += r
                            list2.append(.5)
                        return len(r)
                    elif b2:
                        r = findTFromPos(ctrl2, ctrl1.valueAt(.5, pos1), pos2)
                        if len(r):
                            list2 += r
                            list1.append(.5)
                        return len(r)
                    else:
                        list1.append(.5)
                        list2.append(.5)
                        return True
            else:
                return False

        poslist = [[], []]
        check = binarySearch
        check(self, pos, poslist[0], other, otherPos, poslist[1])
        #check = simplifiedCheck
        #check(self, pos, poslist[0], other, otherPos, poslist[1])

        tOffset = [PIX_OFFSET/self.approximatedLength(), PIX_OFFSET/other.approximatedLength()]
        for i in [0, 1]:
            temp = []
            n = interval[0]
            poslist[i].sort()
            for r in poslist[i]:
                if r >= interval[0] and r <= interval[1]:
                    if len(temp) != 0:
                        if r - n > tOffset[i]:
                            if len(temp) and n != temp[-1]:
                                if n - temp[-1] > tOffset[i]:
                                    temp.append(n)
                                else:
                                    temp[-1] = (temp[-1] + n) / 2
                            temp.append(r)
                    else:
                        temp.append(r)
                    n = r
            if len(temp):
                if n - temp[-1] > tOffset[i]:
                    temp.append(n)
                else:
                    temp[-1] = (temp[-1] + n) / 2
            poslist[i] = temp

        return poslist
        
    def curve(self):
        circle = math.pi*2
        sTangents = self.tangents(0)
        sRadian = sTangents[1].radian(sTangents[0])
        eTangents = self.tangents(1)
        eRadian = eTangents[1].radian(eTangents[0])

        r = self.rotations()
        if r < 0:
            return (sRadian - eRadian) % circle
        else:
            return (eRadian - sRadian) % circle

    def radianSegmentation(self, radian):
        OFFSET = .01
        sTangents = self.tangents(0)
        sRadian = (sTangents[1].radian(sTangents[0]) + math.pi*2) % (math.pi*2)
        # eTangents = self.tangents(1)
        # eRadian = (eTangents[1].radian(eTangents[0]) + math.pi*2) % (math.pi*2)
        r = self.curve()
        radian = radian % (math.pi*2)
        nectR = radian * self.rotations()

        if abs(radian) < OFFSET:
            return [[self], [1]]
        
        ctrl = self.rotate(-sRadian)
        tList = []
        cList = []
        preT = 0
        while abs(r-radian) > abs(radian) and ctrl.isValid(OFFSET):
            ctrl = ctrl.rotate(-nectR)
            t = None
            for n in ctrl.extermes()[1]:
                if n > 0 and n <= 1 and (t == None or t > n):
                    t = n
            tList.append(t * (1-preT) + preT)
            cList.append(self.splitting(preT)[1].splitting(t)[0])
            preT = tList[-1]
            ctrl = ctrl.splitting(t)[1]

            r -= radian

        if len(tList) != 0 and 1 - tList[-1] < OFFSET:
            if len(tList) > 1:
                preT = tList[-2]
            else:
                preT = 0
            tList[-1] = 1
            cList[-1] = self.splitting(preT)[1]
        else:
            tList.append(1)
            cList.append(self.splitting(preT)[1])

        return [cList, tList]

    def scale(self, value):
        return BezierCtrl(p1=self.p1.scale(value), p2=self.p2.scale(value), pos=self.pos.scale(value))

    def isLine(self):
        OFFSET = .01
        return abs(self.pos.x * self.p2.y - self.p2.x * self.pos.y) < OFFSET and abs(self.p1.x * self.p2.y - self.p2.x * self.p1.y) < OFFSET

    def isValid(self, offset=0):
        return max(abs(self.p1.x), abs(self.p2.x), abs(self.pos.x), abs(self.p1.y), abs(self.p2.y), abs(self.pos.y)) > offset

def _connectPaths(paths):
    OFFSET = 2

    temp = []
    if len(paths[0]) == 0:
        if len(paths[1]) == 0:
            return temp
        else:
            paths = [paths[1], paths[0]]
    for aPaths in paths:
        i = 0
        while i < len(aPaths):
            if len(aPaths) != 1 and aPaths[i].endPos().distanceOffset(aPaths[(i+1) % len(aPaths)].startPos(), OFFSET):
                j = (i+1) % len(aPaths)
                aPaths[i].connectPath(aPaths[j])
                aPaths.pop(j)
                if j == 0:
                     i -= 1
                else:
                    continue

            if aPaths[i].endPos().distanceOffset(aPaths[i].startPos(), OFFSET):
                aPaths[i].close()

            if aPaths[i].isClose():
                temp.append(aPaths[i])
                aPaths.pop(i)
            else:
                i += 1

    a = 0
    while len(paths[0]) or len(paths[1]):
        if len(paths[a]) == 0:
            a = (a+1) % 2

        connectPath = paths[a][0]
        paths[a].pop(0)
        a = (a+1) % 2
        if len(paths[a]) == 0:
            a = (a+1) % 2
        pos = connectPath.endPos()
        i = 0
        done = False
        while not done:
            for p2 in [paths[a][i], paths[a][i].reverse()]:
                if pos.distanceOffset(p2.startPos(), OFFSET):
                    pos = p2.endPos()
                    connectPath.connectPath(p2)
                    paths[a].pop(i)
                    a = (a+1) % 2
                    i = -1
                    if connectPath.startPos().distanceOffset(connectPath.endPos(), OFFSET):
                        done = True
                        connectPath.close()
                        temp.append(connectPath)
                    break
            i += 1

    return temp
           
class BezierPath(object):
    def __init__(self) -> None:
        self._ctrlList = []

    def __iter__(self):
        return iter(self._ctrlList)

    def __len__(self):
        return len(self._ctrlList)

    def __getitem__(self, index):
        return self._ctrlList[index]

    def __setitem__(self, index, value:BezierCtrl):
        self._ctrlList[index] = value

    def __and__(self, path):
        if len(self) == 0 or len(path) == 0:
            return []

        newPaths = self.separateFromPath(path)
        
        oldPath = [self, path]
        a = 0
        b = 1
        while True:
            temp = []
            for p in newPaths[a]:
                pos = p[0].valueAt(.5, p.startPos())
                if oldPath[b].containsPos(pos):
                    temp.append(p)
            newPaths[a] = temp
            if a == 0:
                a, b = b, a
            else:
                break

        return _connectPaths(newPaths)

    def __or__(self, path):
        b1 = len(self) == 0
        b2 = len(path) == 0
        if b1 and b2:
            return []
        elif b1:
            return [path]
        elif b2:
            return [self]            
            
        newPaths = self.separateFromPath(path)
        
        oldPath = [self, path]
        a = 0
        b = 1
        while True:
            temp = []
            for p in newPaths[a]:
                pos = p[0].valueAt(.5, p.startPos())
                if not oldPath[b].containsPos(pos):
                    temp.append(p)
            newPaths[a] = temp
            if a == 0:
                a, b = b, a
            else:
                break

        return _connectPaths(newPaths)

    def __sub__(self, path):
        if not (self.isClose() and path.isClose()):
            return [self]

        newPaths = self.separateFromPath(path)
        
        oldPath = [self, path]
        a = 0
        b = 1
        flag = True
        while True:
            temp = []
            for p in newPaths[a]:
                i = 0
                while not p[i].isValid(5) and i + 1 != len(p):
                    i += 1
                pos = p[i].valueAt(.5, p.startPos())
                if oldPath[b].containsPos(pos) ^ flag:
                    temp.append(p)
            newPaths[a] = temp
            if a == 0:
                a, b = b, a
                flag = False
            else:
                break

        return _connectPaths(newPaths)

    def insert(self, index, value:BezierCtrl):
        self._ctrlList.insert(index, value)

    def extend(self, iterable):
        self._ctrlList.extend(iterable)

    def popFront(self):
        self._ctrlList.pop(0)

    def popBack(self):
        self._ctrlList.pop()

    def startPos(self):
        return self._startPos

    def start(self, pos:Point=Point()):
        self._startPos = pos
    
    setStartPos = start

    def close(self):
        if not hasattr(self, 'z'):
            ep = self.endPos()
            sp = self.startPos()

            OFFSET = 1
            if ep != sp:
                if ep.distance(sp) < OFFSET:
                    self[-1].pos += sp - ep
                else:
                    self.connect(sp - ep)
            
            self.z = True

    def isClose(self):
        return hasattr(self, 'z')
        
    def connect(self, pos:Point, p1:Point = Point(0, 0), p2:Point = None, s:bool = False):
        if self.isClose():
            raise Exception('Add point to the closed path!')
        if not hasattr(self, '_startPos'):
            raise Exception('Bezier path not started!')
        if p1.isOrigin() and (p2 == None or p2.isOrigin()) and pos.isOrigin():
            return
        if s:
            p1 = self._ctrlList[-1].pos - self._ctrlList[-1].p2
        self._ctrlList.append(BezierCtrl(pos, p1, p2))

    def connectPath(self, path):
        if self.isClose() or path.isClose():
            raise Exception('Cannot connect closed path!')
        self._ctrlList.extend(iter(path))

    def append(self, ctrl:BezierCtrl):
        self._ctrlList.append(ctrl)
        
    def backCtrl(self):
        return self._ctrlList[-1]
    
    def boundingBox(self):
        rect = Rect(Point(99999, 99999), Point())
        startPos = self.startPos()
        for bCtrl in self._ctrlList:
            box = bCtrl.boundingBox(startPos)
            if box.left < rect.left: rect.left = box.left
            if box.bottom < rect.bottom: rect.bottom = box.bottom
            if box.right > rect.right: rect.right = box.right
            if box.top > rect.top: rect.top = box.top
            startPos += bCtrl.pos

        return rect

    def rotate(self, radian, center:Point=Point()):
        newPath = BezierPath()
        newPath.start(self.startPos().rotate(radian, center))
        for ctrl in self._ctrlList:
            newPath.append(ctrl.rotate(radian))

        if self.isClose:
            newPath.close()
        return newPath
        
    def reverse(self):
        rPath = BezierPath()
        rPath.start()
        rStartPos = Point()
        for ctrl in reversed(self._ctrlList):
            rPath.connect(p1=ctrl.p2-ctrl.pos, p2=ctrl.p1-ctrl.pos, pos=-ctrl.pos)
            rStartPos += ctrl.pos
        rPath.setStartPos(self._startPos + rStartPos)
        if self.isClose():
            rPath.close()

        return rPath
    
    def endPos(self):
        pos = self._startPos
        for ctrl in self._ctrlList:
            pos += ctrl.pos
        return pos

    def containsPos(self, pos):
        PIX_OFFSET = 3
        RADIAN = math.pi/90
        OFFSET = .01

        count = 0
        if self.isClose():
            path = copy.deepcopy(self)
            sPos = self.startPos()
            i = 0
            r = 0
            while i < len(path):
                if sPos.distanceOffset(pos, OFFSET):
                    return True
                if sPos.y < pos.y or abs(sPos.x - pos.x) > PIX_OFFSET:
                    sPos += path[i].pos
                    i += 1
                else:
                    i = 0
                    r += RADIAN
                    path = self.rotate(r, pos)
                    sPos = path.startPos()

                    if r > math.pi * 2:
                        raise Exception('The graph is too small!')

            for ctrl in path:
                roots = ctrl.roots(x=pos.x, pos=sPos, offset=OFFSET, interval=[0, 1])
                for t in roots:
                    cPosY = ctrl.valueAt(t, sPos, False).y
                    if abs(cPosY - pos.y) < .01:
                        return True
                    if cPosY > pos.y:
                        if len(roots) == 1:
                            ePosx = ctrl.pos.x + sPos.x
                            if (ePosx < pos.x and pos.x < sPos.x) or (ePosx > pos.x and pos.x > sPos.x):
                                count += 1
                        else:
                            count += 1
                sPos += ctrl.pos

        return int(count) % 2 == 1
    
    def rotations(self):
        center = self.boundingBox().center()

        t = 0
        pos = self.startPos()
        for ctrl in self:
            p1 = pos - center
            # p2 = ctrl.pos + p1
            p2 = ctrl.valueAt(.5, p1)
            v = p1.x * p2.y - p2.x * p1.y
            if v < 0:
                t -= 1
            elif v > 0:
                t += 1
            pos += ctrl.pos

        if t < 0:
            return -1
        elif t > 0:
            return 1
        return 0            

    def toOutline(self, strokeWidth, jointype='Round', captype='Butt'):
        radius = strokeWidth / 2
        newPath = [BezierPath(),  BezierPath()]

        def join(ctrl1, ctrl2, normals, preNormals):
            tangent = -normals.perpendicular()
            preTangent = -preNormals.perpendicular()

            def joinProcess(path1, path2, ctrl1, ctrl2, en, sn, radian):
                ePos = -sn + en
                if jointype == 'Miter':
                    path1.connect(ePos)
                    path1.append(ctrl1)
                elif jointype == 'Round':
                    mNum = arcMagicNumber(radian)
                    path1.connect(p1=preTangent*mNum, p2=ePos-(tangent*mNum), pos=ePos)
                    path1.append(ctrl1)
                else:
                    raise Exception('Undefine join type: ' + jointype)
                iList1, iList2 = path2[-1].intersections(Point(), ctrl2, path2[-1].pos + sn - en)

                if len(iList1) or 1:
                    path2[-1] = path2[-1].splitting(max(iList1))[0]
                    path2.append(ctrl2.splitting(min(iList2))[1])

            if len(newPath[0]) == 0:
                newPath[0].append(ctrl1)
                newPath[1].append(ctrl2)
                return

            radian = normals.rotate(-preNormals.radian()).radian()
            if abs(radian) > 3.1415926:
                d = ctrl1.rotations()
                if d == 0:
                    d = newPath[0][-1].rotations()
                    
                if d > 0:
                    radian = -abs(radian)
                else:
                    radian = abs(radian)
            if radian > 0:
                joinProcess(newPath[0], newPath[1], ctrl1, ctrl2, normals, preNormals, radian)
            elif radian < 0:
                joinProcess(newPath[1], newPath[0], ctrl2, ctrl1, -normals, -preNormals, -radian)
            else:
                newPath[0].append(ctrl1)
                newPath[1].append(ctrl2)
            
        startPos = self.startPos()
        
        preNormals, prePos = self[0].normals(0, radius, startPos)
        newPath[0].start(prePos + preNormals)
        newPath[1].start(prePos - preNormals)

        for bCtrl in self._ctrlList:
            pOffset = 2 / bCtrl.approximatedLength(12)

            tg = bCtrl.tangents(0)
            roots = bCtrl.extermes(-(tg[0]-tg[1]).radian())
            splitValues = []
            for t in roots[0] + roots[1]:
                if t < 0+pOffset or t > 1-pOffset:
                    continue
                splitValues.append(t)
            splitValues.sort()
            #splitValues = splitValues[1:]

            temp = []
            sValue = 0
            for t in splitValues:
                if t - sValue < pOffset:
                    continue
                temp.append((t+sValue) / 2)
                temp.append(t)
                sValue = t
            if sValue and sValue + pOffset < 1:
                temp.append((1+sValue) / 2)
            temp.append(1)
            splitValues = temp
            del temp

            if bCtrl.isLine():
                normals = bCtrl.pos.normalization(radius).perpendicular()
                join(bCtrl, bCtrl, normals, preNormals)
                preNormals = normals
            else:
                sValue = 0
                sNormals, sPos = bCtrl.normals(0, radius, startPos)
                for t in splitValues:
                    eNormals, ePos = bCtrl.normals(t, radius, startPos)

                    currentCtrl = bCtrl.splitting(sValue)[1].splitting((t-sValue) / (1-sValue))[0]
                    cpList = currentCtrl.casteljauPoints(.5, sPos)

                    mNormals = (cpList['n2'][1] - cpList['n1']).normalization(radius)
                    if mNormals:
                        mNormals = mNormals.perpendicular()
                    else:
                        mNormals = (ePos - sPos).normalization(radius).perpendicular()
                    mPos = cpList['n1']
                    
                    intersectPos = intersection(sPos, sPos+sNormals, ePos, ePos+eNormals)
                    if not intersectPos:
                        intersectPos =  (sPos - ePos) / 2

                    ratio1 = (mPos+mNormals).distance(intersectPos) / mPos.distance(intersectPos)
                    eCtrlPos1 = (ePos+eNormals) - (sPos+sNormals)

                    ratio2 = (mPos-mNormals).distance(intersectPos) / mPos.distance(intersectPos)
                    eCtrlPos2 = (ePos-eNormals) - (sPos-sNormals)

                    def newCtrlGen(ratio, eCtrlPos):
                        if ratio < 1:
                            # 这是一个有缺陷的缩小处理方法，也许以后会修正……的吧？
                            ctl = currentCtrl.scale(ratio)
                            for v in ctl.roots(x=eCtrlPos.x, y=eCtrlPos.y):
                                if v > 0 and v < .85:
                                    if abs(ctl.valueAt(v).distance(eCtrlPos)) < 3:
                                        ctl = ctl.splitting(v)[0]
                                        #ctl.p2 = eCtrlPos - ctl.pos
                                        ctl.pos = eCtrlPos
                                        return ctl
                        return BezierCtrl(p1=currentCtrl.p1.scale(ratio), p2=(currentCtrl.p2-currentCtrl.pos).scale(ratio)+eCtrlPos, pos=eCtrlPos)

                    c1 = newCtrlGen(ratio1, eCtrlPos1)
                    c2 = newCtrlGen(ratio2, eCtrlPos2)

                    if sValue == 0:
                        join(c1, c2, sNormals, preNormals)
                    else:
                        newPath[0].append(c1)
                        newPath[1].append(c2)

                    sValue = t
                    sNormals = eNormals
                    sPos = ePos
                preNormals = sNormals
            startPos += bCtrl.pos

        if self.isClose():
            tailCtrl = []
            for path in newPath:
                tailCtrl.append(path[0])
                path.setStartPos(path.startPos() + path[0].pos)
                path.popFront()

            normals,_ = self[0].normals(0, radius)
            join(tailCtrl[0], tailCtrl[1], normals, preNormals)
            
            if not(newPath[0].endPos().distanceOffset(newPath[0].startPos(), .1) and newPath[1].endPos().distanceOffset(newPath[1].startPos(), .1)):
                raise Exception('Closing path error in to outline!')

            newPath[0].close()
            newPath[1].close()
            newPath[1] = newPath[1].reverse()
        else:
            path = newPath[1].reverse()
            p2 = path.startPos()
            endPos = newPath[0].endPos()
            if captype == 'Butt':
                newPath[0].connect(p2 - endPos)
                newPath[0].connectPath(path)
                path = newPath[0]
                #path.connect(path.startPos() - p1)
            elif captype == 'Round':
                tangent = -preNormals.perpendicular()
                newPath[0].connect(p1=tangent*SEMICIRCLE, p2=tangent-preNormals*(1-SEMICIRCLE), pos=tangent-preNormals)
                newPath[0].connect(p2=-preNormals-tangent*(1-SEMICIRCLE), pos=-preNormals-tangent, s=True)
                newPath[0].connectPath(path)
                
                preNormals,_ = newPath[0][-1].normals(1, radius)
                tangent = -preNormals.perpendicular()
                newPath[0].connect(p1=tangent*SEMICIRCLE, p2=tangent-preNormals*(1-SEMICIRCLE), pos=tangent-preNormals)
                newPath[0].connect(p2=-preNormals-tangent*(1-SEMICIRCLE), pos=-preNormals-tangent, s=True)
                path = newPath[0]
            else:
                raise Exception('Undefine cap type: ' + captype)

            if not path.endPos().distanceOffset(path.startPos(), .1):
                raise Exception('Closing path error in to outline!')

            path.close()
            newPath = [path]

        return newPath

    def separateFromPath(self, path):
        OFFSET = .5
        if not (self.isClose() and path.isClose()):
            raise Exception('Path not closed!')

        paths = [copy.deepcopy(self), copy.deepcopy(path)]

        iList = [[], []]

        index1 = 0
        pos1 = paths[0].startPos()
        values = [None, None]
        while index1 < len(paths[0]):
            index2 = 0
            pos2 = paths[1].startPos()
            while index2 < len(paths[1]):
                values[0], values[1] = paths[0][index1].intersections(pos1, paths[1][index2], pos2, [0, 1])
                for vs in values:
                    vs.sort()
                if len(values[0]):
                    t = values[0][0]
                    temp = paths[0][index1].splitting(t)
                    for i in [0, 1]:
                        if not temp[i].isValid(OFFSET):
                            temp.pop(i)
                            break
                    if len(temp) == 2:
                        paths[0].insert(index1+1, temp[1])
                        paths[0][index1] = temp[0]
                        for i in range(0, len(iList[0])):
                            if iList[0][i] >= index1 : iList[0][i] += 1
                        iList[0].append(index1)
                    else:
                        if t < .5:
                            preIndex = index1-1
                            if preIndex < 0:
                                preIndex = len(paths[0]) - 1
                            if iList[0].count(preIndex) == 0:
                                iList[0].append(preIndex)
                        else:
                            if iList[0].count(index1) == 0:
                                iList[0].append(index1)
                if len(values[1]):
                    t = values[1][0]
                    temp = paths[1][index2].splitting(t)
                    for i in [0, 1]:
                        if not temp[i].isValid(OFFSET):
                            temp.pop(i)
                            break
                    if len(temp) == 2:
                        paths[1].insert(index2+1, temp[1])
                        paths[1][index2] = temp[0]
                        for i in range(0, len(iList[1])):
                            if iList[1][i] >= index2 : iList[1][i] += 1
                        iList[1].append(index2)
                    else:
                        if t < .5:
                            preIndex = index2-1
                            if preIndex < 0:
                                preIndex = len(paths[1]) - 1
                            if iList[1].count(preIndex) == 0:
                                iList[1].append(preIndex)
                        else:
                            if iList[1].count(index2) == 0:
                                iList[1].append(index2)
                pos2 += paths[1][index2].pos
                index2 += 1
            pos1 += paths[0][index1].pos
            index1 += 1

        newPaths = [[], []]
        n = 0
        for oldPath in paths:
            pos = oldPath.startPos()
            j = 0
            iList[n].sort()
            for i in iList[n]:
                newPaths[n].append(BezierPath())
                newPaths[n][-1].start(pos)
                while j <= i:
                    newPaths[n][-1].append(oldPath[j])
                    pos += oldPath[j].pos
                    j += 1
            if j < len(oldPath):
                temp = BezierPath()
                temp.start(pos)
                while j < len(oldPath):
                    temp.append(oldPath[j])
                    j += 1
                if len(newPaths[n]):
                    temp.connectPath(newPaths[n][0])
                    newPaths[n][0] = temp
                else:
                    temp.close()
                    newPaths[n].append(temp)
            n = 1

        return newPaths

class BezierShape(object):
    def __init__(self) -> None:
        self._pathList = []

    def __iter__(self):
        return iter(self._pathList)

    def __getitem__(self, index):
        return self._pathList[index]

    def __setitem__(self, index, value:BezierPath):
        self._pathList[index] = value

    def __len__(self):
        return len(self._pathList)

    def add(self, bezierPath = BezierPath()):
        self._pathList.append(bezierPath)
        
    def extend(self, iterable):
        self._pathList.extend(iterable)

    def toSvgElement(self, arrt={}):
        attrStr = ''
        for aPath in self._pathList:
            attrStr += 'M {},{} '.format(round(aPath.startPos().x, 3), round(aPath.startPos().y, 3))

            for bCtrl in aPath:
                if bCtrl.p1.isOrigin() and bCtrl.p2.isOrigin():
                    if not bCtrl.pos.x:
                        attrStr += 'v {} '.format(round(bCtrl.pos.y, 3))
                    elif not bCtrl.pos.y:
                        attrStr += 'h {} '.format(round(bCtrl.pos.x, 3))
                    else:
                        attrStr += 'l {},{} '.format(round(bCtrl.pos.x, 3), round(bCtrl.pos.y, 3))
                else:
                    attrStr += 'c {},{} {},{} {},{} '.format(round(bCtrl.p1.x, 3), round(bCtrl.p1.y, 3), round(bCtrl.p2.x, 3), round(bCtrl.p2.y, 3), round(bCtrl.pos.x, 3), round(bCtrl.pos.y, 3))

            if aPath.isClose():
                attrStr += 'z '                    
    
        arrt['d'] = attrStr
        elem = ET.Element('path', arrt)#re.sub(_re_zero, r'\1\2', attrStr) })
        elem.tail = '\n'
        return elem
    
    def boundingBox(self):
        rect = Rect(Point(99999, 99999), Point())
        for path in self._pathList:
            box = path.boundingBox()
            if box.left < rect.left: rect.left = box.left
            if box.bottom < rect.bottom: rect.bottom = box.bottom
            if box.right > rect.right: rect.right = box.right
            if box.top > rect.top: rect.top = box.top

        return rect
        
    def rotate(self, radian, center:Point=Point()):
        newShape = BezierShape()
        for path in self._pathList:
            newShape.add(path.rotate(radian, center))
        return newShape

    def union(self, shape):
        pass

def createPathfromSvgElem(elem, tag=''):
    if(tag == ''):
        tag = elem.tag

    path = BezierShape()
    bezier = BezierPath()
    if tag == 'path':
        pos = Point()
        for avg in re.finditer(_re_args, elem.get('d')):
            numList = re.finditer(_re_num, avg.group())
            com = avg.group()[0]
            if com == 's':
                bezier.connect(p2=_getPointFromReMatch(numList), pos=_getPointFromReMatch(numList), s=True)
            elif com == 'c':
                bezier.connect(p1=_getPointFromReMatch(numList), p2=_getPointFromReMatch(numList), pos=_getPointFromReMatch(numList))
            elif com == 'l':
                bezier.connect(_getPointFromReMatch(numList))
            elif com == 'h':
                bezier.connect(Point(next(numList).group(), 0))
            elif com == 'v':
                bezier.connect(Point(0, next(numList).group()))
            elif com == 'S':
                bezier.connect(p2=_getPointFromReMatch(numList) - pos, pos=_getPointFromReMatch(numList) - pos, s=True)
            elif com == 'C':
                bezier.connect(p1=_getPointFromReMatch(numList) - pos, p2=_getPointFromReMatch(numList) - pos, pos=_getPointFromReMatch(numList) - pos)
            elif com == 'L':
                bezier.connect(_getPointFromReMatch(numList) - pos)
            elif com == 'H':
                bezier.connect(Point(strToNum(next(numList).group()) - pos.x, 0))
            elif com == 'V':
                bezier.connect(Point(0, strToNum(next(numList).group()) - pos.y))
            elif com == 'M':
                bezier.start(_getPointFromReMatch(numList))
                pos = bezier.startPos()
                continue
            elif com == 'z':
                bezier.close()
                path.add(bezier)
                bezier = BezierPath()
                pos = Point()
                continue
            else:
                raise AttributeError
            
            if len(bezier):
                pos = bezier.endPos()
        if (not bezier.isClose()) and (len(bezier)):
            path.add(bezier)
    elif tag == 'polyline':
        matchs = re.finditer(_re_num, elem.get('points'))
        pos = _getPointFromReMatch(matchs)
        bezier.start(pos)
        
        while True:
            try:
                p = _getPointFromReMatch(matchs)
                bezier.connect(p - pos)
                pos = p
            except StopIteration:
                break
        
        path.add(bezier)
    elif tag == 'line':
        p1 = Point(elem.get('x1'), elem.get('y1'))
        p2 = Point(elem.get('x2'), elem.get('y2'))

        bezier.start(p1)
        bezier.connect(p2 - p1)
        path.add(bezier)
    elif tag == 'circle':
        r = strToNum(elem.get('r'))
        center = Point(elem.get('cx'), elem.get('cy'))

        bezier.start(Point(center.x, center.y - r))
        bezier.connect(p1=Point(r*SEMICIRCLE, 0), p2=Point(r, r-r*SEMICIRCLE), pos=Point(r, r))
        bezier.connect(p2=Point(-r+r*SEMICIRCLE, r), pos=Point(-r, r), s=True)
        bezier.connect(p2=Point(-r, -r+r*SEMICIRCLE), pos=Point(-r, -r), s=True)
        bezier.connect(p2=Point(r-r*SEMICIRCLE, -r), pos=Point(r, -r), s=True)
        bezier.close()
        path.add(bezier)
    elif tag == 'rect':
        width = strToNum(elem.get('width'))
        height = strToNum(elem.get('height'))

        bezier.start(Point(elem.get('x', 0), elem.get('y', 0)))
        bezier.connect(Point(width, 0))
        bezier.connect(Point(0, height))
        bezier.connect(Point(-width, 0))
        bezier.connect(Point(0, -height))
        bezier.close()
        path.add(bezier)
    else:
        raise RuntimeError('Not definde!')
    
    return path

class GroupShape(object):
    def __init__(self, shape:BezierShape=BezierShape()) -> None:
        def grouping(path, group):
            apos = path[0].valueAt(.5, path.startPos())
            for i in range(0, len(group)):
                p, g = group[i]
                if p.containsPos(apos):
                    grouping(path, g)
                    return
                elif path.containsPos(p[0].valueAt(.5, p.startPos())):
                    group[i] = [path, [group[i]]]
                    return
            group.append([path, []])

        def direction(d, list):
            for i in range(0, len(list)):
                r = list[i][0].rotations()
                if r != d and r != 0:
                    list[i][0] = list[i][0].reverse()
                direction(-d, list[i][1])

        group = []
        for path in shape:
            if path.isClose():
                grouping(path, group)

        direction(-1, group)
        self._group = group

    def __or__(self, group):
        def anding(b1, ws1, b2, ws2):
            tempB = b1 | b2
            tempW = []

            incGroup = BezierShape()
            incGroup._pathList = tempB
            incGroup = GroupShape(incGroup)._group
            if len(incGroup) == 2:
                return [False, [b2, ws2]]
            for w in incGroup[0][1]:
                tempW.append(w)
                
            for w1, _ in ws1:
                temp = w1 - b2
                if len(temp) != 0:
                    tempW.append([temp[0], _])
                if len(temp) > 1:
                    for shape in temp[1:]:
                        if shape.rotations() == 1:
                            tempW.append([shape, []])
                        else:
                            tempW[-1][1].append([temp[1], []])
                for w2, _ in ws2:
                    for u in w2&w1:
                        tempW.append([u, []])
            for w2, _ in ws2:
                temp = w2 - b1
                if len(temp) != 0:
                    tempW.append([temp[0], _])
                if len(temp) > 1:
                    for shape in temp[1:]:
                        if shape.rotations() == 1:
                            tempW.append([shape, []])
                        else:
                            tempW[-1][1].append([temp[1], []])

            return [True, [incGroup[0][0], tempW]]

        if len(self._group) == 0:
            return group
        elif len(group._group) == 0:
            return self

        oldGroup = []
        newGroup = copy.deepcopy(group._group)
        for p1, g1 in self._group:
            i = 0
            hIndex = None
            while i < len(newGroup):
                p2, g2 = newGroup[i]
                h, newGroup[i] = anding(p1, g1, p2, g2)
                if h:
                    p1, g1 = newGroup[i]
                    if hIndex != None:
                        newGroup.pop(hIndex)
                        hIndex = i-1
                    else:
                        hIndex = i
                        i += 1
                else:
                    i += 1
            if hIndex == None:
                oldGroup.append([p1, g1])

        ng = GroupShape()
        ng._group = newGroup + oldGroup
        return ng

    def toShape(self):
        def unGroup(group, list):
            for p, g in group:
                list.append(p)
                unGroup(g, list)

        shape = BezierShape()
        unGroup(self._group, shape._pathList)

        return shape