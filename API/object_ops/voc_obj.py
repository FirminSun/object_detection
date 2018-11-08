import cv2
import os
from xml_ops import xml_manager
from image_ops import image_utils
from io_ops import io_utils
import numpy as np
import datetime
import random

class Voc_obj(object):
    def __init__(self,path,scale=1000,mode='load',xml_type='normal'):
        self.path=path
        self.mode=mode
        self.scale=scale
        self.xml_type=xml_type
        self._jpg_list=None
        self._xml_list=None
        self.file_list=None
        self.labels=None
        self.trainval=None
        self.test=None
        self.init()

    def init(self):
        if self.mode=='load':
            self._jpg_list=os.listdir(os.path.join(self.path,'JPEGImages'))
            if self.xml_type=='normal':
                self._xml_list=os.listdir(os.path.join(self.path,'Annotations'))
            elif self.xml_type=='test':
                self._xml_list = os.listdir(os.path.join(self.path, 'Annotations_test'))
            self._check_data()
        if self.mode=='create':
            jpgs=[os.path.join(self.path,jpg) for jpg in os.listdir(self.path) if os.path.splitext(jpg)[1]=='.jpg' or os.path.splitext(jpg)[1]=='.JPG']
            xmls = [os.path.join(self.path,xml) for xml in os.listdir(self.path) if os.path.splitext(xml)[1] == '.xml']
            self._make_voc_dir()
            self._rotate_pre_voc(jpgs)
            self._rename_pre_voc(jpgs,xmls)

    def before_train(self):
        self._check_data()
        self._divide_dataset()
        self.count_labels(output=True)


    def _divide_dataset(self):
        self.make_dir(['ImageSets','ImageSets/Main'])
        file_list=self.file_list.copy()
        random.shuffle(file_list)
        self.trainval = [file_list[i] for i in range(len(file_list) // self.scale, len(file_list))]
        self.test = [file_list[i] for i in range(len(file_list) // self.scale)]
        self.save_dataset()

    def save_dataset(self):
        with open(os.path.join(self.path,'ImageSets/Main/trainval.txt'), 'w+') as f:
            f.write('\n'.join(self.trainval))
            print("trainval, numbers:{}".format(len(self.trainval)))
        with open(os.path.join(self.path,'ImageSets/Main/test.txt'), 'w+') as f:
            f.write('\n'.join(self.test))
            print("test, numbers:{}".format(len(self.test)))
        with open(os.path.join(self.path,'ImageSets/Main/trainval_test.txt'), 'w+') as f:
            f.write('\n'.join(self.trainval))
            f.write('\n')
            f.write('\n'.join(self.test))
            print("trainval_test, numbers:{}".format(len(self.trainval)+len(self.test)))

    def count_labels(self,output=False):
        self.load_dataset()
        label_dict={}
        for fn in self.trainval:
            labels=xml_manager.Xml_manager(path=self.get_file_path(fn)[1]).get_labels()
            for label in labels:
                if label in label_dict.keys():
                    label_dict[label]+=1
                else:
                    label_dict[label]=1
        self.labels=label_dict.keys()

        if output:
            label_dict = sorted(label_dict.items(), key=lambda x: x[1], reverse=False)
            print(label_dict)
            with open(self.path + "/" + "labelCount_trainval.txt", "w") as f:
                for (label,count) in label_dict:
                    f.write(label + " :  " + str(count) + "\n")
                f.write("total have {} type object\n".format(str(len(label_dict))))
            print("finish")


    def load_dataset(self):
        with open(os.path.join(self.path,'ImageSets/Main','trainval.txt'),'r') as f:
            self.trainval=[line.replace("\n",'').replace("\r",'') for line in f.readlines()]
        with open(os.path.join(self.path,'ImageSets/Main','test.txt'),'r') as f:
            self.test=[line.replace("\n",'').replace("\r",'') for line in f.readlines()]


    def _make_voc_dir(self):
        self.make_dir('JPEGImages')
        self.make_dir('Annotations')

    def make_dir(self,dir_name):
        if type(dir_name) is str:
            fn=os.path.join(self.path,dir_name)
            if not os.path.exists(fn):
                os.mkdir(fn)
        elif type(dir_name) is list:
            i=0
            while(i<len(dir_name)):
                fn=os.path.join(self.path,dir_name[i])
                if not os.path.exists(fn):
                    os.mkdir(fn)
                i+=1

    def _rotate_pre_voc(self,jpgs):
        for jpg in jpgs:
            self._rotate_img(jpg)

    def _rotate_img(self,jpg_path):
        try:
            img = cv2.imread(jpg_path)
            width = img.shape[0]
            height = img.shape[1]
            if width > height:
                image = np.array(np.rot90(img, 1))
                image = image.copy()
            else:
                image = img

            # don't need resize
            # image = cv2.resize(image, (int(image.shape[1] * 0.5), int(image.shape[0]*0.5)), interpolation=cv2.INTER_CUBIC)
            # print('resize:{}'.format(image.shape))
            cv2.imwrite(jpg_path, image)

            #print(save_path)
        except Exception as e:
            print('Exception in pascal_voc_parser: {}'.format(e))


    def _rename_pre_voc(self,jpgs,xmls):
        #cur_date=datetime.datetime.now()
        #str_date = '{year}{month}{day}'.format(year=cur_date.year, month=cur_date.month, day=cur_date.day)
        #prefix='train'
        id=10000
        for i,jpg in enumerate(jpgs):
            io_utils.rename(jpg,os.path.abspath(os.path.join(jpg,'..','JPEGImages','{}_{}.jpg'.format(os.path.split(self.path)[1],id+i))))
        for xml in xmls:
            io_utils.rename(xml,os.path.abspath(os.path.join(xml,'..','Annotations',os.path.split(xml)[1])))

    def _check_data(self):
        jpgs=[os.path.splitext(jpg)[0] for jpg in self._jpg_list]
        xmls = [os.path.splitext(xml)[0] for xml in self._xml_list]
        xml_loss=[jpg for jpg in jpgs if jpg not in xmls]
        jpg_loss=[xml for xml in xmls if xml not in jpgs]
        self._move_to_trash(jpg_loss,xml_loss)
        self.file_list=[jpg for jpg in jpgs if jpg in xmls]

    def _move_to_trash(self,jpg_loss,xml_loss):
        if len(jpg_loss)>0:
            self.make_dir(['trash','trash/Annotations'])
            print('package lack jpg files :\n{}'.format('\n'.join(jpg_loss)))
            io_utils.move(os.path.join(self.path,'Annotations',jpg_loss+'.xml'),os.path.join(self.path,'trash/Annotations'))
        if len(xml_loss)>0:
            self.make_dir(['trash', 'trash/JPEGImages'])
            print('package lack xml files :\n{}'.format('\n'.join(xml_loss)))
            io_utils.move(os.path.join(self.path,'JPEGImages',jpg_loss+'.jpg'),os.path.join(self.path,'trash/JPEGImages'))


    def load_image_info(self,file):
        assert self.mode=='load','you can set the load mode, and run again!'
        [im_path,xml_path]=self.get_file_path(file)
        im=self._load_im(im_path)
        xml_info=self._load_image_info(xml_path)
        return [im,xml_info]


    def get_file_path(self,file):
        im_path = os.path.join(self.path, 'JPEGImages', file + '.jpg')
        xml_path = os.path.join(self.path, 'Annotations', file + '.xml')
        return [im_path,xml_path]

    def _load_im(self,im_path):
        try :
            im=cv2.imread(im_path)
        except Exception as e:
            print('Exception in pascal_voc_parser: {}'.format(e))
        return im

    def _load_xml(self,xml_path):
        xml=xml_manager.Xml_manager(path=xml_path)
        return xml

    def _load_xml_info(self,xml_path):
        xml=xml_manager.Xml_manager(path=xml_path)
        labels=xml.get_labels()
        boxes=xml.get_boxes()
        info=[[labels[i],boxes[i][0],boxes[i][1],boxes[i][2],boxes[i][3]]for i in range(len(labels))]
        return info

    def rename_voc_file(self,id):
        for obj in self.file_list:
            [im_path,xml_path]=self.get_file_path(obj)
            io_utils.rename(im_path,os.path.join(self.path,'JPEGImages','{}_{}.jpg'.format(os.path.split(self.path)[1],id)))
            io_utils.rename(xml_path,os.path.join(self.path, 'Annotations', '{}_{}.xml'.format(os.path.split(self.path)[1], id)))
            xml=self._load_xml(os.path.join(self.path, 'Annotations', '{}_{}.xml'.format(os.path.split(self.path)[1], id)))
            xml.reload_path_attribute(os.path.join(self.path, 'Annotations', '{}_{}.xml'.format(os.path.split(self.path)[1], id)))
            xml.save_xml()
            id+=1

voc=Voc_obj(path='/home/hyl/data/data-lyl/train_data_2018-11-07_3',mode='load',scale=100)
# voc.before_train()
