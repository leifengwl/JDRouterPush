import json
import requests
import datetime
import hashlib
import hmac
import base64
import GlobalVariable

# 获取今天是第几天
def distanceDate():
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day
    months = (0,31,59,90,120,151,181,212,243,273,304,334)
    totalDays = months[month-1]
    totalDays += day
    if(year % 400 == 0)or((year % 4 == 0) and (year % 100 != 0)):
        if month > 2:
            totalDays += 1
    return totalDays

# 通过秒数计算时间
def calculatingTime(onlineTime):
    day = 0
    hour = 0
    minute = int(int(onlineTime) / 60)
    second = int(onlineTime) % 60
    if(minute > 60):
        hour = int(minute / 60)
        minute %= 60
    if hour > 24:
        day = int(hour / 24)
        hour %= 24
    return "%s天%s小时%s分钟%s秒"%(day,hour,minute,second)

def getAuthorization(body,accessKey):
    totalDays = distanceDate()
    deviceKey = "Android6.5.5MI 69:%s" % (totalDays)
    deviceKey = hashlib.md5(deviceKey.encode()).hexdigest()
    time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    text = "%spostjson_body%s%s%s%s" % (deviceKey, body, time, accessKey, deviceKey)
    digest = hmac.new(GlobalVariable.hmacKey.encode(), text.encode(), hashlib.sha1).digest()
    decode = base64.b64encode(digest).decode()

    authorization = "smart %s:::%s:::%s" % (accessKey, decode, time)
    return authorization


# 获取所有设备昵称
def getListAllUserDevices():
    url = GlobalVariable.jd_service_url + "listAllUserDevices"
    body = ''
    GlobalVariable.service_headers["Authorization"] = str(getAuthorization(body,GlobalVariable.accessKey))
    res = requests.post(url,params=GlobalVariable.service_pram,headers=GlobalVariable.service_headers,data=body)
    if res.status_code == 200:
        res = res.json()
        resultLists = res["result"][0]["list"]
        for resultList in resultLists:
            device_id = resultList["device_id"]
            feed_id = resultList["feed_id"]
            device_name = resultList["device_name"]
            GlobalVariable.device_list[device_id] = {"device_name":device_name,"feed_id":feed_id}
    else:
        print("Request getListAllUserDevices failed!")

def getControlDevice(mac,i):
    feed_id = GlobalVariable.device_list[mac]["feed_id"]
    url = GlobalVariable.jd_service_url + "controlDevice"
    body = GlobalVariable.service_body%(feed_id,GlobalVariable.cmds[i])
    GlobalVariable.service_headers["Authorization"] = str(getAuthorization(body,GlobalVariable.accessKey))
    res = requests.post(url, params=GlobalVariable.service_pram, headers=GlobalVariable.service_headers, data=body)
    control_device = {}
    if res.status_code == 200 and res.json()["result"] is not None:
        res = res.json()
        result = json.loads(res["result"])
        streams = result["streams"][0]
        current_value = json.loads(streams["current_value"])
        data = current_value["data"]
        if i == 0:
            # 连接的设备列表
    #         print(data)
            pass
        elif i == 1:
            # 上传与下载
            upload = data["upload"]
            download = data["download"]
            bandwidth = data["bandwidth"]
        elif i == 2:
            # 运行信息
            mac = data["mac"]
            rom = data["rom"]
            sn = data["sn"]
            upload = data["upload"]
            download = data["download"]
            romType = data["romType"]
            model = data["model"]
            cpu = data["cpu"]
            onlineTime = data["onlineTime"]
            wanip = data["wanip"]
            mem = data["mem"]
            upload_str = ""
            download_str = ""
            if int(upload) < 10240:
                upload_str = str(round(int(upload)/10)) + "KB/s"
                download_str = str(round(int(download)/10)) + "KB/s"
            else:
                upload_str = str(round(int(upload)/10/1024,2)) + "MB/s"
                download_str = str(round(int(upload)/10/1024,2)) + "MB/s"
            control_device = {"rom":rom,"speed":"↑%s   ↓%s"%(upload_str,download_str),"cpu":cpu + "%","onlineTime":calculatingTime(onlineTime),"wanip":wanip,"model":model}
        elif i == 3:
            # 插件版本
            if isinstance(data,str):
                print("无法获取插件信息!")
                print("信息如下:",data)
                control_device = {"pluginInfo":False}
            else:
                pcdn_list = data["pcdn_list"]
                pcdn_st = pcdn_list[0]
                status = pcdn_st["status"]
                nickname = pcdn_st["nickname"]
                name = pcdn_st["name"]
                cache_size = pcdn_st["cache_size"]
                extstorage_exist = data["extstorage_exist"]
                extstorage_enable = data["extstorage_enable"]
                board = data["board"]
                control_device = {"pluginInfo":True,"status":status,"nickname":nickname,"pcdnname":name,"cache_size":str(round(int(cache_size)/1000000,2)) + "GB"}
        
    else:
        control_device = {"pluginInfo": False}
        print("Request getControlDevice failed!")
        
    index = GlobalVariable.findALocation(mac)
    if index != -1:
        point_info = GlobalVariable.final_result["pointInfos"][index]
        point_info.update(control_device)
    else:
        print("Find mac failure!")




