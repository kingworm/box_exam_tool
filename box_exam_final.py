import os
import argparse
import cv2
from exam_functions_final import get_boxes, delete_box, create_box
import matplotlib.pyplot as plt
import matplotlib.colors as col
from scipy import misc
import matplotlib.patches as patches

import numpy as np
import shutil
from matplotlib.widgets import RectangleSelector, EllipseSelector

parser = argparse.ArgumentParser(description='2D Box Examination')
parser.add_argument('--obj-img-dir', type=str, default='C:/Users/User/Desktop/2D_Data/small_object', help='object image directory')
parser.add_argument('--scn-img-dir', type=str, default='C:/Users/User/Desktop/2D_Data/small_scene', help='scene image directory')
parser.add_argument('--xml-dir', type=str, default='C:/Users/User/Google 드라이브/Select_Star_official/의뢰/RCV 연구실/code/rcv_1204/xml/test_1208', help='xml directory')
parser.add_argument('--img-path', type=str, default='', help='image path')

reset_dir='C:/Users/User/Google 드라이브/Select_Star_official/의뢰/RCV 연구실/code/rcv_1204/xml/reset_test'
good_dir='C:/Users/User/Google 드라이브/Select_Star_official/의뢰/RCV 연구실/code/rcv_1204/xml/good_test'

args = parser.parse_args()

colors = [(0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 0, 0), (0, 0, 255), (255, 0, 255), (153, 0, 204),
          (255, 0, 100), (51, 153, 204), (0, 0, 0), (255, 255, 255)]
parts = ['InsulatorA', 'InsulatorB', 'InsulatorC', 'InsulatorD', 'GILBS', 'ElectricPole', 'COS', 'Transformer', 'Tree',
         'Arrester', 'Insulator']

object_image_dir = args.obj_img_dir
scene_image_dir = args.scn_img_dir
xml_dir = args.xml_dir

xml_list = os.listdir(xml_dir)
xml_list.sort()
for lis in xml_list:
    if not 'xml' in lis:
        xml_list.remove(lis)

xml_path = ''
img_path = ''
labels = []
idx = 0
candidates = []
selected_box = None
box = None
box_name = 'GILBS'
fig, ax = plt.subplots(1)
create_mode = False


class CustomBoxBase(object):
    def __init__(self, x1, x2, y1, y2):
        self.x1, self.x2 = x1, x2
        self.y1, self.y2 = y1, y2
        self.xy = (x1, y1)
        self.name = ''
        self.type = 'bbox'
        self.w = x2 - x1
        self.h = y2 - y1


class RectangleHandler:

    def __init__(self, drs):
        self.drs = drs
        self.ax = drs[0].rect.axes

        self.cidpress = self.ax.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)

    def on_press(self, event):
        if event.inaxes != self.ax: return
        for dr in self.drs:
            rect = dr.rect
            contains, attrd = rect.contains(event)
            if contains:
                zorder = rect.zorder
                try:
                    if zorder > maxZorder:
                        maxZorder = zorder
                        rectToDrag = dr
                except NameError:
                    maxZorder = zorder
                    rectToDrag = dr
        try:
            if rectToDrag:
                rectToDrag.on_press(event)
        except UnboundLocalError:
            pass


def line_select_callback(eclick, erelease):
    global labels, colors, parts, box, box_name, xml_path, create_mode
    'eclick and erelease are the press and release events'
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    # print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
    # print(" The button you used were: %s %s" % (eclick.button, erelease.button))
    if create_mode:
        code = '#%02x%02x%02x' % colors[parts.index(box_name)]
        box = CustomBoxBase(x1, x2, y1, y2)
        box.name = box_name
        rect = patches.Rectangle(box.xy, box.w, box.h, linewidth=1, edgecolor=code, facecolor='none',
                                 picker=True)
        rect.set_label(box.name)
        ax.add_patch(rect)
        create_box(xml_path, box)
        print('box created to xml :', xml_path)
        create_mode = False


