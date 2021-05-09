import os
import json
import shutil
from typing import Union
# import ctypes
import win32api
import win32con
import win32gui
import tkinter as tk
from send2trash import send2trash
from tkinter import messagebox
from tkinter.filedialog import askdirectory

# def killConsole():
#     """干掉/隐藏命令行界面"""
#     k32 = ctypes.windll.LoadLibrary("kernel32.dll")
#     whnd = k32.GetConsoleWindow()
#     if whnd != 0:
#         ctypes.windll.user32.ShowWindow(whnd, 0)
#         ctypes.windll.kernel32.CloseHandle(whnd)


def deleteConfig():
    """删除配置文件"""

    if os.path.exists(config_path):
        os.remove(config_path)

    window.quit()


def getConfigpath() -> Union[str, None]:
    """获取配置文件路径"""
    current_path = os.getcwd()
    config_path = current_path + '\\config.json'
    return config_path


def getConfig() -> dict:
    """获取配置信息"""
    with open(config_path) as f:
        configs = json.load(f)

    os.remove(config_path)

    path_1.set(configs['path_1'])
    path_2.set(configs['path_2'])
    return configs['i'], configs['img_paths']


def dirlist(rootdir: str, allfile: list) -> list:
    """列出文件夹下所有文件"""

    filelist = os.listdir(rootdir)

    for filename in filelist:
        filepath = os.path.join(rootdir, filename)
        if os.path.isdir(filepath):
            dirlist(filepath, allfile)
        else:
            allfile.append(filepath)
    return allfile


def getallfiles(fp: str) -> list:
    "fp：文件夹路径"
    files = []
    datas = os.listdir(fp)
    for data in datas:
        p = os.path.join(fp, data)
        if os.path.isdir(p):
            files.extend(getallfiles(p))
        else:
            files.append(p)

    return files


def printInfo(filename):
    """输出信息"""
    l.config(text=len(wallpapers.paths) - wallpapers.i)
    if filename != '':
        if t.get(1.0, tk.END) != '':
            t.delete(1.0, tk.END)
        t.insert('insert', filename)
# BUG: 输出信息时可能不及时


def message(msg: str):
    """弹窗"""
    tk.messagebox.showinfo(title='出错了', message=msg)


# def fileext(filepath):
#     (_, fileext) = os.path.splitext(filepath)
#     return fileext
def setWallpaper(fpath: str):
    """设置壁纸"""
    if os.path.isfile(fpath):
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
            win32con.SPI_SETDESKWALLPAPER, fpath, win32con.SPIF_SENDWININICHANGE)
        printInfo(fpath)
    else:
        message("文件不存在")


def selectPath(m: int):
    path_f = askdirectory().replace('/', '\\')
    if m == 1:
        path_1.set(path_f)
    elif m == 2:
        path_2.set(path_f)


