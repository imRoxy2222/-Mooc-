import random
import re
from time import sleep
from tkinter import *
import tkinter
import time

import requests
from ddddocr import DdddOcr

root = Tk()
textCol = 1.0

headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'cookie': "token=sid.K7MvIBt8HPC9bqyeNJR37lfsqaDuhY",
    'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    'sec-ch-ua-platform': '"Windows"',
    'user-agent': ""
}

headers_list = [
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
    "Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14",
    "Opera/12.0(Windows NT 5.1;U;en)Presto/22.9.168 Version/12.00",
    "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0"
]

TIME = 1600


def study(data: dict, url: str):
    global TIME
    count = 0
    InsertTotextInfo(" 本集一共需要%d秒\n" % TIME)

    root.after(30000, lambda: value.set(1))
    tmplable.wait_variable(value)

    for time in range(data["studyTime"] + 30, TIME + 20, 30):
        data['studyTime'] = time
        resp = requests.post(url=url, headers=headers, data=data)

        if "提交学时成功" in resp.text:
            res = 100 if time / TIME > 1.0 else time / TIME * 100

            InsertTotextInfo(" %s已刷%.4s%%\n" % (data['nodeId'], str(res)))

        else:
            InsertTotextInfo(" 提交失败\n")

        if count % 6 == 0:
            a = 0 if postOnline() else InsertTotextInfo(" online提交失败\n")

        count = count + 1

        root.after(30000, lambda: value.set(1))
        tmplable.wait_variable(value)


def getStudyId(nodeld: str, url: str):
    data = {"nodeId": nodeld, "studyId": 0, "studyTime": 1, "code": ""}
    data["nodeld"] = nodeld

    code = getCode()
    data['code'] = code + '_'
    resp = requests.post(url=url, headers=headers, data=data).text

    studyid_ex = '"studyId":(\d{8}),'
    studyid = re.findall(studyid_ex, resp, re.M)

    return studyid[0]


def getCourseId():
    url = "https://mooc.cqcst.edu.cn/user/index?kind=run"
    resp = requests.get(url=url, headers=headers).text

    course_id_ex = '\"/user/course\?courseId\=(\d+)">([\u4e00-\u9fa5a-zA-Z]+)'
    course_id = re.findall(course_id_ex, resp, re.M)

    return course_id


def getTime(course_id: str):
    url = "https://mooc.cqcst.edu.cn/user/study_record.json"
    params = {
        "courseId": course_id,
        "page": 1,
        "_": "1666320828" + str(random.randint(100, 999))
    }

    study_nodeid_dct = {}
    state_ex = '未学|已学'
    nodeid_ex = "nodeId\=(\d+)"
    video_time = '"videoDuration":"(\d{2}:\d{2}:\d{2})"'

    for i in range(1, 10, 1):
        params["page"] = i
        InsertTotextInfo("========第%d页==========\n" % i, nowtime="")
        resp_info = requests.get(url=url, headers=headers, params=params).text

        for state, nodeid, time in zip(re.findall(state_ex, resp_info, re.M), re.findall(nodeid_ex, resp_info, re.M),
                                       re.findall(video_time, resp_info, re.M)):
            InsertTotextInfo(" %s %s %s\n" % (state, nodeid, time))
            if state == "未学":
                study_nodeid_dct[nodeid] = time
        if len(re.findall(state_ex, resp_info, re.M)) < 20:
            return study_nodeid_dct


def postStudy():
    global TIME
    url = "https://mooc.cqcst.edu.cn/user/node/study"

    data = {
        'nodeId': "",
        'studyId': 0,
        'studyTime': 1
    }

    course_list = getCourseId()
    for course_id in course_list:
        for nodeid, time in getTime(course_id[0]).items():
            TIME = int(time[0:2]) * 3600 + int(time[3:5]) * 60 + int(time[6:])
            InsertTotextInfo(" 正在学习%s\n" % nodeid)

            data["nodeId"] = nodeid

            data["studyId"] = getStudyId(nodeid, url)

            n = random.randint(3, 10)
            data["studyTime"] = n
            root.after(n * 1000, lambda: value.set(1))
            tmplable.wait_variable(value)

            InsertTotextInfo(" studyID=%s\n" % data["studyId"])

            if len(data["studyId"]) == 8:
                study(data, url)
            else:
                InsertTotextInfo(" %d刷取失败" % nodeid)


