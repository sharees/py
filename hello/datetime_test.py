from datetime import datetime,timedelta,timezone
import pytz

#2015-05-18 16:28:07.198690
now = datetime.now()

#2023-01-19 13:43:00
dt = datetime(2023,1,19,13,43)

#1674106980.0 轉換成時間戳
ts = dt.timestamp()

#2023-01-19 13:43:00 轉換成當地時間
dt = datetime.fromtimestamp(ts)

#轉換成UTC時間 2023-01-19 05:43:00
utc = datetime.utcfromtimestamp(ts)

strtime = '2023-01-19 05:43:00';

#字符串轉換為日期 2023-01-19 05:43:00
cday = datetime.strptime(strtime,'%Y-%m-%d %H:%M:%S')

#日期轉字符串 Fri,Jan 19 14:01
strdy = now.strftime('%a,%b %d %H:%M')

#日期/時間加減 2024-01-20 14:05:40.253037
tomorrow = now + timedelta(days=1)

#時間相加 2024-01-19 17:06:28.972940
nextHour = now + timedelta(hours=3)

#本地時間轉換為UTC時間
tz_utc_8 = timezone(timedelta(hours=8))
now = datetime.now()
#强制设置为UTC+8:00 2024-01-19 14:09:10.560328+08:00
dt = now.replace(tzinfo=tz_utc_8)

#轉換成UTC時間
utf_time = now.astimezone(timezone.utc)

#2024-01-19 14:09:10.560328+08:00轉換為時間戳
fmt = '%Y-%m-%d %H:%M:%S.%f%z'
strtime = '2024-01-19 14:09:10.560328+08:00'
ndt = datetime.strptime(strtime,fmt)
dt = ndt.astimezone(pytz.utc)
timestamp = dt.timestamp()
print(dt,timestamp)

