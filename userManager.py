#coding=utf-8
class Info:
    def __init__(self, name, system, device, pakingVer,signalSrc,reservation, garage):
        self.name = name
        self.system = system
        self.device = device
        self.pakingVer = pakingVer
        self.signalSrc = signalSrc
        self.reservation = reservation
        self.garage = garage
    def getGarage(self):
        return self.garage
    def getName(self):
        return self.name
    def getAllInfoText(self):
        return ("使用者："+self.name + "\n"+"裝置： "+self.device+"\n"+"系統："+self.system +"\n"+"版本："+self.pakingVer+"\n"+"電信： "+self.signalSrc+"\n預約： "+ self.reservation+"\n車廠： "+self.garage +"\n"+"///////////////////////////////////\n\n")
    def printAllInfo(self):
        print("使用者："+self.name + "\n"+"裝置： "+self.device+"\n"+"系統："+self.system +"\n"+"版本："+self.pakingVer+"\n"+"電信： "+self.signalSrc+"預約： "+ self.reservation+"\n車廠： "+self.garage +"\n"+"///////////////////////////////////\n\n")
