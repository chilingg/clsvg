# -*- coding: utf-8 -*-

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

_namespaceList = dict()

def parse(path):
    global _namespaceList
    _namespaceList = dict([node for _, node in ET.iterparse(path, events=['start-ns'])])
    for k, v in _namespaceList.items():
        ET.register_namespace(k, v)
    
    return ET.parse(path)

def unPrefix(name, prefix = ''):
    global _namespaceList
    return name[len(_namespaceList[prefix])+2:]

def prefix(name, prefix = ''):
    global _namespaceList
    return "{%s}%s" % (_namespaceList[prefix], name)

def createCircleElem(cpos, r, attr={}):
    attr.update({ 'cx': str(round(cpos.x, 3)), 'cy': str(round(cpos.y, 3)), 'r': str(round(r, 3)) })
    elem = ET.Element('circle', attr)
    elem.tail = '\n'
    return elem
    
def createLineElem(pos1, pos2, attr={}):
    attr.update({ 'x1': str(round(pos1.x, 3)), 'x2': str(round(pos2.x, 3)), 'y1': str(round(pos1.y, 3)), 'y2': str(round(pos2.y, 3)) })
    elem = ET.Element('line', attr)
    elem.tail = '\n'
    return elem

def createRectElem(rect, attr={}):
    attr.update({ 'x': str(round(rect.left, 3)), 'y': str(round(rect.bottom, 3)), 'width': str(round(rect.width, 3)), 'height': str(round(rect.height, 3)) })
    elem = ET.Element('rect', attr)
    elem.tail = '\n'
    return elem