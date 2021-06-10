import win32com.client
from win32api import GetFileVersionInfo, HIWORD, LOWORD
import subprocess  # 用于执行cmd命令
import re  # 正则模块
import os
import sys
import urllib.request  # 发送http请求
import urllib.parse  # 拼接url
import zipfile  # 操作.zip文件
startMenu = 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs'

version_re = re.compile(r'^[0-9]\d*\.\d*.\d*')


def getVersionNumber(filename):
    try:
        info = GetFileVersionInfo(filename, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return [HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls)]
    except Exception as e:
        print(e)
        return [0, 0, 0, 0]


def getChromePath():
    for i in os.listdir(startMenu):
        if "chrome" in i.lower():
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(f'{startMenu}\{i}')
            return shortcut.Targetpath
    return ""
def getChromeVersion():
    for i in os.listdir(startMenu):
        if "chrome" in i.lower():
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(f'{startMenu}\{i}')
            version = getVersionNumber(shortcut.Targetpath)
    _v = '.'.join([str(i) for i in version])
    print(_v)
    return version_re.findall(_v)[0]


def getDriverVersion(absPath):
    """
    :param absPath: chromedriver.exe的绝对路径
    """
    cmd = r'{} --version'.format(absPath)  # 拼接成cmd命令
    try:
        # 执行cmd命令并接收命令回显
        out, err = subprocess.Popen(cmd,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE).communicate()
        out = out.decode('utf-8')
        _v = out.split(' ')[1]  # 拆分回显字符串，获取版本号
        return version_re.findall(_v)[0]
    except IndexError as e:
        return 0


def checkVersionMatch():
    c_v = getChromeVersion()
    d_v = getDriverVersion('chromedriver.exe')
    return c_v == d_v


def downloadChromeDriver(__v='',
                         url='http://npm.taobao.org/mirrors/chromedriver/',
                         save_d='.'):
    # 访问淘宝镜像首页

    if not __v:
        __v = getChromeVersion()
    rep = urllib.request.urlopen(url).read().decode('utf-8')
    # '<a href="/mirrors/chromedriver/84.0.4147.30/">84.0.4147.30/</a>'
    directory = re.compile(r'>(\d.*?/)</a>').findall(rep)  # 匹配文件夹（版本号）

    # 获取期望的文件夹（版本号）
    match_list = []
    for i in directory:
        v = version_re.findall(i)[0]
        if __v == v:
            match_list.append(i)

    # http://npm.taobao.org/mirrors/chromedriver/83.0.4103.39/chromedriver_win32.zip
    dirUrl = urllib.parse.urljoin(url, match_list[-1])
    downUrl = urllib.parse.urljoin(dirUrl, 'chromedriver_win32.zip')  # 拼接出下载路径
    print('will download {}'.format(downUrl))

    # 指定下载的文件名和保存位置
    file = os.path.join(save_d, os.path.basename(downUrl))
    print('will saved in {}'.format(file))

    # 开始下载，并显示下载进度(progressFunc)
    urllib.request.urlretrieve(downUrl, file, progressFunc)

    # 下载完成后解压
    zFile = zipfile.ZipFile(file, 'r')
    for fileM in zFile.namelist():
        zFile.extract(fileM, os.path.dirname(file))
    zFile.close()
    try:
        os.remove(file)
    except Exception as e:
        print(e)


def progressFunc(blocknum, blocksize, totalsize):
    '''回调函数
    :blocknum: 已经下载的数据块
    :blocksize: 数据块的大小
    :totalsize: 远程文件的大小
    '''
    percent = 100.0 * blocknum * blocksize / totalsize
    if percent > 100:
        percent = 100
    downsize = blocknum * blocksize
    if downsize >= totalsize:
        downsize = totalsize
    s = "%.2f%%" % (percent) + "====>" + "%.2f" % (
        downsize / 1024 / 1024) + "M/" + "%.2f" % (totalsize / 1024 /
                                                   1024) + "M \r"
    sys.stdout.write(s)
    sys.stdout.flush()
    if percent == 100:
        print('')
