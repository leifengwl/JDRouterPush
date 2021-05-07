import os


# 全局参数
# API
jd_base_url = "https://router-app-api.jdcloud.com/v1/regions/cn-north-1/"
jd_service_url = "https://gw.smart.jd.com/f/service/"

# RequestHeader
headers = {
    "x-app-id": "996",
    "Content-Type": "application/json"
}

accessKey = "b8f9c108c190a39760e1b4e373208af5cd75feb4"

service_headers = {
    "tgt": "JDRouterPush",
    "Authorization": "JDRouterPush",
    "accesskey": accessKey,
    "pin": "JDRouterPush",
    "appkey": "996",
    "User-Agent": "Android",
    "Host": "gw.smart.jd.com"
}

cmds = [
    "get_device_list",    # 获取设备列表 在线与离线的客户端状态
    "get_router_status_info",    # 获取路由器状态信息 上传与下载
    "get_router_status_detail",    # 获取路由器版本 mac  sn  上传  下载  cpu  路由在线时间(秒)  wanip  内存
    "jdcplugin_opt.get_pcdn_status",    # 获取路由器插件版本   缓存大小
]

# 请求参数
service_pram = {
    "hard_platform":'MI 6',
    "app_version":"6.5.5",
    "plat_version":9,
    "channel":"jdCloud",
    "plat":"Android"
}

hmacKey = "706390cef611241d57573ca601eb3c061e174948"

# 请求体
service_body = '{"feed_id":"%s","command":[{"current_value":{"cmd":"%s"},"stream_id":"SetParams"}]}'

# 查询后的总结果
final_result = {}
# 设备名
device_name = {}
# 设备MAC 昵称 feed_id
device_list = {}
# 记录数
records_num = 7
# 当前版本
version = "20210506"

# 环境变量
WSKEY = os.environ.get("WSKEY", "")  # 京东云无线宝中获取
SERVERPUSHKEY = os.environ.get("SERVERPUSHKEY", "")  # Server酱推送
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")  # Telegram推送服务Token
TG_USER_ID = os.environ.get("TG_USER_ID", "")  # Telegram推送服务UserId
BARK = os.environ.get("BARK", "")  # bark消息推送服务,自行搜索; secrets可填;形如jfjqxDx3xxxxxxxxSaK的字符串
PUSHPLUS = os.environ.get("PUSHPLUS", "")  # PUSHPLUS消息推送Token
DEVICENAME = os.environ.get("DEVICENAME", "")  # 设备名称 mac后6位:设置的名称，多个使用&连接
RECORDSNUM = os.environ.get("RECORDSNUM", "7")  # 需要设置的获取记录条数 不填默认7条
ACCESSTOKEN = os.environ.get("ACCESSTOKEN", "")  # 企业微信access_token     获取地址:https://work.weixin.qq.com/api/doc/90000/90135/91039
CORPID = os.environ.get("CORPID", "")  # 企业ID  （如果已经填写ACCESSTOKEN  则无需填写这个）
CORPSECRET = os.environ.get("CORPSECRET", "")  # 应用的凭证密钥  （如果已经填写ACCESSTOKEN  则无需填写这个）
TOUSER = os.environ.get("TOUSER", "@all")  # touser指定接收消息的成员  默认为全部
AGENTID = os.environ.get("AGENTID", "")  # agentid企业应用的id
THUMB_MEDIA_ID = os.environ.get("THUMB_MEDIA_ID", "") #企业微信素材库图片id
AUTHOR = os.environ.get("AUTHOR", "") #企业微信文章作者

# 查找mac位置
def findALocation(mac):
    point_infos = final_result["pointInfos"]
    alocation = -1
    for index, point_info in enumerate(point_infos):
        if mac == point_info["mac"]:
            alocation = index
            break
    return alocation
