#coding=utf-8
import glob
import errno
import time
import userManager
import Info
import io
import garageInfo
import smtp as sender
import lineNotify as lineSender
import operator
import datetime
# define log keyword
def initKeyWork(keep_phrases,checkAPIList,actionList,keepLineDetail):
    keep_phrases = ["page=",
                    "_GI",
                    "-85",
                    "Reservation",
                    "voiceString",
                    "Fail",
                    "popup",
                    "Open InOutGate",
                    "Network-<",
                    "leaveGarageName",
                    "garage_id",
                    "flow_gatecontrol",
                    "switchToInLotState",
                    "[AppDelegate checkUpdate]",
                    "[AppDelegate applicationDidEnterBackground:]",
                    "[AppDelegate applicationWillEnterForeground:]",
                    "[LOG_FROM]",
                    "[Gate]Cancel InOutGat",
                    "centralManagerDidUpdateState",
                    "send command to mcu",
                    "Gate Password Success",
                    "Gate Open Success",
                    "didDisconnectPeripheral",
                    "didConnectPeripheral",
                    "[Gate]BLE ON",
                    "[Gate]BLE OFF",
                    "[AppDelegate applicationDidBecomeActive:]",
                    "[AppDelegate applicationWillResignActive:]",
                    "GateDelay"
                    ]
    keepLineDetail = [
                      "[AppDelegate checkUpdate]",
                      "[AppDelegate applicationDidEnterBackground:]",
                      "[AppDelegate applicationWillEnterForeground:]",
                      "centralManagerDidUpdateState",
                      "Device",
                      "WIFI",
                      "centralManagerDidUpdateState",
                      "send command to mcu",
                      "Gate Password Success",
                      "Gate Open Success",
                      "didDisconnectPeripheral",
                      "didConnectPeripheral",
                      "[Gate]Cancel InOutGat",
                      "[AppDelegate applicationWillResignActive:]",
                      "[AppDelegate applicationDidBecomeActive:]",
                      "GateDelay"
                    ]
    checkAPIList = [
                    "checkGarage",
                    "garage_enter_check_reservechange",
                    "garage_enter_confirm"
                    ]


    actionList = ["_GI", "popup", "Open InOutGate", "leaveGarageName", "checkUpdate","applicationDidEnterBackground","applicationWillEnterForeground","didDisconnectPeripheral","didConnectPeripheral","[Gate]Cancel InOutGat","[Gate]BLE","AppDelegate applicationDidBecomeActive","AppDelegate applicationWillResignActive" ]
    return (keep_phrases, checkAPIList, actionList,keepLineDetail)

def removeMeaninglessSymbol(info):
    info = info.replace("<m>","")
    return info

# 塞選keyWord
def getKeyWordFromLog(keep_phrases):
    count = 0
    analysisLog=""
    for line in f:
        for phrase in keep_phrases:
            if phrase in line or count <= 10 :
                str1 = line.split(",")
                try:
                    time = str1[0].split(" ")[0] +" "+str1[0].split(" ")[1]
                except:
                    time = ""
                info = str1[-1]
                for element in keepLineDetail:
                    if element in line:
                        info = ''.join(str1[1:])
                        if "WIFI" in line:
                            info = "Network <WIFI> PaKing-" + str1[-1].replace(" ","" )

                mark = ""
                if "Fail" in line:
                    mark = "!!!"
                if "Success" in line or "Request" in line:
                    tmp = info.split("page=")
                    if (len(tmp)>1):
                        info = tmp[1]
                    info = info.replace(": {","")
                
                info = removeMeaninglessSymbol(info)
                analysisLog = analysisLog+ mark + time+" || "+ info + "\n"
                break
        count = count + 1
    return analysisLog

# 設定使用者資料
def setUserInfo(analysisLog):
    infoLines = analysisLog.split("\n")
    name = infoLines[2].split("||")[-1].split("的")[0].replace(" ","")
    system = infoLines[4].split("||")[-1]
    devie = infoLines[6].split(":")[-1]
    version = infoLines[8].split("||")[-1]
    reservation = "無"
    garageName = ""
    signalSrc = ""
    for line in infoLines:
        if "Carrier" in line:
            signalSrc = line.split(" ")[-1]
            break;
    for line in infoLines:
        if "isGarageReservation = 1" in line:
            reservation = "有"
        if "garage_id" in line and garageName == "":
            garageName = garageName + line.split("=")[-1].replace(";","")
    if garageName != "":
        garageName = garageInfo.getDetailGarageName(garageName.replace(" ",""))

    user = userManager.Info(name,system,devie,version,signalSrc,reservation,garageName)
    return user

