from datetime import date, datetime, timedelta
import math
from wechatpy import WeChatClient, WeChatClientException
from wechatpy.client.api import WeChatMessage
import requests
import os
import random

today = datetime.utcnow() + timedelta(hours=8)
today = datetime.strptime(str(today.date()), "%Y-%m-%d")

start_date = os.getenv('START_DATE')
birthday = os.getenv('BIRTHDAY')
app_id = os.getenv('APP_ID')
app_secret = os.getenv('APP_SECRET')
user_ids = os.getenv('USER_ID', '').split("\n")
template_id = os.getenv('TEMPLATE_ID')

if app_id is None or app_secret is None:
  print('请设置 APP_ID 和 APP_SECRET')
  exit(422)

if not user_ids:
  print('请设置 USER_ID，若存在多个 ID 用空格分开')
  exit(422)

if template_id is None:
  print('请设置 TEMPLATE_ID')
  exit(422)

# 纪念日正数
def get_memorial_days_count():
  if start_date is None:
    print('没有设置 START_DATE')
    return 0
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

# 生日倒计时
def get_birthday_left():
  if birthday is None:
    print('没有设置 BIRTHDAY')
    return 0
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

# 彩虹屁 接口不稳定，所以失败的话会重新调用，直到成功
def get_words():
  response = requests.get("https://api.shadiao.pro/chp")
  print(response.json()['data'])
  if response.status_code != 200:
    return get_words()
  return response.json()['data']['text']

# 随机颜色
def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)

try:
  client = WeChatClient(app_id, app_secret)
except WeChatClientException as e:
  print('微信获取 token 失败，请检查 APP_ID 和 APP_SECRET，或当日调用量是否已达到微信限制。')
  exit(502)

wm = WeChatMessage(client)
data = {
  "love_days": {
    "value": get_memorial_days_count(),
    "color": get_random_color()
  },
  "birthday_left": {
    "value": get_birthday_left(),
    "color": get_random_color()
  },
  "words": {
    "value": get_words(),
    "color": get_random_color()
  },
}

if __name__ == '__main__':
  count = 0
  try:
    for user_id in user_ids:
      res = wm.send_template(user_id, template_id, data)
      count+=1
  except WeChatClientException as e:
    print('微信端返回错误：%s。错误代码：%d' % (e.errmsg, e.errcode))
    exit(502)

  print("发送了" + str(count) + "条消息")
