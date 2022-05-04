# -*- coding: utf-8 -*-

from clsvg import svgfile
from clsvg import bezierShape

import os
FILE_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_FOLDER = os.path.join(FILE_PATH, 'testFile')
TEST_OVER_FOLDER = os.path.join(FILE_PATH, 'testFile/over/')
TARGET_FILE = os.path.join(FILE_PATH, 'test.svg')

MAIN_PATH_STYLE = '.st0{fill:none;stroke:#000000;stroke-width:2;}'

def testShapeToPath():
    targetFile = 'shape_to_path.svg'

    tree = svgfile.parse(os.path.join(TEST_FOLDER, targetFile))
    root = tree.getroot()

    newRoot = svgfile.ET.Element(root.tag, root.attrib)
    newRoot.text = '\n'
    styleElem = svgfile.ET.Element('style', { 'type': 'text/css' })
    styleElem.text = MAIN_PATH_STYLE
    styleElem.tail = '\n'
    newRoot.append(styleElem)

    for child in root:
        tag = svgfile.unPrefix(child.tag)
        if(tag != 'style'):
            elem = bezierShape.createPathfromSvgElem(child, tag).toSvgElement()
            elem.set('class', 'st0')
            newRoot.append(elem)

    newTree = svgfile.ET.ElementTree(newRoot)
    newTree.write(os.path.join(TEST_OVER_FOLDER, targetFile), encoding = "utf-8", xml_declaration = True)

def testCasteljau():
    targetFile = 'casteljau.svg'
    
    tree = svgfile.parse(os.path.join(TEST_FOLDER, targetFile))
    root = tree.getroot()

    newRoot = svgfile.ET.Element(root.tag, root.attrib)
    newRoot.text = '\n'
    styleElem = svgfile.ET.Element('style', { 'type': 'text/css' })
    styleElem.text = MAIN_PATH_STYLE
    styleElem.tail = '\n'
    newRoot.append(styleElem)

    for child in root:
        tag = svgfile.unPrefix(child.tag)
        if tag != 'style':
            path = bezierShape.createPathfromSvgElem(child, tag)
            pathElem = path.toSvgElement()
            pathElem.set('class', 'st0')
            newRoot.append(pathElem)
            for bPath in path:
                pos = bPath.startPos()
                for bCtrl in bPath:
                    ctrlPosList = bCtrl.casteljauPoints(.5, pos)
                    newRoot.append(svgfile.createLineElem(pos, pos+bCtrl.p1, { 'stroke-width': '1', 'stroke': "rgb(100,100,250)" }))
                    newRoot.append(svgfile.createLineElem(pos+bCtrl.p1, pos+bCtrl.p2, { 'stroke-width': '1', 'stroke': "rgb(100,100,250)" }))
                    newRoot.append(svgfile.createLineElem(pos+bCtrl.p2, pos+bCtrl.pos, { 'stroke-width': '1', 'stroke': "rgb(100,100,250)" }))
                    for p in ctrlPosList['n3']:# + ctrlP['n2']:
                        newRoot.append(svgfile.createCircleElem(p, 4, {'fill': 'blue'}))

                    newRoot.append(svgfile.createLineElem(ctrlPosList['n3'][0], ctrlPosList['n3'][1], { 'stroke-width': '1', 'stroke': "rgb(250,100,100)" }))
                    newRoot.append(svgfile.createLineElem(ctrlPosList['n3'][1], ctrlPosList['n3'][2], { 'stroke-width': '1', 'stroke': "rgb(250,100,100)" }))
                    for p in ctrlPosList['n2']:
                        newRoot.append(svgfile.createCircleElem(p, 4, {'fill': 'red'}))
                            
                    newRoot.append(svgfile.createLineElem(ctrlPosList['n2'][0], ctrlPosList['n2'][1], { 'stroke-width': '1', 'stroke': "rgb(100,250,100)" }))
                    newRoot.append(svgfile.createCircleElem(ctrlPosList['n1'], 4, {'fill': 'green'}))
                    pos += bCtrl.pos

    newTree = svgfile.ET.ElementTree(newRoot)
    newTree.write(os.path.join(TEST_OVER_FOLDER, targetFile), encoding = "utf-8", xml_declaration = True)

