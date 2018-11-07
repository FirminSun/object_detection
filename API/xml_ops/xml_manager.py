from lxml.etree import Element, SubElement, tostring,ElementTree
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import os

class Xml_manager(object):
    def __init__(self,path,mode='load',labels=None,boxes=None,size=None):
        self._xml_path=path
        self.mode=mode
        self._labels=[] if not labels else labels #初始化
        self._boxes = [] if not boxes else boxes
        self._size = [] if not size else size
        self._tree=None
        self._root = None
        self.init() #建立必要的结构

    def init(self):
        if self.mode=='create': #创建模式
            self._root = Element('annotation')
            self._tree = ElementTree(self._root)
            self.create_structure()

        else:#加载模式
            self._tree = ET.parse(self._xml_path)
            self._root = self._tree.getroot()
            self.find_labels()
            self.find_boxes()

    def create_structure(self): #重建xml树结构
        self.load_default_attribute()
        self.load_path_attribute()
        self.load_size_attribute()
        self.load_obj_attribute()

    def load_default_attribute(self): #构建voc默认属性
        node_folder = SubElement(self._root, 'folder')
        node_folder.text = 'JPEGImages'
        node_segmented = SubElement(self._root, 'segmented')
        node_segmented.text = '0'

    def load_path_attribute(self): #构建路径属性
        node_filename = SubElement(self._root, 'filename')
        node_filename.text = os.path.split(self._xml_path)[1][:-4]+'.jpg'
        node_path = SubElement(self._root, 'path')
        node_path.text = os.path.split(self._xml_path)[0]

    def load_size_attribute(self): #构建图像尺寸属性
        node_size = SubElement(self._root, 'size')
        node_width=SubElement(node_size,'width')
        node_width.text=str(self._size[0])
        node_height = SubElement(node_size, 'height')
        node_height.text=str(self._size[1])
        node_depth = SubElement(node_size, 'depth')
        node_depth.text = str(self._size[2])

    def load_obj_attribute(self):  #构建图像物体属性
        for i,label in enumerate(self._labels):
            node_object = SubElement(self._root, 'object')
            node_name = SubElement(node_object, 'name')
            node_name.text = label
            node_pose = SubElement(node_object, 'pose')
            node_pose.text = 'Unspecified'
            node_truncated = SubElement(node_object, 'truncated')
            node_truncated.text = '0'
            node_difficult = SubElement(node_object, 'difficult')
            node_difficult.text = '0'
            self._boxes[i]=self.check_border(self._boxes[i])

            node_bndbox = SubElement(node_object, 'bndbox')
            node_xmin = SubElement(node_bndbox, 'xmin')
            node_xmin.text = str(int(self._boxes[i][0]))

            node_ymin = SubElement(node_bndbox, 'ymin')
            node_ymin.text = str(int(self._boxes[i][1]))

            node_xmax = SubElement(node_bndbox, 'xmax')
            node_xmax.text = str(int(self._boxes[i][2]))

            node_ymax = SubElement(node_bndbox, 'ymax')
            node_ymax.text = str(int(self._boxes[i][3]))

    def check_border(self,bbox): #边缘检测
        if bbox[0] <= 0.0:
            bbox[0] = 1

        if bbox[1] <= 0.0:
            bbox[1] = 1

        if bbox[2] >= self._size[0]:
            bbox[2] = self._size[0] - 1

        if bbox[3] >= self._size[1]:
            bbox[3] = self._size[1] - 1
        return bbox

    def reload_path_attribute(self,path): #重写路径属性
        self._xml_path=path
        self.load_path_attribute()

    def reload_size_attribute(self,size): #重写尺寸属性
        self.size=size
        self.load_size_attribute()

    def reload_obj_attribute(self,labels,boxes): #重写目标物属性
        self._labels=labels
        self._boxes=boxes
        assert len(self._labels)==len(self._boxes),'label is not match with boxes,Please check again!'
        self.load_obj_attribute()

    def find_labels(self):  #加载目标物标签
        element_objs = self._root.findall('object')
        for element_obj in element_objs:
            name = element_obj.find('name').text
            self._labels.append(name)

    def find_boxes(self):  #加载目标物位置
        element_objs = self._root.findall('object')
        for element_obj in element_objs:
            bbox = element_obj.find('bndbox')
            xmin = int(float(bbox.find('xmin').text))
            ymin = int(float(bbox.find('ymin').text))
            xmax = int(float(bbox.find('xmax').text))
            ymax = int(float(bbox.find('ymax').text))
            self._boxes.append([xmin,ymin,xmax,ymax])

    def find_size(self):  #加载图像尺寸
        element_objs = self.root.findall('size')
        width = int(element_objs[0].find('width').text)
        height = int(element_objs[1].find('height').text)
        depth = int(element_objs[2].find('depth').text)
        self._size.append(width).append(height).append(depth)

    def get_xml_path(self): #返回路径
        return self._xml_path

    def get_labels(self):  #返回标签
        return self._labels

    def get_boxes(self):  #返回位置
        return self._boxes

    def get_size(self): #返回尺寸
        return self._size

    def save_xml(self,new_path=None): #写入本地
        if new_path!=None:
            #写入至其他路径
            path=new_path
        else:#重新写入当前路径
            path=self._xml_path
        self.write_xml(path)

    def write_xml(self,path): #写入xml信息至本地
        if self.mode == 'create':
            xml = tostring(self._root, pretty_print=True)
            dom = parseString(xml)
            with open(path, 'w+') as f:
                dom.writexml(f, addindent='', newl='', encoding='utf-8')
        else:
            self._tree.write(path, encoding="utf-8",xml_declaration=True)

# data=Xml_manager(path='/home/hyl/data/data-lyl/fusion_data/fusion_output/fusion_2018-09-29_resize/Annotations/fusion_2018-09-29_10001_resize.xml')
# # data.save_xml('/home/hyl/data/data-lyl/fusion_2018-09-29_10001_resize_1.xml')
#
# data1=Xml_manager(path='/home/hyl/data/data-lyl/fusion_2018-09-29_10001_resize.xml',mode='create',size=[1000,1000,3])
# print(data1.get_labels())

# data1.save_xml()

