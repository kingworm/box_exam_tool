import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
import cv2
import numpy as np
from PIL import Image


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def get_boxes(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    boxes = []
    for object in root.iter('object'):
        name = object.attrib['name']
        type = object.attrib['type']
        if type == 'bbox':
            box_dicts = object.find('bbox').attrib
            coord = np.array(
                [float(box_dicts['x1']), float(box_dicts['y1']), float(box_dicts['x2']), float(box_dicts['y2'])])
            boxes.append([coord, name])

    return boxes


def delete_box(xml_file, name, type, x1, y1, x2, y2):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    annotation=root.find('Annotation')
    for object in annotation.iter('object'):
        if name == object.attrib['name'] and type == object.attrib['type']:
            box_dicts = object.find('bbox').attrib
            if box_dicts['x1'] == str(x1) and box_dicts['y1'] == str(y1) and box_dicts['x2'] == str(x2) and box_dicts['y2'] == str(y2):
                annotation.remove(object)
                print('remove_success')
    indent(root)
    print(xml_file)
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)
    return True



def create_box(xml_file, box):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    annotation = root.find('Annotation')
    object = Element('object')
    object.attrib['name'] = box.name
    object.attrib['type'] = box.type
    bbox = Element(box.type)
    bbox.attrib['x1'] = str(box.x1)
    bbox.attrib['y1'] = str(box.y1)
    bbox.attrib['x2'] = str(box.x2)
    bbox.attrib['y2'] = str(box.y2)
    object.append(bbox)
    annotation.append(object)
    indent(root)
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)
    print('BOX is successfully created.')
    return True
# create_box(xml_file='_(추가)세원간29_1.xml',name="ElectricPole",type= "bbox",x1="0.426201922155", x2="0.66767836", y1="0.1390465406", y2="1.0")

colors = [(0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 0, 0), (0, 0, 255), (255, 0, 255), (153, 0, 204),
          (255, 0, 100), (51, 153, 204), (0, 0, 0), (255, 255, 255)]
parts = ['InsulatorA', 'InsulatorB', 'InsulatorC', 'InsulatorD', 'GILBS', 'ElectricPole', 'COS', 'Transformer', 'Tree',
         'Arrester', 'Insulator']


def resize(img, size):
    w, h = img.size
    if w > h:
        img = img.resize((int(w / h * size), size), resample=Image.LANCZOS)
    if w < h:
        img = img.resize((size, int(h / w * size)), resample=Image.LANCZOS)
    return img


def img_process(img, boxes):
    i = 0
    already = []
    for box in boxes:
        h, w = len(img), len(img[0])
        x1, y1, x2, y2 = box[0]
        name = box[1]
        color = colors[parts.index(name)]
        box_w = x2 - x1
        if box_w < 0.05:
            cv2.rectangle(img, (int(x1 * w), int(y1 * h)), (int(x2 * w), int(y2 * h)), color, 2)
        elif box_w < 0.25:
            cv2.rectangle(img, (int(x1 * w), int(y1 * h)), (int(x2 * w), int(y2 * h)), color, 2)
        else:
            cv2.rectangle(img, (int(x1 * w), int(y1 * h)), (int(x2 * w), int(y2 * h)), color, 5)
        if not name in already:
            cv2.putText(img, name, (int(25), int(i + 75)), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 5)
            already.append(name)
            i += 50

    return img


def check_double_box(boxes):
    box_coords = []
    box_names = []
    wrong_boxes = []
    for box in boxes:
        box_coords.append(box[0])
        box_names.append(box[1])
    box_coords = np.array(box_coords)
    for i in range(len(box_names)):
        box_coord = box_coords[i]
        compare = np.abs(box_coords - box_coord)
        for j in range(len(box_names)):
            comp = compare[j]
            if all(comp < 0.02) and not i == j:
                if box_names[i] == box_names[j]:
                    wrong_boxes.append([box_coord[0], box_coords[j][0], box_names[j]])
                break

    return wrong_boxes