def testSimplified():
    targetFile = 'simplified.svg'

    tree = svgfile.parse(os.path.join(TEST_FOLDER, targetFile))
    root = tree.getroot()

    newRoot = svgfile.ET.Element(root.tag, root.attrib)
    newRoot.text = '\n'
    styleElem = svgfile.ET.Element('style', { 'type': 'text/css' })
    styleElem.text = MAIN_PATH_STYLE
    styleElem.tail = '\n'
    newRoot.append(styleElem)

    for child in root:
        tag = svgfile.unPrefix(child.tag)
        if tag != 'style':
            path = bezierShape.createPathfromSvgElem(child, tag)
            pathElem = path.toSvgElement()
            pathElem.set('class', 'st0')
            newRoot.append(pathElem)
            for bPath in path:
                startPos = bPath.startPos()
                for bCtrl in bPath:
                    for t in [.2, .4, .6, .8, 1]:
                        endPos = bCtrl.valueAt(t, bPath.startPos())
                        newRoot.append(svgfile.createLineElem(startPos, endPos, { 'stroke-width': '4', 'stroke': "rgb(255,150,150)" }))
                        startPos = endPos

    newTree = svgfile.ET.ElementTree(newRoot)
    newTree.write(os.path.join(TEST_OVER_FOLDER, targetFile), encoding = "utf-8", xml_declaration = True)

def testSplitting():
    targetFile = 'splitting.svg'

    tree = svgfile.parse(os.path.join(TEST_FOLDER, targetFile))
    root = tree.getroot()

    newRoot = svgfile.ET.Element(root.tag, root.attrib)
    newRoot.text = '\n'
    styleElem = svgfile.ET.Element('style', { 'type': 'text/css' })
    styleElem.text = MAIN_PATH_STYLE
    styleElem.tail = '\n'
    newRoot.append(styleElem)

    for child in root:
        tag = svgfile.unPrefix(child.tag)
        if tag != 'style':
            path = bezierShape.createPathfromSvgElem(child, tag)
            for bPath in path:
                n = 0
                while(n < len(bPath)):
                    splitCtrls = bPath[n].splitting(.5)
                    bPath[n] = splitCtrls[0]
                    bPath.insert(n+1, splitCtrls[1])
                    n += 2
            pathElem = path.toSvgElement()
            pathElem.set('class', 'st0')
            newRoot.append(pathElem)

    newTree = svgfile.ET.ElementTree(newRoot)
    newTree.write(os.path.join(TEST_OVER_FOLDER, targetFile), encoding = "utf-8", xml_declaration = True)

def testTangentsAndNormals():
    targetFile = 'tangents_and_normals.svg'

    tree = svgfile.parse(os.path.join(TEST_FOLDER, targetFile))
    root = tree.getroot()

    newRoot = svgfile.ET.Element(root.tag, root.attrib)
    newRoot.text = '\n'
    styleElem = svgfile.ET.Element('style', { 'type': 'text/css' })
    styleElem.text = '.st0{fill:none;stroke:#aaaaaa;stroke-width:1;}'
    styleElem.tail = '\n'
    newRoot.append(styleElem)

    for child in root:
        tag = svgfile.unPrefix(child.tag)
        if tag != 'style':
            path = bezierShape.createPathfromSvgElem(child, tag)
            pathElem = path.toSvgElement()
            pathElem.set('class', 'st0')
            newRoot.append(pathElem)
            for bPath in path:
                startPos = bPath.startPos()
                for bCtrl in bPath:
                    t = 0
                    while t <= 1:
                        tLine = bCtrl.tangents(t, 24, startPos)
                        nLine = bCtrl.normals(t, 24, startPos)
                        newRoot.append(svgfile.createLineElem(tLine[0], tLine[1], { 'stroke-width': '2', 'stroke': "blue" }))
                        newRoot.append(svgfile.createLineElem(nLine[1], nLine[0] + nLine[1], { 'stroke-width': '2', 'stroke': "green" }))
                        newRoot.append(svgfile.createCircleElem(tLine[0], 4, {'fill': 'red'}))
                        t += .2
                    startPos += bCtrl.pos

    newTree = svgfile.ET.ElementTree(newRoot)
    newTree.write(os.path.join(TEST_OVER_FOLDER, targetFile), encoding = "utf-8", xml_declaration = True)

