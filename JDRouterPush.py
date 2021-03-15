import datetime
import requests
import os

# API
jd_base_url = "https://router-app-api.jdcloud.com/v1/regions/cn-north-1/"

def todayPointIncome(headers):
    today_total_point = 0
    today_date = ""
    res = requests.get(jd_base_url + "todayPointIncome", headers=headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        todayTotalPoint = result["todayTotalPoint"]
        todayDate = result["todayDate"]
        today_date = datetime.datetime.strptime(todayDate, "%Y-%m-%d").strftime("%Y年%m月%d日")
        today_total_point = todayTotalPoint
    else:
        print("Request todayPointIncome failed!")
    return today_date + "到账积分" + str(today_total_point)

def pinTotalAvailPoint(headers):
    total_avail_point = 0
    res = requests.get(jd_base_url + "pinTotalAvailPoint", headers=headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        totalAvailPoint = result["totalAvailPoint"]
        total_avail_point = totalAvailPoint
    else:
        print("Request pinTotalAvailPoint failed!")
    return total_avail_point

def routerAccountInfo(headers,mac):
    params = {
        "mac" : mac,
    }
    res = requests.get(jd_base_url + "routerAccountInfo", params=params, headers=headers)
    content = ""
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        accountInfo = result["accountInfo"]
        amount = accountInfo["amount"]
        content = " 可用积分:" + str(amount) + routerActivityInfo(headers,mac)
    else:
        print("获取routerAccountInfo失败")
    return content

def routerActivityInfo(headers,mac):
    params = {
        "mac": mac,
    }
    content = ""
    res = requests.get(jd_base_url + "router:activityInfo", params=params, headers=headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        satisfiedTimes = result["routerUnderwayResult"]["satisfiedTimes"]
        content = "    累计在线:" + str(satisfiedTimes)+"天"
    else:
        print("获取routerActivityInfo失败")
    return content

def todayPointDetail(headers):
    params = {
        "sortField": "today_point",
        "sortDirection": "DESC",
        "pageSize": "30",
        "currentPage": "1",
    }
    content = ""
    MAC = []
    res = requests.get(jd_base_url + "todayPointDetail", params=params, headers=headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        todayDate = result["todayDate"]
        totalRecord = result["pageInfo"]["totalRecord"]
        pointInfos = result["pointInfos"]
        content = content + "* 数据日期: " + todayDate + "\n* 总可用积分: " + str(pinTotalAvailPoint(headers)) + "\n* 设备总数: " + str(totalRecord) + "\n* 设备收益如下:"
        for info in pointInfos:
            mac = info["mac"]
            MAC.append(mac)
            todayPointIncome = info["todayPointIncome"]
            allPointIncome = info["allPointIncome"]
            content = content + "\n  * 京东云无线宝_" + str(mac[-4:]) + " ==>\n今日收益: " + str(todayPointIncome) + " 总积分: " + str(allPointIncome) \
                      + routerAccountInfo(headers, mac) \
                      + pointOperateRecordsShow(headers,mac)
    else:
        print("Request todayPointDetail failed!")
    return content

def pointOperateRecordsShow(headers,mac):
    params = {
        "source": 1,
        "mac": mac,
        "pageSize": 7,
        "currentPage": 1
    }
    content = ""
    res = requests.get(jd_base_url + "pointOperateRecords:show", params=params, headers=headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        pointRecords = result["pointRecords"]
        content = "\n* 最近7条记录:"
        for pointRecord in pointRecords:
            recordType_str = " "
            recordType = pointRecord["recordType"]
            pointAmount = pointRecord["pointAmount"]
            createTime = pointRecord["createTime"]
            createTime_str = datetime.datetime.fromtimestamp(createTime / 1000)
            if recordType == 1:
                recordType_str = "积分收入:"
            else:
                recordType_str = "积分支出:"
            content = content + "\n *  " + str(createTime_str) + "\t" + recordType_str + " " + str(pointAmount)
    else:
        print("获取pointOperateRecordsShow失败")
    return content

# 推送通知
def sendNotification(SERVERPUSHKEY,text,desp):
    # server推送
    server_push_url = "https://sctapi.ftqq.com/" + SERVERPUSHKEY + ".send"
    params = {
        "title" : text,
        "desp" : desp
    }
    res = requests.get(url=server_push_url, params=params)
    if res.status_code == 200:
        print("推送成功!")
    else:
        print("推送失败!")
    print("标题->",text)
    print("内容->\n",desp)


# 主操作
def main(WSKEY,SERVERPUSHKEY):
    headers = {
        "wskey": WSKEY,
        "x-app-id": "996",
        "Content-Type": "application/json"
    }
    today_total_point = todayPointIncome(headers)
    today_point_detail = todayPointDetail(headers)
    sendNotification(SERVERPUSHKEY, today_total_point, today_point_detail)

# 读取配置文件
if __name__ == '__main__':
    WSKEY = os.environ["WSKEY"]
    SERVERPUSHKEY = os.environ["SERVERPUSHKEY"]
    main(WSKEY,SERVERPUSHKEY)
