
import requests,socket,time,os
import logging
import datetime
from threading import Timer

def handleLogFile():
    # 是否有日志文件夹
    path = os.getcwd()
    log_path = path + '\print_log'

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    now_date = time.strftime("%Y%m%d", time.localtime())
    logging.basicConfig(level=logging.INFO, 
                        filename='./print_log/print_%s.log' % (now_date), 
                        filemode='a+', 
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', 
                        encoding="utf-8")

    # 清理7天前的日志文件
    for root,dirs,files in os.walk(log_path):
        for file in files:
            # 使用join函数将文件名称和文件所在根目录连接起来
            file_path = os.path.join(root, file)
            # 文件创建时间
            file_create_time = os.path.getctime(file_path)
            # 当日的7天前
            seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days = 7))
            # 转换为时间戳
            seven_days_ago_timestamp = int(time.mktime(seven_days_ago.timetuple()))
            
            if seven_days_ago_timestamp > file_create_time:
                os.remove(file_path)
                logging.info('removelog ' + file_path)


def GetPrintData():
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 请求该接口
    try:
        response = requests.get('printer_data_url')

        print(now_time, response.status_code)
        logging.info(now_time + ' ' + str(response.status_code))

        # 获取响应数据，并解析JSON，转化为python字典
        if response.status_code == 200:
            result = response.json()
            if result['data']['total'] > 0:
                # 创建一个 TCP/IP socket 对象
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # 前一次运行使套接字处于 TIME_WAIT 状态，无法立即重用
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                # 本机IP 
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 80))
                local_ip = s.getsockname()[0]

                last_ip = ''
                for item in result['data']['list']:
                    printer_ip = item['printer_ip']
                    print_data = item['print_data']

                    print(now_time + ' : ' + printer_ip + ' ; ' + local_ip)
                    print(print_data)

                    logging.info(now_time + ' : ' + printer_ip + ' ; ' + local_ip)
                    logging.info(print_data)

                    printer_status = True
                    if last_ip != printer_ip:
                        last_ip = printer_ip
                        # 连接服务器
                        server_address = (printer_ip, 9100)
                        try:
                            sock.settimeout(10)
                            sock.connect(server_address)
                        except Exception as e:
                            printer_status = False
                            print(e)
                    
                    if printer_status == True:
                        # 发送打印指令
                        # message = print_data.encode()
                        message = print_data.encode("GBK")
                        sock.sendall(message)
                    
                # 关闭 socket 连接
                sock.close()
        else:
            response.close()

    except BaseException as e:
        logging.warning(e)
        print('请求数据失败', e)

class LoopTimer(Timer):
    """Call a function after a specified number of seconds:
               t = LoopTimer(30.0, f, args=[], kwargs={})
               t.start()
               t.cancel()     # stop the timer's action if it's still waiting
       """
    def __init__(self,interval,function,args=[],kwargs={}):
        Timer.__init__(self,interval,function,args,kwargs)

    def run(self):
        '''self.finished.wait(self.interval)
                if not self.finished.is_set():
                    self.function(*self.args, **self.kwargs)
                self.finished.set()'''
        
        while True:
            self.finished.wait(self.interval)
            if self.finished.is_set():
                self.finished.set()
                break
            self.function(*self.args,**self.kwargs)


handleLogFile()
t = LoopTimer(2, GetPrintData)
t.start()