# API狀態設定
def setApiState(analysisLog, info):
    infoLines = analysisLog.split("\n")
    apiName = ""
    state = ""
    start_time = ""
    end_time = ""
    errorMsg = ""
    network = ""
    apiName = info
    count = 0
    for line in infoLines:
        if info in line and "Request" in line and start_time == "":
            start_time = line.split("||")[0]
        if info in line and "Success" in line and end_time == "" :
            end_time = line.split("||")[0]
        if start_time != "" and end_time != "":
            state = "Success"
            if "Network" in line and network == "":
                network = line.split(" ")[-1]
        if "Network" in line and start_time != "" and end_time == "" and network == "":
            network = line.split(" ")[-1]
        if info in line and "Request" in line:
            count = count + 1


    if start_time == "":
        errorMsg = "NO Request!"
    elif end_time == "":
        errorMsg = "Request but no feedback success!"

    if errorMsg != "":
        state = "Fail"

    api = Info.API_info(apiName,state,start_time,end_time,errorMsg,network,count)

    return api


# 使用者動作設定
def getUserActionTrack(analysisLog, act, user, actionlist):
    infoLines = analysisLog.split("\n")
    actionName = ""
    start_time = ""
    findGI = False
    isPopup = False
    isPressOpen = False
    isLeave = False
    for line in infoLines:
        if act in line:
            if (act == "_GI" and findGI == False):
                actionName = "收到第一個GI"
                findGI = True
            elif (act == "popup" and isPopup == False):
                actionName = "入閘POP_UP"
                isPopup = True
            elif (act == "Open InOutGate" and isPressOpen == False):
                actionName = "按下入閘按鈕"
                isPressOpen = True
            elif (act == "leaveGarageName" and isLeave == False):
                actionName = "離開車廠紀錄"
                isLeave = True
            elif (act == "checkUpdate"):
                actionName = "啟動App程序"
            elif (act == "applicationWillEnterForeground"):
                actionName = "進入App前景"
            elif (act == "applicationDidEnterBackground"):
                actionName = "退到App背景"
            elif ( act == "didConnectPeripheral" and "duration" in line):
                actionName = "[didConnectPeripheral]" + line.split(" ")[-1]
            elif ( act == "didDisconnectPeripheral" and "pName" in line ):
                actionName = "[didDisconnectPeripheral]"
            elif ( act == "[Gate]Cancel InOutGat" ):
                actionName = "[Gate]Cancel InOutGat";
            elif ( act == "[Gate]BLE" ):
                actionName = line.split("|")[-1]
            elif (act == "AppDelegate applicationWillResignActive"):
                actionName = "[AppDelegate] applicationWillResignActive"
            elif ( act == "AppDelegate applicationDidBecomeActive" ):
                actionName = "[AppDelegate] applicationDidBecomeActive"
            start_time = line.split("||")[0]
            start_time = start_time.split(".")[0]
            if ( actionName!="" ):
                actionlist.append(Info.Action(actionName,start_time))
                actionName = ""
                start_time = ""

    if  (act == "_GI" and actionName == "" and findGI == False):
        actionName= "沒有收到GI"
        actionlist.append(Info.Action(actionName,start_time))
    if  (act == "popup" and actionName == "" and isPopup == False):
        actionName= "沒有跳出開閘按鈕"
        actionlist.append(Info.Action(actionName,start_time))
    if  (act == "Open InOutGate" and actionName == "" and "Beacon" in user.getGarage() and isPressOpen == False):
        actionName= "沒有按下開閘按鈕"
        actionlist.append(Info.Action(actionName,start_time))
    if (act == "leaveGarageName" and actionName == "" and isLeave == False):
        actionName= "沒有離開車廠紀錄"
        actionlist.append(Info.Action(actionName,start_time))

    return actionlist

# 分析後Log輸出總內容
def getOutputText(user,apiInfo,action):
    userResult = user.getAllInfoText()
    State = ""
    for act in action:
        State = State + act.getAllInfoText()
    userResult = userResult + getSpendTimefromGItoPopUp(State)
    State = State+"///////////////////////////////////\n\n"
    for t in apiInfo:
        State = State + t.getAllInfoText()
    result = userResult+State
    return result