def testExtermesFinding():
    targetFile = 'extermes_finding.svg'

    tree = svgfile.parse(os.path.join(TEST_FOLDER, targetFile))
    root = tree.getroot()

    newRoot = svgfile.ET.Element(root.tag, root.attrib)
    newRoot.text = '\n'
    styleElem = svgfile.ET.Element('style', { 'type': 'text/css' })
    styleElem.text = MAIN_PATH_STYLE
    styleElem.tail = '\n'
    newRoot.append(styleElem)
    
    for child in root:
        tag = svgfile.unPrefix(child.tag)
        if tag != 'style':
            path = bezierShape.createPathfromSvgElem(child, tag)
            newRoot.append(path.toSvgElement({ 'class': 'st0' }))
            for bPath in path:
                startPos = bPath.startPos()
                for bCtrl in bPath:
                    tg = bCtrl.tangents(0)
                    roots = bCtrl.extermes(-(tg[0]-tg[1]).radian())
                    for t in roots[0]:
                        if t < 0 or t > 1:
                            continue
                        aPos = bCtrl.valueAt(t, startPos)
                        newRoot.append(svgfile.createCircleElem(aPos, 4, {'fill': 'green'}))
                    for t in roots[1]:
                        if t < 0 or t > 1:
                            continue
                        aPos = bCtrl.valueAt(t, startPos)
                        newRoot.append(svgfile.createCircleElem(aPos, 4, {'fill': 'blue'}))
                        
                    if roots[2] and roots[2] > 0 and roots[2] < 1:
                        aPos = bCtrl.valueAt(roots[2], startPos)
                        newRoot.append(svgfile.createCircleElem(bCtrl.valueAt(roots[2], startPos), 4, {'fill': 'red'}))
                    if roots[3] and roots[3] > 0 and roots[3] < 1:
                        aPos = bCtrl.valueAt(roots[3], startPos)
                        newRoot.append(svgfile.createCircleElem(bCtrl.valueAt(roots[3], startPos), 4, {'fill': 'red'}))

                    startPos += bCtrl.pos

    newTree = svgfile.ET.ElementTree(newRoot)
    newTree.write(os.path.join(TEST_OVER_FOLDER, targetFile), encoding = "utf-8", xml_declaration = True)

def testBoundingBox():
    targetFile = 'bounding_box.svg'

    tree = svgfile.parse(os.path.join(TEST_FOLDER, targetFile))
    root = tree.getroot()

    newRoot = svgfile.ET.Element(root.tag, root.attrib)
    newRoot.text = '\n'
    styleElem = svgfile.ET.Element('style', { 'type': 'text/css' })
    styleElem.text = MAIN_PATH_STYLE
    styleElem.tail = '\n'
    newRoot.append(styleElem)
    
    for child in root:
        tag = svgfile.unPrefix(child.tag)
        if tag != 'style':
            path = bezierShape.createPathfromSvgElem(child, tag)
            newRoot.append(path.toSvgElement({ 'class': 'st0' }))
            rect = path.boundingBox()
            newRoot.append(svgfile.createRectElem(rect, { 'fill': 'none', 'stroke-width': '1', 'stroke': "grey" }))

    newTree = svgfile.ET.ElementTree(newRoot)
    newTree.write(os.path.join(TEST_OVER_FOLDER, targetFile), encoding = "utf-8", xml_declaration = True)

