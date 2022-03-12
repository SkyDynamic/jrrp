# encoding:utf-8
import os
import json
import random
from apscheduler.schedulers.background import *

from mcdreforged.api.all import *

#默认配置，可自定义，配置文件位于MCDReforged/config/jrrp/jrrp_setting.json
class Config(Serializable):
    luck_bad: str = '今天的运气有点差哦，出门注意车辆行人！'
    luck_low: str = '今天的运气一般般~多与朋友聊聊天增进感情哦~'
    luck_fine: str = '今天的运气很好！也许走在马路上能捡到钱哦~' 
    luck_verygood: str = '今天的运气非常好！也许能遇到桃花运？' 
    luck_99: str = '但不等于100'
    luck_best: str = '今天的运气达到了顶峰！也太离谱了吧！'

config: Config
ConfigFilePath = os.path.join('config/jrrp', 'jrrp_setting.json')
Prefix = '!!jrrp'
default_config = {}

helpmessage = '''
§3{0} §5测试今天的运势
§3{0} §4help §5显示此文本
'''.format(Prefix)

#数据储存json，不可删除，不可擅自更改
def config_data(mode, js=None):
    if js is None:
        js = {}
    if mode == 'r':
        if not os.path.exists('config/jrrp/jrrp_data.json'):
            with open('config/jrrp/jrrp_data.json', 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
        with open('config/jrrp/jrrp_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    if mode == 'w':
        with open('config/jrrp/jrrp_data.json', 'w', encoding='utf-8') as f:
            json.dump(js, f, ensure_ascii=False, indent=4)

#定期删除数据储存json
@new_thread
def Restore_json():
    with open('config/jrrp/jrrp_data.json', 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=4)

#随机一个数字
def random1():
    global playerys,ysmessage
    playerys = random.randrange(1, 100, 1)
    ysmessage = '§b你今天的运势是： §6' + str(playerys)

#主代码
@new_thread('main')
def itrtp(server: ServerInterface):
    global user_id,lucks
    cfg = config_data('r')
    user_id = str(server.player)
    if user_id in cfg:
        lucks = cfg[user_id]
        bbb()
        server.reply('§4§l你已经测试过运势了，不要再测试了！')
        server.reply('§b你今天的运势是：§6{}'.format(cfg[user_id]) + '§r————'+ wmessage)
    else:
        random1()
        lucks = playerys
        bbb()
        cfg[server.player] = playerys
        config_data('w', cfg)
        server.reply(ysmessage + '§r————' + wmessage)

#判断随机数并输出相应的话，对应上方配置
def bbb():
    global wmessage
    if lucks == 100:
        wmessage = '§e{}'.format(config.luck_best)
    elif lucks ==99:
        wmessage = '§e{}'.format(config.luck_99)
    elif lucks >=81:
        wmessage = '§e{}'.format(config.luck_verygood)
    elif lucks >=51:
        wmessage = '§e{}'.format(config.luck_fine)
    elif lucks >= 21:
        wmessage = '§e{}'.format(config.luck_low)
    elif lucks >= 1:
        wmessage = '§e{}'.format(config.luck_bad)

@new_thread('cron')
def cron_task():
    scheduler = BlockingScheduler()
    scheduler.add_job(Restore_json, 'cron', hour=4)
    scheduler.start()

def on_load(server: PluginServerInterface, old):
    global config
    config = server.load_config_simple(file_name=ConfigFilePath, in_data_folder=False, target_class=Config)
    server.register_help_message('!!jrrp', '测运势')
    server.register_command(
        Literal(Prefix).runs(itrtp).
            then(
                Literal('help').runs(lambda server: server.reply(helpmessage))
            )
    )
    cron_task()
