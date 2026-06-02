# 嵌入式技术全景图 — 技术参考手册

本文件供 embedded-learning-coach Skill 参考，覆盖主流嵌入式技术栈。

---

## 一、硬件平台层

### MCU 系列
| 系列 | 代表型号 | 架构 | 常用开发框架 |
|------|---------|------|------------|
| STM32 F/G/H | F103, F407, H743 | ARM Cortex-M | HAL, LL, CMSIS |
| STM32 L | L476, L552 | Cortex-M (低功耗) | HAL |
| ESP32 | ESP32, ESP32-S3 | Xtensa LX6/7 | ESP-IDF, Arduino |
| NRF52 | nRF52840 | Cortex-M4 | Zephyr, SDK |
| GD32 | GD32F103 | Cortex-M3 | GD32 标准库 |
| CH32 | CH32V307 | RISC-V | MRS SDK |
| RP2040 | Raspberry Pi Pico | Cortex-M0+ 双核 | Pico SDK |

### 开发板识别特征
- `.ioc` 文件 → STM32CubeMX 工程 → STM32
- `sdkconfig` / `esp_idf_component.yml` → ESP-IDF → ESP32
- `prj.conf` / `west.yml` → Zephyr RTOS
- `CMakeLists.txt` 含 `pico_sdk_import.cmake` → RP2040

---

## 二、外设驱动层

### GPIO（通用输入输出）
**学习知识点：**
- KP1：推挽/开漏/浮空输入模式原理
- KP2：内部上下拉电阻机制
- KP3：GPIO 寄存器操作（ODR / IDR / BSRR）
- KP4：外部中断（EXTI）配置与中断优先级
- KP5：位带操作（Bit-Band）

### UART / USART
**学习知识点：**
- KP1：异步串行通信原理（起始位/数据位/校验位/停止位）
- KP2：波特率计算（BRR寄存器）
- KP3：轮询发送与接收
- KP4：中断收发与环形缓冲区
- KP5：DMA收发（双缓冲/循环模式）
- KP6：流控（RTS/CTS）

### SPI
**学习知识点：**
- KP1：四线SPI时序（CPOL/CPHA 4种模式）
- KP2：主从模式与NSS管理
- KP3：HAL_SPI_Transmit / Receive / TransmitReceive
- KP4：DMA加速SPI传输
- KP5：SPI与FLASH（W25Q系列）交互

### I2C
**学习知识点：**
- KP1：两线协议（SCL/SDA）、开漏与上拉
- KP2：起始/停止信号、7位/10位地址
- KP3：读写时序（Register Map访问模式）
- KP4：I2C总线仲裁与时钟拉伸
- KP5：常见I2C传感器（MPU6050、SHT31、AHT20）驱动

### ADC
**学习知识点：**
- KP1：逐次逼近型ADC原理
- KP2：分辨率、采样时间、参考电压
- KP3：单次/连续/扫描模式
- KP4：DMA传输ADC数据
- KP5：过采样与滤波（均值/滑动窗口）

### Timer / PWM
**学习知识点：**
- KP1：通用定时器结构（PSC/ARR/CNT）
- KP2：输出比较模式与PWM生成（CCR/TIMx_CCER）
- KP3：输入捕获（频率/脉宽测量）
- KP4：编码器接口模式
- KP5：死区时间与互补PWM（用于电机驱动）

### DMA
**学习知识点：**
- KP1：DMA工作原理（内存→外设/外设→内存/内存→内存）
- KP2：DMA通道/流配置
- KP3：循环模式与半传输中断
- KP4：DMA与Cache一致性问题（H7系列）

---

## 三、通信协议层

### UART协议（物理层扩展）
- RS232 / RS485 电气标准
- Modbus RTU / ASCII 协议栈

### CAN总线
**学习知识点：**
- KP1：差分信号与总线仲裁
- KP2：帧格式（标准帧/扩展帧/远程帧/错误帧）
- KP3：位时间与波特率配置（BS1/BS2/SJW）
- KP4：过滤器（Mask/List模式）
- KP5：CAN FD 与经典CAN区别

### USB
**学习知识点：**
- KP1：USB拓扑与枚举过程
- KP2：USB全速/高速电气特性
- KP3：HID / CDC / MSC 设备类
- KP4：STM32 USB Device Library 使用

### TCP/IP（嵌入式网络）
- LwIP协议栈架构
- DHCP/DNS/HTTP客户端
- MQTT协议（嵌入式IoT）

### 无线协议
- BLE（蓝牙低功耗）：广播/连接/GATT
- Wi-Fi（ESP32）：Station/AP/SmartConfig
- Zigbee / LoRa / NB-IoT

---

## 四、RTOS层

### FreeRTOS
**学习知识点：**
- KP1：任务创建与调度（抢占式/时间片）
- KP2：队列（Queue）—— 任务间通信
- KP3：信号量（Semaphore）/ 互斥量（Mutex）
- KP4：事件组（EventGroup）
- KP5：软件定时器
- KP6：内存管理（heap_1~heap_5）
- KP7：任务通知（Task Notification，轻量级IPC）
- KP8：堆栈溢出检测

### RT-Thread
- 线程与调度
- 消息队列 / 邮箱 / 信号
- 设备驱动框架（device framework）

### 裸机调度
- 超级循环（Super Loop）
- 状态机调度
- 协作式调度器

---

## 五、中间件层

### 文件系统
- FatFS：SD卡 / Flash 文件系统
- LittleFS：NOR Flash 磨损均衡

### 显示驱动
- LVGL：嵌入式GUI框架
- SSD1306 / ILI9341 / ST7789 驱动

### 传感器融合
- 互补滤波
- Kalman滤波
- 四元数姿态解算

### 电机控制
- PWM调速
- PID控制器实现
- FOC（磁场定向控制）基础

---

## 六、构建系统层

### 识别方法
| 文件特征 | 构建系统 |
|---------|---------|
| `CMakeLists.txt` | CMake |
| `Makefile` | Make |
| `*.uvprojx` / `*.uvproj` | Keil MDK |
| `*.eww` / `*.ewp` | IAR EWARM |
| `*.cproject` / `.settings/` | STM32CubeIDE / Eclipse |
| `platformio.ini` | PlatformIO |
| `west.yml` | Zephyr/West |

### 编译工具链
- `arm-none-eabi-gcc`：ARM裸机
- `riscv-none-elf-gcc`：RISC-V裸机
- `xtensa-esp32-elf-gcc`：ESP32

---

## 七、调试工具

| 工具 | 用途 |
|------|------|
| J-Link / ST-Link | SWD/JTAG 下载调试 |
| GDB + OpenOCD | 命令行调试 |
| STM32CubeIDE | 集成调试 |
| Logic Analyzer | SPI/I2C/UART 时序分析 |
| Wireshark + SLCAN | CAN/TCP 抓包 |

---

## 八、学习主题推荐优先级

初学者路径（建议顺序）：
1. GPIO + 外部中断 → 建立基本IO概念
2. UART轮询收发 → 调试基础
3. 定时器 + PWM → 时序控制
4. I2C传感器驱动 → 协议理解
5. UART DMA → 高效收发
6. FreeRTOS基础 → 系统化并发
7. SPI + FLASH → 存储操作
8. CAN总线 → 工业通信
9. TCP/IP (LwIP) → 网络通信
10. FOC电机控制 → 高级应用

中级工程师路径：
1. DMA多通道协同
2. FreeRTOS内存优化与栈溢出排查
3. USB设备类开发
4. LwIP + MQTT IoT应用
5. Bootloader + OTA升级
