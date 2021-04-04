import datetime
import requests
import os

# region 全局参数

# API
jd_base_url = "https://router-app-api.jdcloud.com/v1/regions/cn-north-1/"
# RequestHeader
headers = {
    "x-app-id": "996",
    "Content-Type": "application/json"
}
# Store query results
final_result = {}
# 设备名
device_name = {}
# 记录数
records_num = 7
# 当前版本
version = "20210314"

# 环境变量
WSKEY = os.environ.get("WSKEY", "")  # 京东云无线宝中获取
SERVERPUSHKEY = os.environ.get("SERVERPUSHKEY", "")  # Server酱推送
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")  # Telegram推送服务Token
TG_USER_ID = os.environ.get("TG_USER_ID", "")  # Telegram推送服务UserId
BARK = os.environ.get("BARK", "")  # bark消息推送服务,自行搜索; secrets可填;形如jfjqxDx3xxxxxxxxSaK的字符串
PUSHPLUS = os.environ.get("PUSHPLUS", "")  # PUSHPLUS消息推送Token
DEVICENAME = os.environ.get("DEVICENAME", "")  # 设备名称 mac后6位:设置的名称，多个使用&连接
RECORDSNUM = os.environ.get("RECORDSNUM", "7")  # 需要设置的获取记录条数 不填默认7条

