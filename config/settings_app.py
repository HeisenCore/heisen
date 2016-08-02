# coding: utf-8
import os
from paramiko.rsakey import RSAKey

# Raspberry config #####################################################
RASPBERRY_FIREFOX_PROFILE_DIRECTORY = '/root/fids/firefox'
RASPBERRY_ADS_PATH = '/root/fids/ads/'
RASPBERRY_SCREENSHOT_PATH = os.path.join(BASE_DIR, 'raspberry', 'screenshot')
RASPBERRY_VIDEO_PLAYLIST = '/root/fids/video_playlist'
RASPBERRY_IMAGE_PLAYLIST = '/root/fids/image_playlist'
RASPBERRY_PLAYER_SCRIPT = '/root/fids/player.py'
RASPBERRY_RESTART_BROWSER_SCRIPT = '/root/fids/restart_browser.sh'
RASPBERRY_STOP_ADVERTISE_COMMAND = '/root/fids/kill_player.sh'
raspberry_EMERGENCY_MODE_IMAGE = '/root/fids/emergency.png'
SSH_KEY_FILE = os.path.join(
    BASE_DIR, 'fids', 'raspberry', 'raspberry_ssh_key'
)
PA_SSH_KEY_FILE = os.path.join(BASE_DIR, 'fids', 'pa', 'id_rsa')
LOCAL_FIREFOX_PROFILE = os.path.join(
    BASE_DIR, 'fids', 'raspberry', 'firefox_profile.tar.bz2'
)
LOCAL_PLAYER_SCRIPT = os.path.join(BASE_DIR, 'fids', 'raspberry', 'player.py')
LOCAL_RESTART_BROWSER_SCRIPT = os.path.join(
    BASE_DIR, 'fids', 'raspberry', 'restart_browser.sh'
)
LOCAL_ADS_PATH = os.path.join(BASE_DIR, 'raspberry', 'ads')
TEMP_UPLOAD_PATH = os.path.join(BASE_DIR, 'raspberry', 'temp_upload')
LOCAL_EMERGENCY_MODE_IMAGE = os.path.join(
    BASE_DIR, 'static', 'img', 'emergency.png'
)
VIDEO_CONVERT_COMMAND = '/usr/bin/ffmpeg -i {} -aspect 16:9 -c:v libx264 -preset fast -crf 22 -c:a copy -an {}'
VIDEO_SCREENSHOT_COMMAND = '/usr/bin/ffmpeg -i {} -ss {} -vframes 1 {}'
FFPROBE_COMMAND = '/usr/bin/ffprobe -v quiet -print_format json -show_format {}'
SYSTEM_COMMANDS_OUTPUT = '>> /tmp/fids 2>&1'
TMP_UPLOAD = '/tmp/'
SSH_KEY = RSAKey(filename=SSH_KEY_FILE, password='qsEcUUG3c00CZmf2')
PA_SSH_KEY = RSAKey(filename=PA_SSH_KEY_FILE)
########################################################################

activity_log = {
    'resource.delete': 'پا کردن منابع',
    'resource.close': 'بستن منابع',
    'resource.update': 'ویرایش منابع',
    'resource.allocate': 'اختصاص منابع',
    'resource.convert_videos': 'تبدیل ویدیو',
    'entry.reset_resource_status': 'پاک کردن ریسورهای یک پرواز',
    'entry.departure_time': 'درج زمان برخواستن',
    'entry.arrival_time': 'درج زمان نشست',
    'entry.edit_status': 'ویرایش وضعیت',
    'entry.edit_general': 'ویرایش اطلاعات عمومی',
    'entry.insert_arrival': 'درج پروازهای ورودی',
    'entry.insert_departure': 'درج پروازهای خروجی',
    'entry.reset_arrival_status': 'پاک کردن وضعیتهای ورودی',
    'entry.reset_departure_status': 'پاک کردن وضعیت های خروجی',
    'entry.delete_by_id': 'پاک کردن یک پرواز',
    'entry.delete_rpl': 'پاک کردن پرواازهای رشته ایی',
    'entry.insert_arrival_rpl': 'درج پروازهای رشته ایی ورودی',
    'entry.insert_departure_rpl': 'درج پروازهای رشته ایی خروجی',
    'entry.update_rpl': 'ویرایش پروازهای رشته ایی',
    'raspberry.change_hostname': 'ویرایش hostname رزپری',
    'raspberry.copy_browser_profile': 'بروزرسانی تنظیمات رزپری',
    'raspberry.delete_raspberry': 'پاک کردن رزپری',
    'raspberry.emergency_mode': 'حالت اصطراری',
    'raspberry.reboot_raspberry': 'راه اندازی مجدد رزپری',
    'raspberry.send_key': 'ارسال کلید به رزپری',
    'raspberry.restart_browser': 'راه اندازی مجدد مرورگر',
    'raspberry.add_raspbery': 'اضافه کردن رزپری',
    'raspberry.stop_advertise': 'متوقف کردن تبلیغات',
    'raspberry.sync_ads': 'ارسال فایل تبلیغات',
    'raspberry.play_advertise': 'پخش تبلیغات',
}
flight_activity_log = [
    'entry.reset_resource_status',
    'entry.departure_time',
    'entry.arrival_time',
    'entry.edit_status',
    'entry.edit_general',
    'entry.reset_arrival_status',
    'entry.reset_departure_status',
    'entry.delete_by_id',

    'resource.delete',
    'resource.close',
    'resource.update',
    'resource.allocate',
]

REDIS_HOST = 'redis_host'
REDIS_PORT = 6379
REDIS_PASSWORD = '5GXFzavCHcK1r3OUuGug'

OPEN_WEATHER_MAP_API_KEY = '484372e569e032d3ead500120f6021b4'
