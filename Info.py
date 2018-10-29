#coding=utf-8
import datetime

class Action:
    def __init__(self, actionName, start_time ):
        self.actionName = actionName
        self.start_time = start_time
        self.info = ""
    def getAllInfoText(self):
        if (self.actionName == ""):
            return ""
        self.info = "( " + self.start_time + " )" + "\t" + self.actionName +"\n\n"
        return self.info
    def getStartTime(self):
        return self.start_time
    def getName(self):
        return self.actionName


class API_info:
    def __init__(self, apiName, state ,start_time, end_time, errorMsg, network, count ):
        self.apiName = apiName
        self.state = state
        self.start_time = start_time
        self.end_time = end_time
        self.errorMsg = errorMsg
        self.network = network
        self.info = ""
        self.count = count
    def getAllInfoText(self):
        self.info = "<API:" + self.apiName + ">\n" + "狀態："+self.state +"\n呼叫次數："+str(self.count) + "次"
        
        if ( self.start_time == "" or self.end_time == "" ):
            self.info = self.info+"\n錯誤訊息："+self.errorMsg
        else:
            min = float(self.end_time.split(":")[-2])-float(self.start_time.split(":")[-2])
            try:
                sec = float(self.end_time.split(":")[-1])-float(self.start_time.split(":")[-1])
            except:
                sec = float(self.end_time.split(":")[-1][:-6])-float(self.start_time.split(":")[-1][:-6])
            if min < 0 :
                min = min + 60
            if sec < 0 :
                sec = sec + 60
            sec = sec + min*60

            self.info = self.info+"\n耗費時間："+ str("%.3f" %sec) + "秒" ;
        if ( self.network != "" ):
            self.info = self.info + "\n網路來源：" + self.network
        elif (self.start_time != "") :
            self.info = self.info + "\n網路來源：" + "Paking Wifi"
        return self.info+"\n"+"\n"


