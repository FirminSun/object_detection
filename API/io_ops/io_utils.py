#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 3/15/2018 4:22 PM
# @Author : sunyonghai
# @File : io_utils.py
# @Software: ZJ_AI
# =========================================================

# 引入模块
import os
import shutil

def mkdir(dest_dir):
    # 去除首位空格
    dest_dir = dest_dir.strip()
    # 去除尾部 \ 符号
    dest_dir = dest_dir.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    is_exists = os.path.exists(dest_dir)

    # 判断结果
    if not is_exists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        try:
            os.makedirs(dest_dir)
        except Exception as e:
            print("Can't create dir:", dest_dir)

        print(dest_dir + ' create successfully.')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        #print(dest_dir + 'Dir is existed ')
        return False

def move(src_file, dest_dir):
    mkdir(dest_dir)

    try:
        shutil.move(src_file, dest_dir)
        print("move successfuly:'{}' to '{}'".format(src_file, dest_dir))
    except Exception as e:
        print("Can't not move '{}' to '{}'. :{}", src_file, dest_dir, e)

def copy_dir(src_dir, dest_dir):
    # mkdir(dest_dir)

    for file in os.listdir(src_dir):
        src_file = os.path.join(src_dir, file)
        try:
            shutil.copy(src_file, dest_dir)
            #print("copy successfuly:copy '{}' to '{}'".format(src_file, dest_dir))
        except Exception as e:
            print("Can't not copy {} to {}. :{}", src_file, dest_dir, e)

def copy(src_file, dest_dir):
    # mkdir(dest_dir)

    try:
        shutil.copy(src_file, dest_dir)
        #print('copy successfuly:{} copy t0 {}'.format(src_file, dest_dir))
    except Exception as e:
        print("Can't not copy {} to {}. :{}", src_file, dest_dir, e)

def delete_file_folder(src):
    # 去除首位空格
    src = src.strip()
    # 去除尾部 \ 符号
    src = src.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    is_exists = os.path.exists(src)

    # 判断结果
    if not is_exists:
        return

    '''delete files and folders'''
    if os.path.isfile(src):
        try:
            os.remove(src)
        except:
            pass
    elif os.path.isdir(src):
        for item in os.listdir(src):
            itemsrc=os.path.join(src,item)
            delete_file_folder(itemsrc)
        try:
            os.rmdir(src)
        except:
            pass

def remove_all(dest_dir): #删除目标文件夹中的文件
    try:
        file_list = os.listdir(dest_dir)
        for f in file_list:
            filepath = os.path.join(dest_dir, f)
            if os.path.isfile(filepath):
                os.remove(filepath)
                print(filepath + " removed!")
            elif os.path.isdir(filepath):
                shutil.rmtree(filepath, True)
                print("dir " + filepath + " removed!")

    except IOError as exc:
        print(exc)

def rename(oldname, newname):
    try:
        if oldname !='' and newname != '':
            os.rename(oldname, newname)
            print('old name:', oldname)
            print('new name:', newname)
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    delete_file_folder('/home/syh/temp/a')  #linux的
