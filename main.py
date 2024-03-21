import random
import re
from time import sleep
from tkinter import *
import tkinter.ttk
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
    global TIME, progressBar

    count = 0
    InsertTotextInfo(" 本集大约需要%d分钟\n" % (TIME // 60 + 1))
    InsertTotextInfo("                ****进度条持续卡住请检查网络,或重新登陆,30秒一更新****\n", nowtime="")

    root.after(30000, lambda: value.set(1))
    tmplable.wait_variable(value)

    postOnline()
    for time in range(data["studyTime"] + 30, TIME + 20, 30):
        data['studyTime'] = time
        resp = ""
        for i in range(3):
            try:
                resp = requests.post(url=url, headers=headers, data=data, verify=False)
                break
            except:
                InsertTotextInfo(" 学习时间提交失败 次数%d\n" % (i + 1))

        if "提交学时成功" in resp.text:
            res = 100 if time / TIME > 1.0 else time / TIME * 100
            print(res)
            progressBar["value"] = int(res)
        else:
            InsertTotextInfo(" 学时提交失败\n")
        root.update()

        # online提交
        count = count + 1
        if count % 4 == 0:
            postOnline()
        #     a = InsertTotextInfo(" online提交成功\n") if postOnline() else InsertTotextInfo(" online提交失败\n")

        root.after(30000, lambda: value.set(1))
        tmplable.wait_variable(value)


def getStudyId(nodeld: str, url: str):
    data = {"nodeId": nodeld, "studyId": 0, "studyTime": 1, "code": ""}
    data["nodeId"] = nodeld  # 初始化复制可能失败,重复赋值

    for i in range(3):
        code = getCode()
        data['code'] = code + '_'
        resp = requests.post(url=url, headers=headers, data=data, verify=False).text

        studyid_ex = '"studyId":(\d{8}),'
        studyid = re.findall(studyid_ex, resp, re.M)

        if studyid:
            break
        else:
            if i == 2:
                InsertTotextInfo(" 程序暂停,请重新登陆\n", nowtime="")
                exit(-1)
        root.after(random.randint(3, 10) * 1000, lambda: value.set(1))
        tmplable.wait_variable(value)

    return studyid[0]


# 获取每个课程的courseId
def getCourseId():
    url = "https://mooc.cqcst.edu.cn/user/index?kind=run"
    resp = requests.get(url=url, headers=headers, verify=False).text

    course_id_ex = '\"/user/course\?courseId\=(\d+)">'
    # 去重
    course_id = set(re.findall(course_id_ex, resp, re.M))

    return course_id


def getTime(course_id: str) -> [dict, list]:
    url = "https://mooc.cqcst.edu.cn/user/study_record.json"
    params = {
        "courseId": course_id,
        "page": 1,
        "_": "1666320828" + str(random.randint(100, 999))
    }

    study_nodeid_dct = {}
    courserNameList = []
    # 学习状态
    state_ex = '未学|已学'
    # 课程id
    nodeid_ex = "nodeId\=(\d+)"
    # 课程名
    courserName_ex = "\"name\":\"(.*?)\""
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
        InsertTotextInfo(
            "===========================================第%d页============================================\n" % i,
            nowtime="")
        resp_info = requests.get(url=url, headers=headers, params=params, verify=False).text
        for state, nodeid, time, alltime, courserName in zip(re.findall(state_ex, resp_info, re.M),  # 观看状态
                                                             re.findall(nodeid_ex, resp_info, re.M),  # 视频nodeid
                                                             re.findall(video_time, resp_info, re.M),  # 已观看时长
                                                             re.findall(video_requir_time, resp_info, re.M),  # 需观看时长
                                                             re.findall(courserName_ex, resp_info, re.M)):  # 课程名
            # InsertTotextInfo(" %s %s    视频时长%s\n" % (state, courserName, alltime))
            InsertTotextInfo(f" {state:<4}{courserName:<40}视频时长{alltime:<10}\n")
            if state == "未学":
                study_nodeid_dct[nodeid] = (int(alltime[0:2]) * 3600 + int(alltime[3:5]) * 60 + int(alltime[6:8])) - \
                                           (int(time[0:2]) * 3600 + int(time[3:5]) * 60 + int(time[6:8]))
                courserNameList.append(courserName)
            end_nodeid_temp = nodeid

        # 小于20条记录代表已经到头
        if len(re.findall(state_ex, resp_info, re.M)) < 20:
            return [study_nodeid_dct, courserNameList]
        # 最后一页刚好20条记录,去除前二十条记录
        elif end_nodeid_temp == end_nodeid:
            return [study_nodeid_dct, courserNameList]
        end_nodeid = end_nodeid_temp


def postStudy():
    global TIME, start_time, progressBar
    url = "https://mooc.cqcst.edu.cn/user/node/study"

    data = {
        'nodeId': "",
        'studyId': 0,
        'studyTime': 1
    }

    watched_count = 0

    watched_nodeid = []
    courserCount = 0
    # 获取搜索课程
    course_list = getCourseId()
    for course_id in course_list:
        studyTime_and_courserName = getTime(course_id)
        for nodeid, vtime in studyTime_and_courserName[0].items():
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

            InsertTotextInfo(" \n ", nowtime="")
            # InsertTotextInfo(" 正在学习%s\n" % nodeid)
            InsertTotextInfo(" 正在学习--->%s\n" % studyTime_and_courserName[1][courserCount])
            progressBar["value"] = 0

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

            if len(data["studyId"]) == 8:
                study(data, url)
            else:
                InsertTotextInfo(" %d刷取失败" % nodeid)
            watched_count += 1
            courserCount += 1


def postOnline(count=1):
    url = "https://mooc.cqcst.edu.cn/user/online"

    data = {
        'msg': "ok",
        'status': 'true'
    }

    resp = requests.post(url=url, data=data, headers=headers, verify=False).text
    if 'ok' not in resp and 'true' not in resp:
        return False if count == 4 else postOnline(count + 1)
    return True


def getCode():
    url = "https://mooc.cqcst.edu.cn/service/code/aa?r="
    f = random.random()
    url = url + str(f)

    code_img = requests.get(url=url, headers=headers, verify=False).content

    ocr = DdddOcr(old=True, show_ad=False)

    res = ocr.classification(code_img)
    InsertTotextInfo(" 本集验证码是:%s\n" % res)
    return res


def GetLoginKey():
    parser = {
        "r": "{time()}"
    }
    for i in range(3):
        try:
            InsertTotextInfo(" 请求登录验证码\n")
            keytmp = requests.get(url="https://mooc.cqcst.edu.cn/service/code", params=parser, headers=headers,
                                  verify=False).content
            ocr = DdddOcr(old=True, show_ad=False)
            key = ocr.classification(keytmp)
            return key
        except:
            InsertTotextInfo(" 验证码识别/获取错误 %d\n" % (i + 1))


def InsertTotextInfo(info: str, nowtime="1", sleep_time=200) -> None:
    global textCol
    if nowtime == "1":
        nowtime = time.strftime("%H:%M:%S")

    text_info.insert(str(textCol), nowtime + info)
    textCol += 1
    text_info.update()
    text_info.see(END)

    root.after(sleep_time, lambda: value.set(1))
    tmplable.wait_variable(value)


def randomCookies():
    str_list = list("K7MvIHt8HPC1bqyeNJK23lfsxaDuhY")
    random.shuffle(str_list)
    for i in range(len(str_list)):
        if '0' <= str_list[i] <= '6':
            str_list[i] = chr(ord(str_list[i]) + random.randint(0, 4))
        elif 'a' <= str_list[i] <= 'q':
            str_list[i] = chr(ord(str_list[i]) + random.randint(0, 9))
        elif 'A' <= str_list[i] <= 'Q':
            str_list[i] = chr(ord(str_list[i]) + random.randint(0, 9))
    return "".join(str_list)


def login():
    loginUrl = "https://mooc.cqcst.edu.cn/user/login"
    username = entry_username.get().strip()
    password = entry_passwd.get().strip()

    data = {
        "username": username,
        "password": password,
        "code": "",
        "redirect": ""
    }

    if data["username"] == "" or data["password"] == "":
        InsertTotextInfo(" 账号或密码为空\n")
        return

    for i in range(2):
        data["code"] = GetLoginKey()

        InsertTotextInfo(" 第%d次登录尝试,验证码为%s\n" % (i + 1, data["code"]))

        resp = requests.post(url=loginUrl, data=data, headers=headers, verify=False).text
        if "登录成功" in resp:
            InsertTotextInfo(" 登录成功\n")
            postStudy()
            exit()
        InsertTotextInfo(" 登录失败,等待重试\n")

        root.after(random.randint(5, 10 + 1) * 1000, lambda: value.set(1))
        tmplable.wait_variable(value)

        sleep(3)

    InsertTotextInfo(" 请检查你的账号 or 密码\n")
    root.after(5000, lambda: value.set(1))
    tmplable.wait_variable(value)


def closeWindow():
    root.destroy()


def introduce():
    InsertTotextInfo("兴趣使然,能用就行\n", nowtime="")
    InsertTotextInfo("\n", nowtime="")
    InsertTotextInfo("无法使用请更新\n", nowtime="")
    InsertTotextInfo("https://github.com/imRoxy2222/-Mooc-/\n", nowtime="")

    InsertTotextInfo("\n", nowtime="")
    InsertTotextInfo("原视频多长就需要刷取多久,只是为了挂机刷取才写的这个脚本\n", nowtime="")
    InsertTotextInfo("倍速/极速刷取大概率被检测(太久之前测试的了,不清楚了)\n", nowtime="")

    InsertTotextInfo("\n", nowtime="")
    InsertTotextInfo("\n", nowtime="")


if __name__ == "__main__":
    headers["user-agent"] = headers_list[random.randint(0, len(headers_list) - 1)]
    headers["cookie"] = "token=sid." + randomCookies()

    root.geometry("700x500+150+150")  # 300x500+150+150
    root.resizable(False, False)

    root.title("2024/3/21")

    label_username = Label(root, text="账号:", font=("宋体", 13), fg="black")
    label_passwd = Label(root, text="密码:", font=("宋体", 13), fg="black")
    label_info = Label(root, text="author:frank2222", font=("consolas", 12), fg="red")
    label_username.place(x=20, y=25)  # 20 15
    label_passwd.place(x=300, y=25)  # 20 45
    label_info.place(x=20, y=470)  # 280 470

    entry_username = Entry(root, font=("微软雅黑", 13), fg="black")
    entry_passwd = Entry(root, font=("微软雅黑", 13), fg="black", show="*")
    entry_username.place(x=75, y=25)
    entry_passwd.place(x=350, y=25)  # 65 45

    button_enterOK = Button(root, text="确定", font=("微软雅黑", 15), fg="black", command=login)
    button_enterOK.place(x=600, y=15)  # 110 80

    text_info = Text(root, width=92, height=28, undo=True, autoseparators=False)  # 34 25
    scrollbar = tkinter.Scrollbar(root, orient="vertical", command=text_info.yview)
    text_info.config(yscrollcommand=scrollbar.set)

    scrollbar.place(x=671, y=90, height=370)  # 265 123 353
    text_info.bind("<Key>", lambda e: "break")
    text_info.place(x=23, y=90)  # 23 135

    progressBar = tkinter.ttk.Progressbar(root, length=200)
    progressBar.place(x=470, y=470)
    progressBar["maximum"] = 100
    progressBar["value"] = 0

    root.protocol("WM_DELETE_WINDOW", closeWindow)

    value = tkinter.IntVar()
    tmplable = Label(root)

    introduce()

    root.mainloop()