def testPathToOutline():
    targetFile = 'path_to_outline.svg'

    tree = svgfile.parse(os.path.join(TEST_FOLDER, targetFile))
    root = tree.getroot()

    newRoot = svgfile.ET.Element(root.tag, root.attrib)
    newRoot.text = '\n'
    styleElem = svgfile.ET.Element('style', { 'type': 'text/css' })
    styleElem.text = MAIN_PATH_STYLE
    styleElem.text += '.st1{fill:none;stroke:#ff0000;stroke-width:1;}'
    styleElem.tail = '\n'
    newRoot.append(styleElem)
    
    for child in root:
        tag = svgfile.unPrefix(child.tag)
        if tag != 'style':
            shape = bezierShape.createPathfromSvgElem(child, tag)
            newRoot.append(shape.toSvgElement({ 'class': 'st0' }))

            for bPath in shape:
                newShape = bezierShape.BezierShape()
                for path in bPath.toOutline(36, 'Round', 'Round'):
                    newShape.add(path)
                newRoot.append(newShape.toSvgElement({ 'class': 'st1' }))

    newTree = svgfile.ET.ElementTree(newRoot)
    newTree.write(os.path.join(TEST_OVER_FOLDER, targetFile), encoding = "utf-8", xml_declaration = True)

def testCurveAndLineIntersections():
    targetFile = 'curve_and_line_intersections.svg'

    tree = svgfile.parse(os.path.join(TEST_FOLDER, targetFile))
    root = tree.getroot()

    newRoot = svgfile.ET.Element(root.tag, root.attrib)
    newRoot.text = '\n'
    styleElem = svgfile.ET.Element('style', { 'type': 'text/css' })
    styleElem.text = MAIN_PATH_STYLE
    styleElem.tail = '\n'
    newRoot.append(styleElem)
    
    radian = None
    p1 = None
    for child in root:
        tag = svgfile.unPrefix(child.tag)
        if tag == 'line':
            shape = bezierShape.createPathfromSvgElem(child, tag)
            newRoot.append(shape.toSvgElement({ 'class': 'st0' }))

            p1 = bezierShape.Point(child.get('x1'), child.get('y1'))
            p2 = bezierShape.Point(child.get('x2'), child.get('y2'))
            radian = -p2.radian(p1)

    for child in root:
        tag = svgfile.unPrefix(child.tag)
        if tag == 'path':
            shape = bezierShape.createPathfromSvgElem(child, tag)
            newRoot.append(shape.toSvgElement({ 'class': 'st0' }))

            for bPath in shape:
                startP = bPath.startPos()
                for ctrl in bPath:
                    rctrl =  ctrl.rotate(radian)
                    p = startP.rotate(radian, p1)

                    for t in rctrl.roots(y=p1.y, pos=p):
                        if t >= 0 and t <= 1:
                            newRoot.append(svgfile.createCircleElem(ctrl.valueAt(t, startP), 4, {'fill': 'red'}))
                    startP += ctrl.pos

    newTree = svgfile.ET.ElementTree(newRoot)
    newTree.write(os.path.join(TEST_OVER_FOLDER, targetFile), encoding = "utf-8", xml_declaration = True)