# 網路切換時機
def getNetworkSwitchTimeStamp(analysisLog):
    infoLines = analysisLog.split("\n")
    network  = "";
    time ="";
    strNetworkSwitch = "///////////////////////////////////\n網路切換時機\n";
    switchToInLotState = "";
    for line in infoLines:
        time = line.split("||")[0]
        if network == "" and "Network" in line:
            network = line.split(" ")[-1]
            strNetworkSwitch = strNetworkSwitch + time + network + " (first)\n"
        else:
            if "Network" in line and network != line.split(" ")[-1]:
                network = line.split(" ")[-1]
                strNetworkSwitch = strNetworkSwitch + time + network + "\n"

    return strNetworkSwitch

# 取得 收到第一個GI-入閘POP_UP 時間
def getSpendTimefromGItoPopUp(result):
    infoLines = result.split("\n")
    start_time = ""
    end_time =""
    strSpendTime = "第一次GI 到 Pop Up 時間 : ";
    sec = 0
    for line in infoLines:
        time = line.split(" )\t")[0].replace("( ","")
        if "收到第一個GI" in line:
            start_time = time
        if "入閘POP_UP" in line:
            end_time = time
    if start_time != "" and end_time != "" :
        min = float(end_time.split(":")[-2])-float(start_time.split(":")[-2])
        try:
            sec = float(end_time.split(":")[-1])-float(start_time.split(":")[-1])
        except:
            sec = float(end_time.split(":")[-1][:-6])-float(start_time.split(":")[-1][:-6])
            if min < 0 :
                min = min + 60
            if sec < 0 :
                sec = sec + 60
                sec = sec + min*60
    strSpendTime = strSpendTime + str(sec) + "秒" + "\n\n///////////////////////////////////\n"
    return strSpendTime

def getLogFrom(analysisLog):
    infoLines = analysisLog.split("\n")
    for line in infoLines:
        if "[LOG_FROM]" in line:
            return "\n"+line.split("|")[-1].replace(" ","")+"\n\n"
    return ""

def checkFailMsg(analysisLog, result):
    now = datetime.datetime.now()
    infoLines = analysisLog.split("\n")
    for line in infoLines:
        if "GateDelay" in line and now.strftime("%Y-%m-%d") in line:
            return "Fail"

    if "Fail" in result:
        return "Fail"

    return "Success"

#########################################

path = 'LogFile/'+time.strftime("%Y%m%d", time.localtime())+"/*.log"
print(path)
files = glob.glob(path)
keep_phrases=[]
checkAPIList=[]
actionList=[]
keepLineDetail=[]
keep_phrases, checkAPIList, actionList, keepLineDetail = initKeyWork(keep_phrases, checkAPIList, actionList, keepLineDetail)

state = "Success"
apiInfoList = []
action=[]
result=""
print(files)
for name in files:
    try:
        with open(name,encoding='utf-8') as f:
            f = f.readlines()
        analysisLog = getKeyWordFromLog(keep_phrases)
        if len(f) < 10:
            break;
        
        
        ############################# get User info
        user = setUserInfo(analysisLog)
        if "車辨" in user.getGarage():
            checkAPIList.append("ANPR_check_enter")
            checkAPIList.append("ANPR_binding")
        ############################# get AIP info
        for api in checkAPIList:
            apiInfoList.append(setApiState(analysisLog,api))
        apiInfoList = sorted(apiInfoList, key=operator.attrgetter('start_time'))
        ############################# get action info
        for act in actionList:
            action = getUserActionTrack(analysisLog,act,user,action)
        action = sorted(action, key=operator.attrgetter('start_time'))
        ############################# get result info
        result = getOutputText(user,apiInfoList,action)
        ############################# analysis is fail or not
        if (checkFailMsg(analysisLog, result) == "Fail"):
            state = "Fail"
    

        simpleResult = getLogFrom(analysisLog) +  result + getNetworkSwitchTimeStamp(analysisLog)
        result = simpleResult + "\n\n--------detail--------\n\n" + analysisLog

        name = name +"_"+state+"_"+user.getName()+".txt"
        if (len(glob.glob(name))==0):
            with io.open(name, "w",encoding='utf8') as text_file:text_file.write("%s" % result)
            if state == "Fail":
                #sender.DebugSendMail("檔名："+name.split("/")[-1],result)
                lineSender.SendLineNotify("檔名："+name.split("/")[-1],simpleResult)

        action.clear()
        apiInfoList.clear()
        result=""
        state = "Success"
        keep_phrases, checkAPIList, actionList,keepLineDetail = initKeyWork(keep_phrases, checkAPIList, actionList,keepLineDetail)

    except IOError as exc:
        state = "不正常使用"
        with open(name+"_"+state+"_"+user.getName()+".txt", "w") as text_file:text_file.write("%s" % analysisLog)
        if exc.errno != errno.EISDIR:
            raise








