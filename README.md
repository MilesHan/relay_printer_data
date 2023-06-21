# relay_printer_data
打印机数据转发程序，用于Windows上请求API获取数据并发送至打印机，打印标签。

主要实现以下几个功能：

- 请求数据接口
- 向标签机 `IP:PORT` 发送打印指令
- 定时重复请求
- 记录日志，清理7天前的日志文件
- 使用 `pyinstaller -F .\printer.py` 打包成exe程序