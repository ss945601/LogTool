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

# define log keyword
def initKeyWork(keep_phrases,checkAPIList,actionList,keepLineDetail):
    keep_phrases = [
                    "switchToInLotState",
                    "[AppDelegate checkUpdate]",
                    "[AppDelegate applicationDidEnterBackground:]",
                    "[AppDelegate applicationWillEnterForeground:]",
                    "page=",
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
                    "Utterance:",
                    "[Locker]Locker Popup",
                    "[Locker]Locker Down Pressed",
                    "cancelLockerButtonPressed",
                    "send [lockerDown] notification",
                    "Gate Open Success",
                    "send [ParkedConfirmNote] notification",
                    "SendTrackingData",
                    "[ParkingBtn][CM]真。黃色按鈕",
                    "[ParkingBtn][DM] Remove data before restart",
                    "indoorFindSpaceNavigationMethod",
                    "Locker off",
                    "&RSSI=",
                    "getNewReserveSpace",
                    "刷成功",
                    "isReserveOver = yes",
                    "[Gate]BLE ON",
                    "[Gate]BLE OFF"
                    ]
    keepLineDetail = [
                        "[AppDelegate checkUpdate]",
                        "[AppDelegate applicationDidEnterBackground:]",
                        "[AppDelegate applicationWillEnterForeground:]",
                        "indoorFindSpaceNavigationMethod",
                        "indoorFindOutMethod",
                        "SendTrackingData:"
                        "Device",
                        "WIFI",
                        "Locker off result",
                        "isReserveOver = yes"
                    ]
    checkAPIList = [
                    ]

    actionList = [ "applicationDidEnterBackground","applicationWillEnterForeground","刷成功前","[CarNavigation]ans","[Locker]Locker Popup","Locker Down Pressed","cancelLockerButtonPressed","voiceString","Locker off fail message","Locker off done", "getNewReserveSpace","[ParkedConfirmNote]","[SendTrackingData]","isReserveOver = yes",                    "[Gate]BLE"]
    return (keep_phrases, checkAPIList, actionList,keepLineDetail)

def removeMeaninglessSymbol(info):
    info = info.replace("<m>","")
    info = info.replace("= {","")
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
                
                if "getNewReserveSpace" in line and "Response" in line:
                    secCount = 0;
                    info = "!![getNewReserveSpace] "
                    for line in f:
                        if secCount > count and "floor" in line:
                            info = info + "floor:" +line.split("=")[-1]+ "  "
                        if secCount > count and "space_name" in line:
                            info = info + "space_name:" +line.split("=")[-1]
                            info = info.replace("\n","")
                            break;
                        secCount = secCount + 1

                if "SendTrackingData:" in line :
                    secCount = 0;
                    info = "[SendTrackingData]\n"
                    for line in f:
                        if secCount > count :
                            info = info + line
                        if secCount > count and "}<m>" in line:
                            break;
                        secCount = secCount + 1

                
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
def getUserActionTrack(analysisLog, act, user,actionlist):
    infoLines = analysisLog.split("\n")
    actionName = ""
    start_time = ""

    for line in infoLines:
        if act in line:
            if (act == "刷成功前"):
                actionName = "!![CarNavigation]" + line.split("||")[-1]
            elif ( act == "getNewReserveSpace" ):
                actionName = line.split("||")[-1]
            elif (act == "[CarNavigation]ans"):
                actionName = line.split("|")[-1]
            elif (act == "applicationWillEnterForeground"):
                actionName = "進入App前景"
            elif (act == "applicationDidEnterBackground"):
                actionName = "退到App背景"
            elif ( act == "[Locker]Locker Popup" ):
                actionName = "[Locker]Locker Pop up\t"
            elif ( act == "Locker Down Pressed" ):
                actionName = "[Locker]Locker Down Pressed"
            elif ("voiceString" in line):
                actionName = "[VoiceString] "+line.split(":")[-1]
            elif ("Locker off done" in line):
                actionName = "[Locker off result]" + line.split("||")[-1]
            elif ("Locker off fail message" in line):
                actionName = "[Locker off result]" + line.split("||")[-1]
            else:
                actionName = line.split("|")[-1]
            start_time = line.split("||")[0]
            start_time = start_time.split(".")[0]

            if ( actionName != "" ):
                actionlist.append(Info.Action(actionName,start_time));
                actionName = ""
                start_time = ""
    return actionlist

# 分析後Log輸出總內容
def getOutputText(user,apiInfo,action):
    userResult = user.getAllInfoText()
    State = ""
    for act in action:
        State = State + act.getAllInfoText()
    #State = State+"///////////////////////////////////\n\n"
        #for t in apiInfo:
        #State = State + t.getAllInfoText()
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


def getLogFrom(analysisLog):
    infoLines = analysisLog.split("\n")
    for line in infoLines:
        if "[LOG_FROM]" in line:
            return "\n"+line.split("||")[-1].replace(" ","")+"\n\n"
    return ""
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
        tmp = []
        for t in action:
            if t.getStartTime() == "":
                tmp += [action.pop(0)]
        action += tmp
        ############################# get result info
        result = getOutputText(user,apiInfoList,action)
        if "!!" in result:
            state = "Warning"

        simpleResult = getLogFrom(analysisLog) +  result + getNetworkSwitchTimeStamp(analysisLog)
        result = simpleResult + "\n\n--------detail--------\n\n" + analysisLog
        pathArray = name.split("/")[:-1]
        pathArray.append("InLot/"+name.split("/")[-1])
        
        name = ('/').join(pathArray)
        name = name +"_"+state+"_"+user.getName()+"_InLot.txt"
        
        if (len(glob.glob(name))==0):
            with io.open(name, "w",encoding='utf8') as text_file:text_file.write("%s" % result)
            if state == "Warning":
        #sender.DebugSendMail("檔名："+name.split("/")[-1],result)
                lineSender.SendLineNotify("[InLot] 檔名："+name.split("/")[-1],simpleResult)

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








