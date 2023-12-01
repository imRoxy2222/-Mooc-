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
    'cookie': "",
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

TIME = 0
start_time = int(time.time())


def study(data: dict, url: str):
    global TIME
    count = 0
    InsertTotextInfo(" 本集一共需要%d秒\n" % TIME)

    root.after(30000, lambda: value.set(1))
    tmplable.wait_variable(value)

    postOnline()
    for time in range(data["studyTime"] + 30, TIME + 20, 30):
        data['studyTime'] = time
        resp = ""
        for i in range(3):
            try:
                resp = requests.post(url=url, headers=headers, data=data)
                break
            except:
                InsertTotextInfo(" 网络波动 %d\n" % (i + 1))

        if "提交学时成功" in resp.text:
            res = 100 if time / TIME > 1.0 else time / TIME * 100

            InsertTotextInfo(" %s已刷%.4s%%\n" % (data['nodeId'], str(res)))

        else:
            InsertTotextInfo(" 提交失败\n")

        count = count + 1
        if count % 4 == 0:
            a = InsertTotextInfo(" online提交成功\n") if postOnline() else InsertTotextInfo(" online提交失败\n")

        root.after(30000, lambda: value.set(1))
        tmplable.wait_variable(value)


def getStudyId(nodeld: str, url: str):
    data = {"nodeId": nodeld, "studyId": 0, "studyTime": 1, "code": ""}
    data["nodeld"] = nodeld

    for i in range(3):
        code = getCode()
        data['code'] = code + '_'
        resp = requests.post(url=url, headers=headers, data=data).text

        studyid_ex = '"studyId":(\d{8}),'
        studyid = re.findall(studyid_ex, resp, re.M)

        if studyid:
            break
        else:
            InsertTotextInfo(" 网络波动 %d\n" % (i + 1))
            if i == 2:
                InsertTotextInfo(" 程序暂停 \n", nowtime="")
                exit(-1)
        root.after(random.randint(3, 10) * 1000, lambda: value.set(1))
        tmplable.wait_variable(value)
        # sleep(random.randint(3,10))

    return studyid[0]


# 获取每个课程的courseId
def getCourseId():
    url = "https://mooc.cqcst.edu.cn/user/index?kind=run"
    resp = requests.get(url=url, headers=headers).text

    course_id_ex = '\"/user/course\?courseId\=(\d+)">'
    # 这里set
    course_id = set(re.findall(course_id_ex, resp, re.M))

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
    # 视频已观看时长
    video_time = '"viewedDuration":"(\d{2}:\d{2}:\d{2})"'
    # 视频需观看时长
    video_requir_time = '"videoDuration":"(\d{2}:\d{2}:\d{2})"'

    # 最后一集
    end_nodeid = 0
    # 最后一集,但是临时
    end_nodeid_temp = 0
    for i in range(1, 100, 1):
        params["page"] = i
        InsertTotextInfo("    ========第%d页==========\n" % i, nowtime="")
        resp_info = requests.get(url=url, headers=headers, params=params).text

        for state, nodeid, time, alltime in zip(re.findall(state_ex, resp_info, re.M),  # 观看状态
                                                re.findall(nodeid_ex, resp_info, re.M),  # 视频nodeid
                                                re.findall(video_time, resp_info, re.M),  # 已观看时长
                                                re.findall(video_requir_time, resp_info, re.M)):  # 需观看时长
            InsertTotextInfo(" %s %s %s\n" % (state, nodeid, alltime))
            if state == "未学":
                print(nodeid, alltime, time)
                study_nodeid_dct[nodeid] = (int(alltime[0:2]) * 3600 + int(alltime[3:5]) * 60 + int(alltime[6:8])) - \
                                           (int(time[0:2]) * 3600 + int(time[3:5]) * 60 + int(time[6:8]))
            end_nodeid_temp = nodeid

        # 小于20条记录代表已经到头
        if len(re.findall(state_ex, resp_info, re.M)) < 20:
            return study_nodeid_dct
        # 最后一页刚好20条记录,去除前二十条记录
        elif end_nodeid_temp == end_nodeid:
            return study_nodeid_dct
        end_nodeid = end_nodeid_temp