def testPathIntersections():
    targetFile = 'path_intersections.svg'

    tree = svgfile.parse(os.path.join(TEST_FOLDER, targetFile))
    root = tree.getroot()

    newRoot = svgfile.ET.Element(root.tag, root.attrib)
    newRoot.text = '\n'
    styleElem = svgfile.ET.Element('style', { 'type': 'text/css' })
    styleElem.text = MAIN_PATH_STYLE
    styleElem.tail = '\n'
    newRoot.append(styleElem)
    
    for child in root:
        tag = svgfile.unPrefix(child.tag)
        if tag == 'g':
            shape1 = bezierShape.createPathfromSvgElem(child[0], svgfile.unPrefix(child[0].tag))
            shape2 = bezierShape.createPathfromSvgElem(child[1], svgfile.unPrefix(child[1].tag))
            newRoot.append(shape1.toSvgElement({ 'class': 'st0' }))
            newRoot.append(shape2.toSvgElement({ 'class': 'st0' }))

            pos1 = shape1[0].startPos()
            for ctl1 in shape1[0]:
                pos2 = shape2[0].startPos()
                for ctl2 in shape2[0]:
                    intersectValues = ctl1.intersections(pos1, ctl2, pos2)
                    for t in intersectValues[0]:
                        newRoot.append(svgfile.createCircleElem(ctl1.valueAt(t, pos1), 4, {'fill': 'red'}))
                    for t in intersectValues[1]:
                        newRoot.append(svgfile.createCircleElem(ctl2.valueAt(t, pos2), 4, {'fill': 'green'}))
                    pos2 += ctl2.pos
                pos1 += ctl1.pos

    newTree = svgfile.ET.ElementTree(newRoot)
    newTree.write(os.path.join(TEST_OVER_FOLDER, targetFile), encoding = "utf-8", xml_declaration = True)

def testRadianSegmentation():
    targetFile = 'radian_segmentation.svg'

    tree = svgfile.parse(os.path.join(TEST_FOLDER, targetFile))
    root = tree.getroot()

    newRoot = svgfile.ET.Element(root.tag, root.attrib)
    newRoot.text = '\n'
    styleElem = svgfile.ET.Element('style', { 'type': 'text/css' })
    styleElem.text = MAIN_PATH_STYLE
    styleElem.tail = '\n'
    newRoot.append(styleElem)
    
    for child in root:
        tag = svgfile.unPrefix(child.tag)
        if tag != 'style':
            shape = bezierShape.createPathfromSvgElem(child, tag)
            ctrlList, tList = shape[0][0].radianSegmentation(3.14159/90)
            print('Radian segmentation: {}'.format(tList))
            shape[0]._ctrlList = ctrlList

            newRoot.append(shape.toSvgElement({ 'class': 'st0' }))

    newTree = svgfile.ET.ElementTree(newRoot)
    newTree.write(os.path.join(TEST_OVER_FOLDER, targetFile), encoding = "utf-8", xml_declaration = True)

def test():
    targetFile = TARGET_FILE

    tree = svgfile.parse(os.path.join(TEST_FOLDER, targetFile))
    root = tree.getroot()

    newRoot = svgfile.ET.Element(root.tag, root.attrib)
    newRoot.text = '\n'
    styleElem = svgfile.ET.Element('style', { 'type': 'text/css' })
    styleElem.text = MAIN_PATH_STYLE
    styleElem.text += '.st1{fill:#ff0000;}'
    styleElem.tail = '\n'
    newRoot.append(styleElem)
    
    g = bezierShape.GroupShape()
    for child in root:
        tag = svgfile.unPrefix(child.tag)
        if tag != 'style':
            shape = bezierShape.BezierShape()
            shape.extend(bezierShape.createPathfromSvgElem(child, tag)[0].toOutline(36))
            g |= bezierShape.GroupShape(shape)

    newRoot.append(g.toShape().toSvgElement({ 'class': 'st1' }))

    newTree = svgfile.ET.ElementTree(newRoot)
    newTree.write(os.path.join(TEST_OVER_FOLDER, targetFile), encoding = "utf-8", xml_declaration = True)

if __name__ == '__main__':
    if not os.path.exists(TEST_OVER_FOLDER):
        os.mkdir(TEST_OVER_FOLDER)

    test()
    testBoundingBox()
    testCasteljau()
    testCurveAndLineIntersections()
    testExtermesFinding()
    testPathIntersections()
    testPathToOutline()
    testSimplified()
    testShapeToPath()
    testSplitting()
    testTangentsAndNormals()
    testRadianSegmentation()
    