# 获取当天时间和当天积分
def todayPointIncome():
    today_total_point = 0
    today_date = ""
    res = requests.get(jd_base_url + "todayPointIncome", headers=headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        today_total_point = result["todayTotalPoint"]
        todayDate = result["todayDate"]
        today_date = datetime.datetime.strptime(todayDate, "%Y-%m-%d").strftime("%Y年%m月%d日")
    else:
        print("Request todayPointIncome failed!")
    final_result["today_date"] = today_date
    final_result["today_total_point"] = str(today_total_point)
    return today_total_point


# 获取今日总积分
def pinTotalAvailPoint():
    total_avail_point = 0
    res = requests.get(jd_base_url + "pinTotalAvailPoint", headers=headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        total_avail_point = result["totalAvailPoint"]
    else:
        print("Request pinTotalAvailPoint failed!")
    final_result["total_avail_point"] = str(total_avail_point)
    return total_avail_point


# 查找mac位置
def findALocation(mac):
    point_infos = final_result["pointInfos"]
    alocation = -1
    for index, point_info in enumerate(point_infos):
        if mac == point_info["mac"]:
            alocation = index
            break
    return alocation


# 路由账户信息
def routerAccountInfo(mac):
    params = {
        "mac": mac,
    }
    res = requests.get(jd_base_url + "routerAccountInfo", params=params, headers=headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        accountInfo = result["accountInfo"]
        mac = accountInfo["mac"]
        amount = accountInfo["amount"]
        bindAccount = accountInfo["bindAccount"]
        recentExpireAmount = accountInfo["recentExpireAmount"]
        recentExpireTime = accountInfo["recentExpireTime"]
        recentExpireTime_str = datetime.datetime.fromtimestamp(recentExpireTime / 1000).strftime("%Y-%m-%d %H:%M:%S")
        account_info = {"amount": str(amount), "bindAccount": str(bindAccount),
                        "recentExpireAmount": str(recentExpireAmount), "recentExpireTime": recentExpireTime_str}
        index = findALocation(mac)
        if index != -1:
            point_info = final_result["pointInfos"][index]
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
    res = requests.get(jd_base_url + "router:activityInfo", params=params, headers=headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        # finishActivity = result["finishActivity"]
        totalIncomeValue = result["routerUnderwayResult"]["totalIncomeValue"]
        satisfiedTimes = result["routerUnderwayResult"]["satisfiedTimes"]
        activity_info = {"mac": mac, "totalIncomeValue": totalIncomeValue, "satisfiedTimes": satisfiedTimes}
        index = findALocation(mac)
        if index != -1:
            point_info = final_result["pointInfos"][index]
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
    MAC = []
    res = requests.get(jd_base_url + "todayPointDetail", params=params, headers=headers)
    if res.status_code == 200:
        res_json = res.json()
        result = res_json["result"]
        todayDate = result["todayDate"]
        totalRecord = result["pageInfo"]["totalRecord"]
        pointInfos = result["pointInfos"]
        final_result["todayDate"] = todayDate
        final_result["totalRecord"] = str(totalRecord)
        final_result["pointInfos"] = pointInfos
        for info in pointInfos:
            mac = info["mac"]
            MAC.append(mac)
            routerActivityInfo(mac)
            routerAccountInfo(mac)
            pointOperateRecordsShow(mac)
    else:
        print("Request todayPointDetail failed!")


# 点操作记录显示
def pointOperateRecordsShow(mac):
    params = {
        "source": 1,
        "mac": mac,
        "pageSize": records_num,
        "currentPage": 1
    }
    point_records = []
    res = requests.get(jd_base_url + "pointOperateRecords:show", params=params, headers=headers)
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
        index = findALocation(mac)
        if index != -1:
            point_info = final_result["pointInfos"][index]
            point_info.update({"pointRecords": point_records})
    else:
        print("Request pointOperateRecordsShow failed!")


# 解析设备名称
def resolveDeviceName(DEVICENAME):
    if "" == DEVICENAME:
        print("未设置自定义设备名")
    else:
        devicenames = DEVICENAME.split("&")
        for devicename in devicenames:
            mac = devicename.split(":")[0]
            name = devicename.split(":")[1]
            device_name.update({mac: name})


# 检测更新
def checkForUpdates():
    remote_address = "https://raw.githubusercontent.com/leifengwl/JDRouterPush/main/config.ini"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
    }
    res = requests.get(url=remote_address, headers=headers)
    if res.status_code == 200:
        res_json = res.json()
        final_result["announcement"] = res_json["announcement"]
        if res_json["version"] != version:
            final_result["updates_version"] = res_json["version"]
            final_result["update_log"] = res_json["updateLog"]
        else:
            print("欢迎使用JDRouterPush!")
    else:
        print("checkForUpdate failed!")


# region 通知结果

# 结果显示
def resultDisplay():
    today_date = final_result["today_date"]
    today_total_point = final_result["today_total_point"]
    title = today_date + "到账积分:" + today_total_point
    todayDate = final_result["todayDate"]
    total_avail_point = final_result["total_avail_point"]
    totalRecord = final_result["totalRecord"]
    pointInfos = final_result["pointInfos"]
    content = ""
    point_infos = ""
    bindAccount = ""
    # 更新检测
    if final_result.get("updates_version"):
        content = content + "**JDRouterPush更新提醒:**" \
                  + "\n```\n最新版：" + final_result["updates_version"] \
                  + "  当前版本：" + version
        if final_result.get("update_log"):
            content = content + "\n" + final_result["update_log"] + "\n```"
    if final_result.get("announcement"):
        content = content + "\n> " + final_result["announcement"] + " \n\n"
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
        point_infos = point_infos + "\n" + "- " + device_name.get(str(mac[-6:]), "京东云无线宝_" + str(mac[-3:])) + "==>" \
                      + "\n    - 今日积分：" + str(todayPointIncome) \
                      + "\n    - 可用积分：" + str(amount) \
                      + "\n    - 总收益积分：" + str(allPointIncome)
        if satisfiedTimes != "":
            point_infos = point_infos + "\n    - 累计在线：" + \
                          str(satisfiedTimes) + "天"
        point_infos = point_infos + "\n    - 最近到期积分：" + str(recentExpireAmount) \
                      + "\n    - 最近到期时间：" + recentExpireTime \
                      + "\n    - 最近" + str(records_num) + "条记录："
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

    markdownContent = """{content}---
**数据日期:**
```
{date}
```
**今日总收益:**
```
{total_today}
```
**总可用积分:**
```
{avail_today}
```
**绑定账户:**
```
{account}
```
**设备总数:**
```
{devicesCount}
```
**设备信息如下:**
- ***
{detail}
- ***""".format(**notifyContentJson)
    server_push(title, markdownContent.replace("- ***","```"))
    push_plus(title, markdownContent)
    print("标题->", title)
    print("内容->\n", markdownContent)
    normalContent = """{content}---
数据日期:{date}
今日总收益:{total_today}
总可用积分:{avail_today}
绑定账户:{account}
设备总数:{devicesCount}
**设备信息如下:**
{detail}""".format(**notifyContentJson)
    print("标题->", title)
    print("内容->\n", normalContent)
    telegram_bot(title, normalContent)
    bark(title, normalContent)


# Server酱推送
def server_push(text, desp):
    if not SERVERPUSHKEY:
        # print("Server酱推送的SERVERPUSHKEY未设置!!\n取消推送")
        return
    server_push_url = "https://sc.ftqq.com/" + SERVERPUSHKEY + ".send"
    str = SERVERPUSHKEY[0:3]
    if "SCT" == str:
        server_push_url = "https://sctapi.ftqq.com/" + SERVERPUSHKEY + ".send"
    params = {
        "text": text,
        "desp": desp
    }
    res = requests.post(url=server_push_url, data=params)
    if res.status_code == 200:
        print("Server酱推送成功!")
    else:
        print("Server酱推送失败!")


# tg推送
def telegram_bot(title, content):
    print("\n")
    if not TG_BOT_TOKEN or not TG_USER_ID:
        # print("Telegram推送的TG_BOT_TOKEN或者TG_USER_ID未设置!!\n取消推送")
        return
    print("Telegram 推送开始")
    send_data = {"chat_id": TG_USER_ID, "text": title +
                                                '\n\n' + content, "disable_web_page_preview": "true"}
    response = requests.post(
        url='https://api.telegram.org/bot%s/sendMessage' % (TG_BOT_TOKEN), data=send_data)
    print(response.text)


# Bark推送
def bark(title, content):
    print("\n")
    if not BARK:
        # print("bark服务的bark_token未设置!!\n取消推送")
        return
    print("bark服务启动")
    response = requests.get(
        f"""https://api.day.app/{BARK}/{title}/{content}""")
    print(response.text)

# pushplus推送
def push_plus(title, content):
    if not PUSHPLUS:
        # print("pushplus推送的PUSHPLUS未设置!!\n取消推送")
        return
    push_plus_url = "http://www.pushplus.plus/send"
    params = {
        "token": PUSHPLUS,
        "title": title,
        "content": content,
        "template": "markdown"
    }
    res = requests.post(url=push_plus_url, params=params)
    if res.status_code == 200:
        print("pushplus推送成功!")
    else:
        print("pushplus推送失败!")


# endregion

# 主操作
def main():
    global records_num
    if WSKEY is None or WSKEY.strip() == '':
        print("未获取到环境变量'WSKEY'，执行中止")
        return
    headers["wskey"] = WSKEY
    if RECORDSNUM.isdigit():
        records_num = int(RECORDSNUM)
    resolveDeviceName(DEVICENAME)
    checkForUpdates()
    todayPointIncome()
    todayPointDetail()
    pinTotalAvailPoint()
    resultDisplay()

# endregion

# 读取配置文件
if __name__ == '__main__':
    main()