class Wallpapers:
    "壁纸列表类"

    def __init__(self, config: dict):

        self.paths = list(config['img_paths'])
        self.i = config['i']

    @property
    def ptpath(self,) -> str:
        return path_1.get()

    @property
    def tpath(self,) -> str:
        return path_2.get()

    # NOTE: 通过特性来动态获取ptpath和tpath

    def pretreatment(self,):
        """加载配置或读取设定的文件夹"""
        if os.path.isdir(self.ptpath):
            self.paths.clear()
            allfilepath = getallfiles(self.ptpath)
            for filepath in allfilepath:
                _, ext = os.path.splitext(filepath)
                if ext in '.jpg.png.bmp.jpeg.JPEG':
                    self.paths.append(filepath)
            self.i = 0
            setWallpaper(self.paths[self.i])
        else:
            message("请输入目录")

    def previous(self,):
        "将前一张图片设为壁纸"
        if self.i >= 1:
            self.i = self.i - 1
        else:
            message("已是第一张")
            self.i = len(self.paths) - 1
        if len(self.paths) > 0:
            setWallpaper(self.paths[self.i])
            

    def next(self,):
        "将下一张图片设为壁纸"
        if self.i < len(self.paths) - 1:
            self.i = self.i + 1
        else:
            message("已是最后一张")
            self.i = self.i + 1 - len(self.paths)
        if len(self.paths) > 0:
            setWallpaper(self.paths[self.i])

    # NOTE:previous()和next()会跳过无法设置成壁纸的图片
    # MOD: 前一张和后一张可能出错 -> 索引位置未对齐

    def copyimg(self,):
        """复制移动当前壁纸到目标目录"""
        if os.path.exists(self.tpath) & os.path.isdir(self.tpath):
            shutil.copy(self.paths[self.i], self.tpath)
        else:
            message("目标目录未输入或不存在")

    def moveimg(self,):
        """移动当前壁纸到目标目录"""
        if os.path.exists(self.tpath) & os.path.isdir(self.tpath):
            fpath = self.paths[self.i]
            _, filename = os.path.split(fpath)
            targetpath = self.tpath + "/" + filename
            if os.path.isfile(targetpath):
                targetpath = self.tpath + "/2_" + filename
            self.next()
            os.rename(fpath, targetpath)
            self.paths.remove(fpath)
            self.i = self.i - 1

        else:
            message("目标目录未输入或不存在")

    def deleteimg(self,):
        """删除当前壁纸"""
        try:
            fpath = self.paths[self.i]
            self.next()
        except IndexError:
            message("请输入目录")
            fpath = ''
        if os.path.isfile(fpath):
            send2trash(fpath)
            self.paths.remove(fpath)
            self.i = self.i - 1

    # NOTE:moveimg()和deleteimg()应当在执行self.next()后再从self.paths中删除文件路径

    def saveconfig(self,):
        """存储配置信息并退出"""
        # config_path = getConfigpath()

        config = {
            'path_1': self.ptpath,
            'path_2': self.tpath,
            'i': self.i,
            'img_paths': self.paths
        }
        if self.ptpath != '':
            with open(config_path, 'w') as f:
                json.dump(config, f)

        window.quit()


# killConsole()

window = tk.Tk()
window.title("Wallpaper Filter")


path_1 = tk.StringVar()
path_2 = tk.StringVar()

config_path = getConfigpath()
CONFIG = {"i": 0, "img_paths": []}

wallpapers = Wallpapers(CONFIG)


tk.Entry(window,
         textvariable=path_1
         ).grid(row=0, column=0, columnspan=3, sticky='N' + 'E' + 'S' + 'W')
tk.Button(window,
          text='选择文件夹',
          command=lambda: selectPath(1)
          ).grid(row=0, column=3, sticky='N' + 'E' + 'S' + 'W')
tk.Entry(window,
         textvariable=path_2,
         ).grid(row=1, column=0, columnspan=3, sticky='N' + 'E' + 'S' + 'W')
tk.Button(window,
          text='选择文件夹',
          command=lambda: selectPath(2)
          ).grid(row=1, column=3, sticky='N' + 'E' + 'S' + 'W')
tk.Button(window,
          text='预处理',
          command=wallpapers.pretreatment,
          height=2).grid(row=2, columnspan=4, sticky='N' + 'E' + 'S' + 'W')
tk.Button(window,
          text='上一张',
          command=wallpapers.previous,
          height=2).grid(row=3, columnspan=4, sticky='N' + 'E' + 'S' + 'W')
tk.Button(window,
          text='下一张',
          command=wallpapers.next,
          height=2).grid(row=4, columnspan=4, sticky='N' + 'E' + 'S' + 'W')
tk.Button(window,
          text='复制当前壁纸',
          command=wallpapers.copyimg,
          height=2).grid(row=5, columnspan=4, sticky='N' + 'E' + 'S' + 'W')
tk.Button(window,
          text='移动当前壁纸',
          command=wallpapers.moveimg,
          height=2).grid(row=6, columnspan=4, sticky='N' + 'E' + 'S' + 'W')
tk.Button(window,
          text='删除当前壁纸',
          command=wallpapers.deleteimg,
          height=2).grid(row=7, columnspan=4, sticky='N' + 'E' + 'S' + 'W')
tk.Button(window,
          text='保存并退出',
          command=wallpapers.saveconfig,
          height=2).grid(row=8, columnspan=4, sticky='N' + 'E' + 'S' + 'W')

t = tk.Text(window, width=45, height=2)
t.grid(row=9, columnspan=4)
l = tk.Label(window, text=wallpapers.i,)
l.grid(row=10, columnspan=4, sticky='N' + 'E' + 'S' + 'W')


if os.path.exists(config_path):
    wallpapers.i, wallpapers.paths = getConfig()
    printInfo(wallpapers.paths[wallpapers.i])
window.protocol("WM_DELETE_WINDOW", deleteConfig)

window.mainloop()