def postStudy():
    global TIME, start_time
    url = "https://mooc.cqcst.edu.cn/user/node/study"

    data = {
        'nodeId': "",
        'studyId': 0,
        'studyTime': 1
    }

    watched_count = 0

    watched_nodeid = []
    # 获取搜索课程
    course_list = getCourseId()
    for course_id in course_list:
        for nodeid, vtime in getTime(course_id).items():
            # 隔一个查看是否刷取成功
            # if (watched_count+1) % 2 == 0:
            #     tmp = getTime(course_id)
            #     # 刷取失败
            #     if tmp.get(str(int(nodeid)-1)):
            #         if tmp[str(int(nodeid)-1)] > 30:
            #             InsertTotextInfo("    刷取失败,尝试重试\n", nowtime="")
            #             input()
            #             postStudy()

            if nodeid not in watched_nodeid:
                watched_nodeid.append(nodeid)
            else:
                continue
            # TIME = int(vtime[0:2]) * 3600 + int(vtime[3:5]) * 60 + int(vtime[6:])
            TIME = vtime

            # 单次刷取时长不超过2h
            now_time = int(time.time())
            if now_time - start_time > 7200:
                start_time = int(time.time())
                InsertTotextInfo("    刷取时长超过2h,重新登录\n", nowtime="")
                InsertTotextInfo("    刷取时长超过2h,重新登录\n", nowtime="")
                InsertTotextInfo("    刷取时长超过2h,重新登录\n", nowtime="")
                postStudy()

            InsertTotextInfo(" 正在学习%s\n" % nodeid)

            # 需要观看的时长小于10s就可以跳过
            if TIME < 10:
                InsertTotextInfo(" 跳过\n")
                continue

            data["nodeId"] = nodeid
            data["studyId"] = getStudyId(nodeid, url)

            n = random.randint(3, 10)
            data["studyTime"] = n
            root.after(n * 1000, lambda: value.set(1))
            tmplable.wait_variable(value)

            InsertTotextInfo(" studyID=%s\n" % data["studyId"])

            if len(data["studyId"]) == 8:
                study(data, url)
                # pass
            else:
                InsertTotextInfo(" %d刷取失败" % nodeid)
            watched_count += 1


def postOnline(count=1):
    # InsertTotextInfo(" 跳过\n")
    # return True
    url = "https://mooc.cqcst.edu.cn/user/online"

    data = {
        'msg': "ok",
        'status': 'true'
    }

    resp = requests.post(url=url, data=data, headers=headers).text
    if 'ok' not in resp and 'true' not in resp:
        return False if count == 4 else postOnline(count + 1)
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
    for i in range(3):
        try:
            keytmp = requests.get(url="https://mooc.cqcst.edu.cn/service/code", params=parser, headers=headers).content
            # keytmp = requests.get(url='https://mooc.cqcst.edu.cn/service/code?r={time()}', headers=headers).content
            ocr = DdddOcr(old=True, show_ad=False)
            key = ocr.classification(keytmp)

            return key
        except:
            InsertTotextInfo(" 网络波动 %d\n" % (i + 1))



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


def randomCookies():
    str_list = list("K7MvIHt8HPC1bqyeNJK23lfsxaDuhY")
    random.shuffle(str_list)
    for i in range(len(str_list)):
        if str_list[i] >= '0' and str_list[i] <= '6':
            str_list[i] = chr(ord(str_list[i]) + random.randint(0, 4))
        elif str_list[i] >= 'a' and str_list[i] <= 'q':
            str_list[i] = chr(ord(str_list[i]) + random.randint(0, 9))
        elif str_list[i] >= 'A' and str_list[i] <= 'Q':
            str_list[i] = chr(ord(str_list[i]) + random.randint(0, 9))
    # print("".join(str_list))
    return "".join(str_list)


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


def closeWindow():
    # print("关闭")
    root.destroy()


if __name__ == "__main__":
    headers["user-agent"] = headers_list[random.randint(0, len(headers_list) - 1)]
    headers["cookie"] = "token=sid." + randomCookies()

    root.geometry("300x500+150+150")
    root.resizable(False, False)

    root.title("2023/12/2")

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

    root.protocol("WM_DELETE_WINDOW", closeWindow)

    value = tkinter.IntVar()
    tmplable = Label(root)
    InsertTotextInfo("兴趣使然,能用就行\n", nowtime="")
    InsertTotextInfo("\n", nowtime="")



    InsertTotextInfo("更新可以去github网址\n", nowtime="")
    InsertTotextInfo("github.com/Roxy2222/-Mooc-/\n", nowtime="")

    root.mainloop()
