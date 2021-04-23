import datetime
import requests
import GlobalVariable
import JDServiceAPI
import NoticePush
import NoticeTemplate
from urllib.parse import quote




# 获取当天时间和当天积分
def todayPointIncome():
    today_total_point = 0
    today_date = ""
    res = requests.get(GlobalVariable.jd_base_url + "todayPointIncome", headers=GlobalVariable.headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        today_total_point = result["todayTotalPoint"]
        todayDate = result["todayDate"]
        today_date = datetime.datetime.strptime(todayDate, "%Y-%m-%d").strftime("%Y年%m月%d日")
    else:
        print("Request todayPointIncome failed!")
    GlobalVariable.final_result["today_date"] = today_date
    GlobalVariable.final_result["today_total_point"] = str(today_total_point)
    return today_total_point


# 获取今日总积分
def pinTotalAvailPoint():
    total_avail_point = 0
    res = requests.get(GlobalVariable.jd_base_url + "pinTotalAvailPoint", headers=GlobalVariable.headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        total_avail_point = result["totalAvailPoint"]
    else:
        print("Request pinTotalAvailPoint failed!")
    GlobalVariable.final_result["total_avail_point"] = str(total_avail_point)
    return total_avail_point



# 路由账户信息
def routerAccountInfo(mac):
    params = {
        "mac": mac,
    }
    res = requests.get(GlobalVariable.jd_base_url + "routerAccountInfo", params=params, headers=GlobalVariable.headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        accountInfo = result["accountInfo"]
        mac = accountInfo["mac"]
        amount = accountInfo["amount"]
        bindAccount = accountInfo["bindAccount"]
        GlobalVariable.service_headers["pin"] = quote(bindAccount)
        recentExpireAmount = accountInfo["recentExpireAmount"]
        recentExpireTime = accountInfo["recentExpireTime"]
        recentExpireTime_str = datetime.datetime.fromtimestamp(recentExpireTime / 1000).strftime("%Y-%m-%d %H:%M:%S")
        account_info = {"amount": str(amount), "bindAccount": str(bindAccount),
                        "recentExpireAmount": str(recentExpireAmount), "recentExpireTime": recentExpireTime_str}
        index = GlobalVariable.findALocation(mac)
        if index != -1:
            point_info = GlobalVariable.final_result["pointInfos"][index]
            point_info.update(account_info)
        else:
            print("Find mac failure!")
    else:
        print("Request routerAccountInfo failed!")


# 路由活动信息
def routerActivityInfo(mac):
    params = {
        "mac": mac,
    }
    res = requests.get(GlobalVariable.jd_base_url + "router:activityInfo", params=params, headers=GlobalVariable.headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        # finishActivity = result["finishActivity"]
        totalIncomeValue = result["routerUnderwayResult"]["totalIncomeValue"]
        satisfiedTimes = result["routerUnderwayResult"]["satisfiedTimes"]
        activity_info = {"mac": mac, "totalIncomeValue": totalIncomeValue, "satisfiedTimes": satisfiedTimes}
        index = GlobalVariable.findALocation(mac)
        if index != -1:
            point_info = GlobalVariable.final_result["pointInfos"][index]
            point_info.update(activity_info)
    else:
        print("Request routerActivityInfo failed!")


# 收益信息
def todayPointDetail():
    params = {
        "sortField": "today_point",
        "sortDirection": "DESC",
        "pageSize": "30",
        "currentPage": "1"
    }
    MACS = []
    res = requests.get(GlobalVariable.jd_base_url + "todayPointDetail", params=params, headers=GlobalVariable.headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        todayDate = result["todayDate"]
        totalRecord = result["pageInfo"]["totalRecord"]
        pointInfos = result["pointInfos"]
        GlobalVariable.final_result["todayDate"] = todayDate
        GlobalVariable.final_result["totalRecord"] = str(totalRecord)
        GlobalVariable.final_result["pointInfos"] = pointInfos
        for info in pointInfos:
            mac = info["mac"]
            MACS.append(mac)
            routerActivityInfo(mac)
            routerAccountInfo(mac)
            pointOperateRecordsShow(mac)

        JDServiceAPI.getListAllUserDevices()
        
        for mac in MACS:
            JDServiceAPI.getControlDevice(mac,2)
            JDServiceAPI.getControlDevice(mac,3)
    else:
        print("Request todayPointDetail failed!")


# 点操作记录显示
def pointOperateRecordsShow(mac):
    params = {
        "source": 1,
        "mac": mac,
        "pageSize": GlobalVariable.records_num,
        "currentPage": 1
    }
    point_records = []
    res = requests.get(GlobalVariable.jd_base_url + "pointOperateRecords:show", params=params, headers=GlobalVariable.headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        pointRecords = result["pointRecords"]
        for pointRecord in pointRecords:
            recordType = pointRecord["recordType"]
            pointAmount = pointRecord["pointAmount"]
            createTime = pointRecord["createTime"]
            createTime_str = datetime.datetime.fromtimestamp(createTime / 1000).strftime("%Y-%m-%d")
            point_record = {"recordType": recordType, "pointAmount": pointAmount, "createTime": createTime_str}
            point_records.append(point_record)
        index = GlobalVariable.findALocation(mac)
        if index != -1:
            point_info = GlobalVariable.final_result["pointInfos"][index]
            point_info.update({"pointRecords": point_records})
    else:
        print("Request pointOperateRecordsShow failed!")


# 解析设备名称
def resolveDeviceName(DEVICENAME):
    if "" == DEVICENAME:
        # print("未设置自定义设备名")
        pass
    else:
        devicenames = DEVICENAME.split("&")
        for devicename in devicenames:
            mac = devicename.split(":")[0]
            name = devicename.split(":")[1]
            GlobalVariable.device_name.update({mac: name})


# 检测更新
def checkForUpdates():
    remote_address = "https://raw.githubusercontent.com/leifengwl/JDRouterPush/main/config.ini"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
    }
    res = requests.get(url=remote_address, headers=GlobalVariable.headers)
    if res.status_code == 200:
        res_json = res.json()
        GlobalVariable.final_result["announcement"] = res_json["announcement"]
        if res_json["version"] != GlobalVariable.version:
            GlobalVariable.final_result["updates_version"] = res_json["version"]
            GlobalVariable.final_result["update_log"] = res_json["updateLog"]
        else:
            print("欢迎使用JDRouterPush!")
    else:
        print("checkForUpdate failed!")
# region 通知结果

# 结果显示
def resultDisplay():
    today_date = GlobalVariable.final_result["today_date"]
    today_total_point = GlobalVariable.final_result["today_total_point"]
    title = today_date + "到账积分:" + today_total_point
    todayDate = GlobalVariable.final_result["todayDate"]
    total_avail_point = GlobalVariable.final_result["total_avail_point"]
    totalRecord = GlobalVariable.final_result["totalRecord"]
    pointInfos = GlobalVariable.final_result["pointInfos"]
    content = ""
    point_infos = ""
    bindAccount = ""
    # 更新检测
    if GlobalVariable.final_result.get("updates_version"):
        content = content + "**JDRouterPush更新提醒:**" \
                  + "\n```\n最新版：" + GlobalVariable.final_result["updates_version"] \
                  + "  当前版本：" + GlobalVariable.version
        if GlobalVariable.final_result.get("update_log"):
            content = content + "\n" + GlobalVariable.final_result["update_log"] + "\n```"
    if GlobalVariable.final_result.get("announcement"):
        content = content + "\n> " + GlobalVariable.final_result["announcement"] + " \n\n"
    for pointInfo in pointInfos:
        mac = pointInfo["mac"]
        todayPointIncome = pointInfo["todayPointIncome"]
        allPointIncome = pointInfo["allPointIncome"]
        amount = pointInfo["amount"]
        bindAccount = pointInfo["bindAccount"]
        recentExpireAmount = pointInfo["recentExpireAmount"]
        recentExpireTime = pointInfo["recentExpireTime"]
        satisfiedTimes = ""
        if pointInfo.get("satisfiedTimes"):
            satisfiedTimes = pointInfo["satisfiedTimes"]
        pointRecords = pointInfo["pointRecords"]
        point_infos +=  "\n" + "- " + GlobalVariable.device_name.get(str(mac[-6:]), GlobalVariable.device_list[mac]["device_name"]) + "==>" \
                      + "\n    - 今日积分：" + str(todayPointIncome) \
                      + "\n    - 可用积分：" + str(amount) \
                      + "\n    - 总收积分：" + str(allPointIncome)
        if satisfiedTimes != "":
            point_infos += "\n    - 累计在线：" + str(satisfiedTimes) + "天"
        point_infos +=  "\n    - 当前网速：" + pointInfo["speed"] \
                      + "\n    - 当前IP：" + pointInfo["wanip"] \
                      + "\n    - 当前模式：" + pointInfo["model"] \
                      + "\n    - 固件版本：" + pointInfo["rom"]
        if pointInfo.get("pluginInfo"):
            point_infos +=  "\n    - 插件状态：" + pointInfo["status"] \
                          + "\n    - 插件版本：" + pointInfo["nickname"] \
                          + "\n    - 缓存大小：" + pointInfo["cache_size"] \
                          + "\n    - PCDN：" + pointInfo["pcdnname"] 
        point_infos +=  "\n    - 在线时间：" + pointInfo["onlineTime"] \
                      + "\n    - 最近到期积分：" + str(recentExpireAmount) \
                      + "\n    - 最近到期时间：" + recentExpireTime \
                      + "\n    - 最近" + str(GlobalVariable.records_num) + "条记录："
        for pointRecord in pointRecords:
            recordType = pointRecord["recordType"]
            recordType_str = ""
            if recordType == 1:
                recordType_str = "积分收入："
            else:
                recordType_str = "积分支出："
            pointAmount = pointRecord["pointAmount"]
            createTime = pointRecord["createTime"]
            point_infos = point_infos + "\n        - " + \
                          createTime + "  " + recordType_str + str(pointAmount)
    notifyContentJson = {"content": content, "date": todayDate, "total_today": today_total_point,
                         "avail_today": total_avail_point, "account": bindAccount, "devicesCount": totalRecord,
                         "detail": point_infos}

    # mk模板
    markdownContent = NoticeTemplate.markdownTemplate().format(**notifyContentJson)
    NoticePush.server_push(title, markdownContent.replace("- ***", "```"))
    NoticePush.push_plus(title, markdownContent)
    # print("标题->", title)
    # print("内容->\n", markdownContent)

    # 普通模板
    normalContent = NoticeTemplate.normalTemplate().format(**notifyContentJson)
    NoticePush.telegram_bot(title, normalContent)
    NoticePush.bark(title, normalContent)
    NoticePush.enterprise_wechat(title, normalContent)

    # 信息输出测试
    print("标题->", title)
    print("内容->\n", normalContent)
# endregion

# 主操作
def main():
    if GlobalVariable.WSKEY is None or GlobalVariable.WSKEY.strip() == '':
        print("未获取到环境变量'WSKEY'，执行中止")
        return
    GlobalVariable.headers["wskey"] = GlobalVariable.WSKEY
    GlobalVariable.service_headers["tgt"] = GlobalVariable.WSKEY
    if GlobalVariable.RECORDSNUM.isdigit():
        GlobalVariable.records_num = int(GlobalVariable.RECORDSNUM)
    resolveDeviceName(GlobalVariable.DEVICENAME)
    checkForUpdates()
    todayPointIncome()
    todayPointDetail()
    pinTotalAvailPoint()
    resultDisplay()
# endregion

# 读取配置文件
if __name__ == '__main__':
    main()