def postOnline(count=1):
    url = "https://mooc.cqcst.edu.cn/user/online"

    data = {
        'msg': "ok",
        'status': 'true'
    }

    resp = requests.post(url=url, data=data, headers=headers).text
    if 'ok' not in resp and 'true' not in resp:
        InsertTotextInfo(" online提交失败:%d\n" % count)
        return False if count == 4 else postOnline(count + 1)
    InsertTotextInfo(" online提交成功\n")
    return True


def getCode():
    url = "https://mooc.cqcst.edu.cn/service/code/aa?r="
    f = random.random()
    url = url + str(f)

    code_img = requests.get(url=url, headers=headers).content

    ocr = DdddOcr(old=True, show_ad=False)

    res = ocr.classification(code_img)
    InsertTotextInfo(" 验证码是:%s\n" % res)
    return res


def GetLoginKey():
    parser = {
        "r": "{time()}"
    }
    keytmp = requests.get(url="https://mooc.cqcst.edu.cn/service/code", params=parser, headers=headers).content
    ocr = DdddOcr(old=True, show_ad=False)
    key = ocr.classification(keytmp)

    return key


def InsertTotextInfo(info: str, nowtime="1") -> None:
    global textCol
    if nowtime == "1":
        nowtime = time.strftime("%H:%M:%S")

    text_info.insert(str(textCol), nowtime + info)
    textCol += 1
    text_info.update()
    text_info.see(END)

    root.after(200, lambda: value.set(1))
    tmplable.wait_variable(value)


def login():
    global textCol
    loginUrl = "https://mooc.cqcst.edu.cn/user/login"
    username = entry_username.get().strip()
    password = entry_passwd.get().strip()

    data = {
        "username": username,
        "password": password,
        "code": "",
        "redirect": ""
    }
    for i in range(2):
        data["code"] = GetLoginKey()

        InsertTotextInfo(" 第%d次尝试,验证码为%s\n" % (i + 1, data["code"]))

        resp = requests.post(url=loginUrl, data=data, headers=headers).text
        if "登录成功" in resp:
            InsertTotextInfo(" 登录成功\n")
            postStudy()
            exit()
        InsertTotextInfo(" 登录失败,等待重试\n")

        root.after(random.randint(5, 10 + 1) * 1000, lambda: value.set(1))
        tmplable.wait_variable(value)

    InsertTotextInfo(" 账号/密码有误\n")
    root.after(5000, lambda: value.set(1))
    tmplable.wait_variable(value)


if __name__ == "__main__":
    headers["user-agent"] = headers_list[random.randint(0, len(headers_list) - 1)]

    root.geometry("300x500+150+150")
    root.resizable(False, False)

    root.title("Final Version")

    label_username = Label(root, text="账号:", font=("宋体", 13), fg="black")
    label_passwd = Label(root, text="密码:", font=("宋体", 13), fg="black")
    label_info = Label(root, text="author:frank2222", font=("consolas", 8), fg="red")
    label_username.place(x=20, y=15)
    label_passwd.place(x=20, y=45)
    label_info.place(x=80, y=470)

    entry_username = Entry(root, font=("微软雅黑", 13), fg="black")
    entry_passwd = Entry(root, font=("微软雅黑", 13), fg="black", show="*")
    entry_username.place(x=65, y=15)
    entry_passwd.place(x=65, y=45)

    button_enterOK = Button(root, text="确定", font=("微软雅黑", 15), fg="black", command=login)
    button_enterOK.place(x=110, y=80)

    text_info = Text(root, width=34, height=25, undo=True, autoseparators=False)
    scrollbar = tkinter.Scrollbar(root, orient="vertical", command=text_info.yview)
    text_info.config(yscrollcommand=scrollbar.set)

    scrollbar.place(x=265, y=123, height=353)
    text_info.bind("<Key>", lambda e: "break")
    text_info.place(x=23, y=135)

    value = tkinter.IntVar()
    tmplable = Label(root)

    InsertTotextInfo(" 取消验证,可任意使用\n")

    root.mainloop()
