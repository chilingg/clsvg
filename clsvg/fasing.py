import json

from . import bezierShape as bs
from . import svgfile

def loadJson(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)

def writeTempGlyphFromShapes(shapes, fileName, tag, attrib):
    newRoot = svgfile.ET.Element(tag, attrib)
    newRoot.text = '\n'
    styleElem = svgfile.ET.Element('style', { 'type': 'text/css' })
    styleElem.text = '.st0{fill:#000000;}'
    styleElem.tail = '\n'
    newRoot.append(styleElem)

    for shape in shapes:
        newRoot.append(shape.toSvgElement({ 'class': 'st0' }))
    newTree = svgfile.ET.ElementTree(newRoot)
    newTree.write(fileName, encoding = "utf-8", xml_declaration = True)

def lineSymbol(p1, p2):
    if p1.x == p2.x:
        return 'v'
    elif p1.y == p2.y:
        return 'h'
    else:
        return 'd'

def direction(pos):
    if pos.x < 0 and pos.y > 0:
        return '1'
    elif pos.x < 0 and pos.y == 0:
        return '4'
    elif pos.x < 0 and pos.y < 0:
        return '7'
    elif pos.x == 0 and pos.y > 0:
        return '2'
    elif pos.x == 0 and pos.y == 0:
        return '5'
    elif pos.x == 0 and pos.y < 0:
        return '8'
    elif pos.x > 0 and pos.y > 0:
        return '3'
    elif pos.x > 0 and pos.y == 0:
        return '6'
    elif pos.x > 0 and pos.y < 0:
        return '9'
    else:
        raise Exception("posx")

def strokeDirection(bpath):
    text = ''
    for ctrl in bpath:
        text += direction(ctrl.pos)

    return text

def genStrucView(bpaths, p_map):
    def map_x(v):
        return p_map['h'].index(v)
    def map_y(v):
        return p_map['v'].index(v)

    view = [[[] for n in range(len(p_map['h']))] for m in range(len(p_map['v']))]

    for i, path in enumerate(bpaths):
        start = path.startPos()
        prePos = bs.Point(map_x(start.x), map_y(start.y))
        for j, ctrl in enumerate(path):
            sym = lineSymbol(bs.Point(), ctrl.pos)
            attrs = {
                'symbol': sym,
                'indexes': [i, j],
                'padding': False,
                'dir': direction(ctrl.pos),
                'se': 0
            }
            view[prePos.y][prePos.x].append(attrs)
            start += ctrl.pos
            currPos = bs.Point(map_x(start.x), map_y(start.y))
            attrs = {
                'symbol': sym,
                'indexes': [i, j],
                'padding': False,
                'dir': direction(ctrl.pos),
                'se': 1
            }
            view[currPos.y][currPos.x].append(attrs)

            attrs = {
                'symbol': sym,
                'indexes': [i, j],
                'padding': True
            }
            if sym == 'd':
                for y in range(min(prePos.y, currPos.y)+1, max(prePos.y, currPos.y)):
                    for x in range(min(prePos.x, currPos.x)+1, max(prePos.x, currPos.x)):
                        if (y != prePos.y or x != prePos.x) and (y != currPos.y or x != currPos.x):
                            view[y][x].append(attrs)
            else:
                if sym == 'h':
                    for k in range(min(prePos.x, currPos.x) + 1, max(prePos.x, currPos.x)):
                        view[currPos.y][k].append(attrs)
                if sym == 'v':
                    for k in range(min(prePos.y, currPos.y) + 1, max(prePos.y, currPos.y)):
                        view[k][currPos.x].append(attrs)

            prePos = currPos

    return view

def genCharData(data, scale):
    p_map = {'h': set(), 'v': set()}
    path_list = []
    
    for list in data['comb']["key_paths"]:
        prep = None
        path = []

        isHide = False
        for kp in list['points']:
            if kp['p_type'] == "Hide":
                isHide = True
                break
        if isHide: continue

        for kp in list['points']:
            pos = bs.Point(round(kp['point'][0] * scale), round(kp['point'][1] * scale))
            if pos != prep:
                p_map['h'].add(pos.x)
                p_map['v'].add(pos.y)
                path.append(pos)
                prep = pos
        if len(path) > 1:
            path_list.append(path)
            
    bpaths = []
    for points in path_list:
        bp = bs.BezierPath()
        bp.start(points[0])
        bp.extend([bs.BezierCtrl(points[j] - points[j-1]) for j in range(1, len(points))])
        if points[0] == points[-1]:
            bp.close()
        bpaths.append(bp)

    scale = data["info"]["scale"]
    p_map['h'] = sorted(p_map['h'])
    p_map['v'] = sorted(p_map['v'])
    view = genStrucView(bpaths, p_map)
    
    return {'bpaths': bpaths, 'view': view, 'scale': scale, 'p_map': p_map}
