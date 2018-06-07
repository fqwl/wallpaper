import os
import json
import win32api
import win32con
import win32gui
import tkinter as tk
from send2trash import send2trash
from tkinter import messagebox
from tkinter.filedialog import askdirectory


def deleteConfig():
    """删除配置文件"""

    if os.path.exists(config_path):
        os.remove(config_path)

    window.quit()


def getConfigpath():
    """获取配置文件路径"""
    current_path = os.getcwd()
    config_path = current_path + '\\config.json'
    return config_path


def getConfig():
    """获取配置信息"""
    global i, img_paths

    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
            path_1.set(config['path_1'])
            path_2.set(config['path_2'])
            i = config['i']
            img_paths = config['img_paths']


def saveConfig():
    """存储配置信息"""

    config = {
        'path_1': path_1.get(),
        'path_2': path_2.get(),
        'i': i,
        'img_paths': img_paths
    }

    with open(config_path, 'w') as f:
        json.dump(config, f)

    window.quit()


def dirlist(rootdir, allfile):
    """列出文件夹下所有文件"""

    filelist = os.listdir(rootdir)

    for filename in filelist:
        filepath = os.path.join(rootdir, filename)
        if os.path.isdir(filepath):
            dirlist(filepath, allfile)
        else:
            allfile.append(filepath)
    return allfile


def printInfo(filename):
    """输出信息"""
    global i
    l.config(text=i)
    if filename != '':
        if t.get(1.0, tk.END) != '':
            t.delete(1.0, tk.END)
        t.insert('insert', filename)


def message(n):
    """弹窗"""
    if n == 1:
        m = '图片已处理完'
    elif n == 2:
        m = '请输入目录'
    elif n == 3:
        m = '已是第一张'
    tk.messagebox.showinfo(title='出错了', message=m)


def fileext(filepath):
    (filename, fileext) = os.path.splitext(filepath)
    return fileext


def pretreatment():
    global i
    parent_path = path_1.get()

    i = 0
    img_paths.clear()
    filelist = []

    if (parent_path != '') & (os.path.isdir(parent_path)):
        allfilepath = dirlist(parent_path, filelist)
        for filepath in allfilepath:
            ext = fileext(filepath)
            if (ext == '.jpg') | (ext == '.png') | (ext == '.bmp') | (ext == '.jpeg') | (ext == '.JPEG'):
                img_paths.append(filepath)
                i += 1
        printInfo('')
    else:
        message(2)


def setWallpaper(n):
    """设置壁纸"""
    global i
    if i <= 0:
        message(1)
    else:
        if n == 1:
            i -= 1
        elif n == 0:
            i += 1

        if i >= len(img_paths):
            message(3)
            i -= 1
        else:
            # 打开指定注册表路径
            reg_key = win32api.RegOpenKeyEx(
                win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
            # 最后的参数:2拉伸,0居中,6适应,10填充,0平铺
            win32api.RegSetValueEx(
                reg_key, "WallpaperStyle", 0, win32con.REG_SZ, "10")
            # 最后的参数:1表示平铺,拉伸居中等都是0
            win32api.RegSetValueEx(
                reg_key, "TileWallpaper", 0, win32con.REG_SZ, "0")
            # 刷新桌面
            win32gui.SystemParametersInfo(
                win32con.SPI_SETDESKWALLPAPER, img_paths[i], win32con.SPIF_SENDWININICHANGE)
            printInfo(img_paths[i])


def copyImg():
    """复制图片"""
    targetdir = path_2.get()
    if (i == 0) | (targetdir == ''):
        message(2)
    else:
        os.popen("copy %s,%s " % (img_paths[i], targetdir))


def deleteImg():
    """删除图片"""
    if i == 0:
        message(2)
    else:
        files = img_paths.pop(i)
        setWallpaper(1)
        send2trash(files)


def selectPath(n):
    path_f = askdirectory().replace('/', '\\')
    if n == 1:
        path_1.set(path_f)
    elif n == 2:
        path_2.set(path_f)


window = tk.Tk()
window.title("Wallpaper Filter")
window.geometry('280x395')
window.resizable(False, False)

path_1 = tk.StringVar()
path_2 = tk.StringVar()
i = 0
img_paths = []
config_path = getConfigpath()
getConfig()


tk.Entry(window,
         textvariable=path_1,
         width=29).grid(row=0, column=0, sticky='N' + 'W')
tk.Button(window,
          text='选择文件夹',
          command=lambda: selectPath(1)
          ).grid(row=0, column=1, sticky='N' + 'E')
tk.Entry(window,
         textvariable=path_2,
         width=29).grid(row=1, column=0, sticky='N' + 'W')
tk.Button(window,
          text='选择文件夹',
          command=lambda: selectPath(2)
          ).grid(row=1, column=1, sticky='N' + 'E')
tk.Button(window,
          text='预处理',
          command=pretreatment,
          width=38,
          height=2).grid(row=2, columnspan=2)
tk.Button(window,
          text='上一张',
          command=lambda: setWallpaper(0),
          width=38,
          height=2).grid(row=3, columnspan=2)
tk.Button(window,
          text='下一张',
          command=lambda: setWallpaper(1),
          width=38,
          height=2).grid(row=4, columnspan=2)
tk.Button(window,
          text='复制当前壁纸',
          command=copyImg,
          width=38,
          height=2).grid(row=5, columnspan=2)
tk.Button(window,
          text='删除当前壁纸',
          command=deleteImg,
          width=38,
          height=2).grid(row=6, columnspan=2)
tk.Button(window,
          text='保存并退出',
          command=saveConfig,
          width=38,
          height=2).grid(row=7, columnspan=2)

t = tk.Text(window, width=38, height=2)
t.grid(row=8, columnspan=2)
l = tk.Label(window, text=i, width=38)
l.grid(row=9, columnspan=2)

window.protocol("WM_DELETE_WINDOW", deleteConfig)

window.mainloop()
