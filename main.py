import random
import re
from tkinter import *
import tkinter.ttk
from tkinter.ttk import Combobox
import tkinter
import time
from wcwidth import wcswidth

import requests
from ddddocr import DdddOcr

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
# 默认刷取网站
HOST = "zxshixun.cqcst.edu.cn"
# 验证码识别
ocr = DdddOcr(old=True, show_ad=False, beta=True)
# 最大尝试次数
MAX_ATTEMPT_COUNT = 3
# 可视化界面
root = Tk()
# 行数
textCol = 1.0


def study(data: dict, url: str):
	global TIME, progressBar, MAX_ATTEMPT_COUNT
	
	count = 0
	InsertTotextInfo(" 本集视频实际时长%d分钟\n" % (TIME // 60 + 1))
	InsertTotextInfo("                ****进度条持续卡住请检查网络,或重新登陆,30秒一更新****\n", nowTime="")
	
	root.after(30000, lambda: value.set(1))
	tempLabel.wait_variable(value)
	
	postOnline()
	for time in range(data["studyTime"] + 30, TIME + 20, 30):
		data['studyTime'] = time
		resp = ""
		for i in range(MAX_ATTEMPT_COUNT):
			try:
				resp = requests.post(url=url, headers=headers, data=data, verify=False)
				break
			except:
				InsertTotextInfo(" 学习时间提交失败 次数%d\n" % (i + 1))
		
		print(resp.text)
		if "提交学时成功" in resp.text:
			res = 100 if time / TIME > 1.0 else time / TIME * 100
			progressBar["value"] = int(res)
		else:
			InsertTotextInfo(" 学时提交失败\n")
		root.update()
		
		# online提交
		count = count + 1
		if count % 4 == 0:
			postOnline()
		
		root.after(30000, lambda: value.set(1))
		tempLabel.wait_variable(value)


def getStudyId(nodeld: str, url: str):
	global MAX_ATTEMPT_COUNT
	data = {"nodeId": nodeld, "studyId": 0, "studyTime": 1, "code": ""}
	data["nodeId"] = nodeld  # 初始化复制可能失败,重复赋值,python3.8版本会出现这个问题,更新后不想重新测试
	
	studyId = []
	for i in range(MAX_ATTEMPT_COUNT):
		code = getCode()
		data['code'] = code + '_'
		resp = requests.post(url=url, headers=headers, data=data, verify=False).text
		
		studyIdEx = '"studyId":(\d{8}),'
		studyId = re.findall(studyIdEx, resp, re.M)
		
		if studyId:
			break
		else:
			if i == 2:
				InsertTotextInfo(" 程序暂停,请重新登陆\n", nowTime="")
				exit(-1)
		root.after(random.randint(3, 6) * 1000, lambda: value.set(1))
		tempLabel.wait_variable(value)
	
	return studyId[0]


# 获取每个课程的courseId
def getCourseId():
	url = "https://" + HOST + "/user/index?kind=run"
	resp = requests.get(url=url, headers=headers, verify=False).text
	
	course_id_ex = '\"/user/course\?courseId\=(\d+)">'
	# 去重
	course_id = set(re.findall(course_id_ex, resp, re.M))
	
	return course_id


def getTime(course_id: str) -> [dict, list]:
	def formatString(s, width) -> str:
		return s + " " * (width - wcswidth(s))
	
	url = "https://" + HOST + "/user/study_record.json"
	params = {
		"courseId": course_id,
		"page": 1,
		"_": "1666320828" + str(random.randint(100, 999))
	}
	
	studyNodeIdDict = {}
	courserNameList = []
	# 学习状态
	stateEx = '未学|已学'
	# 课程id
	nodeIdEx = "nodeId\=(\d+)"
	# 课程名
	courserName_ex = "\"name\":\"(.*?)\""
	# 视频已观看时长
	videoTime = '"viewedDuration":"(\d{2}:\d{2}:\d{2})"'
	# 视频需观看时长
	videoRequireTime = '"videoDuration":"(\d{2}:\d{2}:\d{2})"'
	
	# 最后一集
	endNode = 0
	# 最后一集,但是临时
	endNodeTemp = 0
	for i in range(1, 100, 1):
		params["page"] = i
		InsertTotextInfo(
			"===========================================第%d页============================================\n" % i,
			nowTime="")
		resp_info = requests.get(url=url, headers=headers, params=params, verify=False).text
		for state, nodeId, time, alltime, courserName in zip(re.findall(stateEx, resp_info, re.M),  # 观看状态
															 re.findall(nodeIdEx, resp_info, re.M),  # 视频nodeid
															 re.findall(videoTime, resp_info, re.M),  # 已观看时长
															 re.findall(videoRequireTime, resp_info, re.M),  # 需观看时长
															 re.findall(courserName_ex, resp_info, re.M)):  # 课程名
			# InsertTotextInfo(f" {state:<4}{courserName:<50}时长{alltime:<10}\n", nowTime="")
			InsertTotextInfo(f" {state:<4}{formatString(courserName, 71)}时长{alltime:<10}\n", nowTime="")
			if state == "未学":
				studyNodeIdDict[nodeId] = (int(alltime[0:2]) * 3600 + int(alltime[3:5]) * 60 + int(alltime[6:8])) - \
										  (int(time[0:2]) * 3600 + int(time[3:5]) * 60 + int(time[6:8]))
				courserNameList.append(courserName)
			endNodeTemp = nodeId
		
		# 小于20条记录代表已经到头
		if len(re.findall(stateEx, resp_info, re.M)) < 20:
			return [studyNodeIdDict, courserNameList]
		# 最后一页刚好20条记录,去除前二十条记录
		elif endNodeTemp == endNode:
			return [studyNodeIdDict[:-20], courserNameList[:-20]]
		
		endNode = endNodeTemp


def postStudy():
	global TIME, start_time, progressBar
	url = "https://" + HOST + "/user/node/study"
	
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
			# TIME = int(vtime[0:2]) * 3600 + int(vtime[3:5]) * 60 + int(vtime[6:])
			TIME = vtime
			
			InsertTotextInfo(" \n ", nowTime="")
			InsertTotextInfo("正在学习--->%s\n" % studyTime_and_courserName[1][courserCount])
			progressBar["value"] = 0
			
			# 需要观看的时长小于10s就可以跳过
			if TIME < 10:
				InsertTotextInfo(" 跳过\n")
				continue
			
			data["nodeId"] = nodeid
			data["studyId"] = getStudyId(nodeid, url)
			
			n = random.randint(3, 6)
			data["studyTime"] = n
			root.after(n * 1000, lambda: value.set(1))
			tempLabel.wait_variable(value)
			
			if len(data["studyId"]) == 8:
				study(data, url)
			else:
				InsertTotextInfo(" %d刷取失败" % nodeid)
			watched_count += 1
			courserCount += 1


def postOnline(count=1):
	url = "https://" + HOST + "/user/online"
	
	data = {
		'msg': "ok",
		'status': 'true'
	}
	
	resp = requests.post(url=url, data=data, headers=headers, verify=False).text
	if 'ok' not in resp and 'true' not in resp:
		return False if count == 4 else postOnline(count + 1)
	return True


def getCode():
	global ocr
	url = "https://" + HOST + "/service/code/aa?r="
	f = random.random()
	url = url + str(f)
	
	code_img = requests.get(url=url, headers=headers, verify=False).content
	
	res = ocr.classification(code_img)
	InsertTotextInfo(" 本集验证码是:%s\n" % res)
	return res


def GetLoginKey():
	global ocr
	parser = {
		"r": "{time()}"
	}
	for i in range(3):
		try:
			InsertTotextInfo(" 请求登录验证码\n")
			keytmp = requests.get(url="https://" + HOST + "/service/code", params=parser, headers=headers,
								  verify=False).content
			
			key = ocr.classification(keytmp)
			return key
		except:
			InsertTotextInfo(" 验证码识别/获取错误 %d\n" % (i + 1))


def InsertTotextInfo(info: str, nowTime="1", sleep_time=200) -> None:
	global textCol
	if nowTime == "1":
		nowTime = time.strftime("%H:%M:%S")
	
	infoText.insert(str(textCol), nowTime + info)
	textCol += 1
	infoText.update()
	infoText.see(END)
	
	root.after(sleep_time, lambda: value.set(1))
	tempLabel.wait_variable(value)


def randomCookies() -> str:
	strList = list("K7MvIHt8HPC1bqyeNJK23lfsxaDuhY")
	random.shuffle(strList)
	for i in range(len(strList)):
		if '0' <= strList[i] <= '6':
			strList[i] = chr(ord(strList[i]) + random.randint(0, 4))
		elif 'a' <= strList[i] <= 'q':
			strList[i] = chr(ord(strList[i]) + random.randint(0, 9))
		elif 'A' <= strList[i] <= 'Q':
			strList[i] = chr(ord(strList[i]) + random.randint(0, 9))
	return "".join(strList)


def login():
	global HOST, MAX_ATTEMPT_COUNT
	infoText.delete("1.0", "end")
	
	tmpUrl = urlCombox.get()
	if tmpUrl != "":
		HOST = tmpUrl.split("-")[-1]
	loginUrl = "https://" + HOST + "/user/login"
	username = usernameEntry.get().strip()
	password = passwordEntry.get().strip()
	
	data = {
		"username": username,
		"password": password,
		"code": "",
		"redirect": ""
	}
	
	InsertTotextInfo(" 当前刷取地址: " + HOST + "\n")
	if data["username"] == "" or data["password"] == "":
		InsertTotextInfo(" 账号或密码为空\n")
		return
	
	button_enterOK.config(state=DISABLED)
	urlCombox.config(state=DISABLED)
	showPwd.config(state=DISABLED)
	
	urlFlag = True
	
	for i in range(MAX_ATTEMPT_COUNT):
		data["code"] = GetLoginKey()
		
		InsertTotextInfo(" 第%d次登录尝试,验证码为%s\n" % (i + 1, data["code"]))
		
		resp = requests.post(url=loginUrl, data=data, headers=headers, verify=False).text
		if "登录成功" in resp:
			InsertTotextInfo(" 登录成功\n")
			button_enterOK.config(state=ACTIVE)
			postStudy()
			# 刷取完成后清空列出课程目录提示刷取完成
			infoText.delete("1.0", "end")
			postStudy()
			urlCombox.config(state=ACTIVE)
			InsertTotextInfo("\t\t\t刷取完毕!!!\n")
			InsertTotextInfo("\t\t\t刷取完毕!!!\n")
			InsertTotextInfo("\t\t\t刷取完毕!!!\n")
			return
		InsertTotextInfo(" 登录失败,等待重试\n")
		
		if i != MAX_ATTEMPT_COUNT - 1:
			root.after(random.randint(5, 10 + 1) * 1000, lambda: value.set(1))
			tempLabel.wait_variable(value)
		
		if i == MAX_ATTEMPT_COUNT - 1 and "不正确" not in resp:
			urlFlag = False
	
	button_enterOK.config(state=ACTIVE)
	urlCombox.config(state=ACTIVE)
	showPwd.config(state=ACTIVE)
	
	InsertTotextInfo("\n", nowTime="")
	if urlFlag:
		InsertTotextInfo(" 请检查你的账号 or 密码\n")
	else:
		InsertTotextInfo(info="\n")
		InsertTotextInfo(" 如果验证码不为None,那么你的url(网址)大概率输入错误\n", nowTime="")
		InsertTotextInfo(" 你刷取的网站因该是登录时需要选择学校的\n", nowTime="")
		InsertTotextInfo(" 你可以尝试登录进去后再复制url\n", nowTime="")
		InsertTotextInfo(" 当你尝试过依旧不行时,请联系我:frank2222@foxmail.com\n", nowTime="")
	root.after(5000, lambda: value.set(1))
	tempLabel.wait_variable(value)


def introduce() -> None:
	InsertTotextInfo("兴趣使然,能用就行\n", nowTime="")
	InsertTotextInfo("\n", nowTime="")
	InsertTotextInfo("刷课之前可以看看有没有新版本,直接复制网址就行\n", nowTime="")
	
	InsertTotextInfo("项目地址:https://github.com/imRoxy2222/-Mooc-\n", nowTime="")
	
	InsertTotextInfo("\n", nowTime="")
	InsertTotextInfo("原视频多长就需要刷取多久,只是为了挂机刷取才写的这个脚本\n", nowTime="")
	InsertTotextInfo("倍速/极速刷取大概率被检测(太久之前测试的了,不清楚了)\n", nowTime="")


def create_toplevel():
	top = Toplevel()
	top.geometry("330x500")
	top.resizable(False, False)
	top.title('介绍')
	msg = Label(top,
				text="只能输入主机地址\n\n地址最好为登录页面的主机地址\n\n这个是完整地址:\nhttps://zxshixun.cqcst.edu.cn/user\n这个是主机地址:\nzxshixun.cqcst.edu.cn\n"
					 "请输入主机地址,否则不保证可用", font=("微软雅黑", 15), fg="black")
	msg.grid()
	Label(top, text="只能输入主机地址\n否则无效", font=("微软雅黑", 15), fg="red").grid()


if __name__ == "__main__":
	headers["user-agent"] = headers_list[random.randint(0, len(headers_list) - 1)]
	headers["cookie"] = "token=sid." + randomCookies()
	
	root.geometry("700x550+150+150")  # 300x500+150+150
	root.resizable(False, False)
	
	root.title("update time:2024/11/5 version:0.4.5.1fix")
	
	# 账号密码作者介绍label
	usernameLabel = Label(root, text="账号:", font=("宋体", 13), fg="black")
	passwordLabel = Label(root, text="密码:", font=("宋体", 13), fg="black")
	infoLabel = Label(root, text="author: frank2222@foxmail.com", font=("consolas", 12), fg="red")
	usernameLabel.place(x=20, y=25)
	passwordLabel.place(x=300, y=25)
	infoLabel.place(x=20, y=510)
	
	# 账号密码框
	usernameEntry = Entry(root, font=("微软雅黑", 13), fg="black")
	passwordEntry = Entry(root, font=("微软雅黑", 13), fg="black", show="*")
	usernameEntry.place(x=75, y=25)
	passwordEntry.place(x=350, y=25)
	
	# 确定按钮
	button_enterOK = Button(root, text="确定", font=("微软雅黑", 15), fg="black", command=login)
	button_enterOK.place(x=630, y=15)
	
	# 显示隐藏密码按钮
	showPwd = Button(text="show")
	showPwd.place(x=550, y=23)
	showPwd.bind("<ButtonPress-1>", lambda e: passwordEntry.config(show=""))
	showPwd.bind("<ButtonRelease-1>", lambda e: passwordEntry.config(show="*"))
	
	# 输入url
	urlLabel = Label(root, text="要刷取的网站:", font=("宋体", 13), fg="black")
	urlButton = Button(root, text="不知道怎么用点我", font=("微软雅黑", 9), fg="red", command=create_toplevel)
	urlLabel.place(x=20, y=85)
	urlButton.place(x=570, y=80)
	urlList = ["英华学堂,选修课选我-mooc.cqcst.edu.cn",
			   "数字化实习实训平台-zxshixun.cqcst.edu.cn",
			   "社会公益平台-gyxy.cqcst.edu.cn",
			   "烺际数字化教学实训平台-cqucc.langjikeji.com",
			   "没有请手动输入,请查看\"不知道怎么用点我\""]
	urlCombox = Combobox(root, values=urlList, width=50)
	urlCombox.set(urlList[0])
	urlCombox.place(x=150, y=85)
	
	infoText = Text(root, width=92, height=28, undo=True, autoseparators=False)
	scrollbar = tkinter.Scrollbar(root, orient="vertical", command=infoText.yview)
	infoText.config(yscrollcommand=scrollbar.set)
	
	scrollbar.place(x=671, y=130, height=370)
	infoText.bind("<Key>", lambda e: "break")
	infoText.bind("<Control-c>", lambda e: "active")
	infoText.place(x=23, y=130)
	
	progressBar = tkinter.ttk.Progressbar(root, length=200)
	progressBar.place(x=470, y=510)
	progressBar["maximum"] = 100
	progressBar["value"] = 0
	
	root.protocol("WM_DELETE_WINDOW", root.destroy)
	
	value = tkinter.IntVar()
	tempLabel = Label(root)
	
	introduce()
	
	root.mainloop()