def toggle_selector(event):
    """
    1-GILBS
    3-ElectricPole
    4-Tree
    5-Transformer
    6-InsulatorA
    7-InsulatorB
    8-InsulatorC
    9-COS
    0-InsulatorD
    """

    global idx, xml_path, img_path, box_name, labels, idx, fig, create_mode, candidates

    if event.key == ',':
        print('show previous image')
        idx -= 1
        assert idx > -1
        plt.cla()
        xml_path, img_path, idx = get_data_path(idx)
        idx = plot_data(xml_path, img_path)
        return True

    if event.key == '.':
        print('show next image')
        idx += 1
        plt.cla()
        xml_path, img_path, idx = get_data_path(idx)
        idx = plot_data(xml_path, img_path)
        return True

    if event.key in ['B', 'b']:
        idx += 1
        p = reset_dir
        if os.path.exists(p):
            shutil.move(xml_path, p)
            print('xml file is moved to reset_1113 dir.')
            plt.cla()
            xml_path, img_path, idx = get_data_path(idx)
            idx = plot_data(xml_path, img_path)
            return True

    if event.key in ['N', 'n']:
        idx += 1
        p = good_dir
        if os.path.exists(p):
            shutil.move(xml_path, p)
            print('xml file is moved to good_1114 dir.')
            plt.cla()
            xml_path, img_path, idx = get_data_path(idx)
            idx = plot_data(xml_path, img_path)
            return True

    if event.key in ['M', 'm']:
        idx += 1
        p = 'xml/fix_good_1119'
        if os.path.exists(p):
            shutil.move(xml_path, p)
            print('xml file is moved to fix_good_1119 dir.')
            plt.cla()
            xml_path, img_path, idx = get_data_path(idx)
            idx = plot_data(xml_path, img_path)
            return True
    if event.key in ['Z', 'z']:
        candidates = []
        print('The selected boxes cleaned')
        return True
    if event.key in ['D', 'd']:
        if not candidates:
            print('NO selected boxes')
            return True
        else:
            candidates.sort(key=lambda x: x.get_width()*x.get_height())
            box_to_removed = candidates[0]
            print(box_to_removed)
            print(box_to_removed.get_label())
            name = box_to_removed.get_label()
            box_to_removed.set_visible(False)
            bbox = box_to_removed.get_bbox()
            delete_box(xml_path, box_to_removed.get_label(), 'bbox', bbox.xmin, bbox.ymin, bbox.xmax, bbox.ymax)
            candidates = []
            print('The box is deleted from xml.')
            return True

    if event.key in ['A', 'a']:
        if not create_mode:
            print('Box create mode activated')
            create_mode = True
            return True
        else:
            print('Box create mode deactivated')
            create_mode = False
            return True

    if event.key == '0':
        box_name = 'InsulatorD'
        print('color set to ', box_name)
        return True
    if event.key == '1':
        box_name = 'GILBS'
        print('color set to ', box_name)
        return True
    if event.key == '3':
        box_name = 'ElectricPole'
        print('color set to ', box_name)
        return True
    if event.key == '4':
        box_name = 'Tree'
        print('color set to ', box_name)
        return True
    if event.key == '5':
        box_name = 'Transformer'
        print('color set to ', box_name)
        return True
    if event.key == '6':
        box_name = 'InsulatorA'
        print('color set to ', box_name)
        return True
    if event.key == '7':
        box_name = 'InsulatorB'
        print('color set to ', box_name)
        return True
    if event.key == '8':
        box_name = 'InsulatorC'
        print('color set to ', box_name)
        return True
    if event.key == '9':
        box_name = 'COS'
        print('color set to ', box_name)
        return True

    print('Unspecified Key pressed.')


def on_pick(event):
    global candidates
    # print(event.artist,'pick_event')
    if isinstance(event.artist, patches.Rectangle):
        print('candidates appended.', event.artist)
        candidates.append(event.artist)
        return True
    else:
        print('Rectangle picker set default')
        candidates = []
        return False


def get_data_path(id):
    global xml_path, img_path
    xml_path = xml_dir + '/' + xml_list[id]
    object_img_path = object_image_dir + '/' + 'ext_' + xml_list[id].split('.xml')[0] + '.jpg'
    scene_img_path = scene_image_dir + '/' + 'small_' + xml_list[id].split('.xml')[0] + '.jpg'

    if os.path.exists(object_img_path):
        img_path = object_img_path
        return xml_path, img_path, id
    elif os.path.exists(scene_img_path):
        img_path = scene_img_path
        return xml_path, img_path, id
    else:
        print('No_image_%s' % xml_path)
        id += 1
        get_data_path(id)


def plot_data(xml_p, img_p):
    global ax, fig, idx, labels
    labels = []
    img = misc.imread(img_p)
    boxes = get_boxes(xml_p)
    i = 0
    plt.title(img_path + '/%d' % idx)
    for b in boxes:
        x1, y1, x2, y2 = b[0]
        name = b[1]
        color = colors[parts.index(name)]
        code = '#%02x%02x%02x' % colors[parts.index(name)]
        box_w = x2 - x1
        box_h = y2 - y1
        rect = patches.Rectangle((x1, y1), box_w, box_h, linewidth=1, edgecolor=code, facecolor='none',
                                 picker=True)
        rect.set_label(name)
        ax.add_patch(rect)
        if name not in labels:
            cv2.putText(img, name, (int(25), int(i + 75)), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 5)
            labels.append(name)
            i += 50
    toggle_selector.RS = RectangleSelector(ax, line_select_callback,
                                           drawtype='box', useblit=False, button=[1, 3],
                                           minspanx=10, minspany=10, spancoords='pixels',
                                           interactive=True)
    imgplot = plt.imshow(img, extent=[0, 1, 1, 0])
    return idx


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def main():
    global xml_path, img_path, idx, fig, ax, labels, colors, parts
    xml_path, img_path, idx = get_data_path(0)
    idx = plot_data(xml_path, img_path)
    fig.canvas.mpl_connect('pick_event', on_pick)
    plt.connect('key_press_event', toggle_selector)
    plt.show()


def onselect(eclick, erelease):
    "eclick and erelease are matplotlib events at press and release."
    print('startposition: (%f, %f)' % (eclick.xdata, eclick.ydata))
    print('endposition  : (%f, %f)' % (erelease.xdata, erelease.ydata))
    print('used button  : ', eclick.button)


if __name__ == '__main__':
    main()
