import os
import tkinter as tk
from send2trash import send2trash
from tkinter import messagebox
import win32api,win32con,win32gui
i = 0

def main():
    global i,t,l
    window = tk.Tk()
    window.title('Wallpaper Filter')
    window.geometry('260x330')
    window.minsize(260,330)
    window.maxsize(260,330)

    e_1,e_2 = entry(window)
    b_1,b_2,b_3,b_4,b_5= button(window)

    b_1.config(command = lambda: pretreatment(e_1))
    b_2.config(command = lambda: set_wallpaper(0))
    b_3.config(command = lambda: set_wallpaper(1))
    b_4.config(command = lambda: copyimg(e_2))
    b_5.config(command = deleteimg)
    t,l = output(window)

    window.mainloop()


def entry(window):
    """生成输入框"""
    e1 = tk.Entry(window,show = None,width = 35)
    e1.pack()
    e2 = tk.Entry(window,show = None,width = 35)
    e2.pack()

    return e1,e2

def button(window):
    """生成按钮"""
    b1 = tk.Button(window,
            text = '预处理',
            width = 35,
            height = 2,)
    b1.pack()
    b2 = tk.Button(window,
            text = '上一张',
            width = 35,
            height = 2,)
    b2.pack()
    b3 = tk.Button(window,
            text = '下一张',
            width = 35,
            height = 2,)
    b3.pack()
    b4 = tk.Button(window,
            text = '复制当前壁纸',
            width = 35,
            height = 2,)
    b4.pack()
    b5 = tk.Button(window,
            text = '删除当前壁纸',
            width = 35,
            height = 2,)
    b5.pack()

    return b1,b2,b3,b4,b5

def output(window):
    """生成输出框"""
    global i
    t = tk.Text(window,width = 35,height = 2)
    t.pack()
    l = tk.Label(window,text = 'i',width = 35,)
    l.pack()

    return t,l

def dirlist(rootdir,allfile):
    filelist = os.listdir(rootdir)

    for filename in filelist:
        filepath = os.path.join(rootdir,filename)
        if os.path.isdir(filepath):
            dirlist(filepath,allfile)
        else:
            allfile.append(filepath)
    return allfile

def fileext(filepath):
    (filename,fileext) = os.path.splitext(filepath)
    return fileext

def pretreatment(e1):
    """预处理"""
    global i,img_path
    parent_path = e1.get()
    i = 0
    filelist = []
    img_path = []
    if (parent_path != '')&(os.path.isdir(parent_path)):
        allfilepath = dirlist(parent_path,filelist)
        for filepath in allfilepath:
            ext = fileext(filepath)
            if (ext == '.jpg')|(ext == '.png')|(ext == '.bmp')|(ext == '.jpeg')|(ext == '.JPEG'):
                img_path.append(filepath)
                i += 1
        printinfo('')
    else:
        message(2)


def set_wallpaper(n):
    """设置壁纸"""
    global i,img_path
    if i <= 0:
        message(1)
    else:
        if n == 1:
            i -= 1
        elif n == 0:
            i += 1

        if i >= len(img_path):
            message(3)
            i -= 1
        else:
            #打开指定注册表路径
            reg_key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER,"Control Panel\\Desktop",0,win32con.KEY_SET_VALUE)
            #最后的参数:2拉伸,0居中,6适应,10填充,0平铺
            win32api.RegSetValueEx(reg_key, "WallpaperStyle", 0, win32con.REG_SZ, "10")
            #最后的参数:1表示平铺,拉伸居中等都是0
            win32api.RegSetValueEx(reg_key, "TileWallpaper", 0, win32con.REG_SZ, "0")
            #刷新桌面
            win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER,img_path[i], win32con.SPIF_SENDWININICHANGE)
            printinfo(img_path[i])



def copyimg(e2):
    """复制图片"""
    global i,img_path
    targetdir = e2.get()
    if (i == 0)|(targetdir == ''):
        message(2)
    else:
        os.system("copy %s,%s " % (img_path[i],targetdir))


def deleteimg():
    """删除图片"""
    global i,img_path
    if i == 0:
        message(2)
    else:
        files = img_path.pop(i)
        set_wallpaper(1)
        send2trash(files)


def printinfo(filename):
    """输出信息"""
    global i,t,l
    l.config(text = i)
    if filename != '':
        if t.get(1.0,tk.END) != '':
            clear(t)
        t.insert('insert',filename)

def clear(txt):
    txt.delete(1.0, tk.END)

def message(n):
    """弹窗"""
    if n == 1:
        m = '图片已处理完'
    elif n == 2:
        m = '请输入目录'
    elif n == 3:
        m = '已是第一张'
    tk.messagebox.showinfo(title='出错了',message = m)

if __name__ == '__main__':
    main()
