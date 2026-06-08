from scservo_sdk import PortHandler, PacketHandler

# 串口设置
PORT_NAME = "/dev/ttyACM0"  # 你的 leader 电机总线端口
BAUDRATE = 1000000          # Feetech 777 默认 1Mbps

# 创建端口和协议对象
port_handler = PortHandler(PORT_NAME)
packet_handler = PacketHandler(2.0)  # 协议 2.0

# 打开端口
if not port_handler.openPort():
    print(f"无法打开端口 {PORT_NAME}")
    exit()
if not port_handler.setBaudRate(BAUDRATE):
    print(f"无法设置波特率 {BAUDRATE}")
    exit()

# 尝试扫描 ID 1~6
print("扫描 Feetech 电机 ID...")
for motor_id in range(1, 7):
    model_number, result, error = packet_handler.ping(port_handler, motor_id)
    if result != 0:
        print(f"ID {motor_id}: 无响应")
    else:
        print(f"ID {motor_id}: 型号 {model_number}")

# 关闭端口
port_handler.closePort()