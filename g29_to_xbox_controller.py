#  pip install PySDL2
#  pip install pysdl2-dll
#  pip install vgamepad
import sdl2
import sdl2.ext
import vgamepad as vg
import math
import time

# 初始化 SDL2 和手柄
sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
if sdl2.SDL_NumJoysticks() == 0:
    print("没有检测到方向盘，请连接后重试。")
    exit()

# 选择第一个方向盘
joystick = sdl2.SDL_JoystickOpen(0)
if not joystick:
    print("无法打开方向盘。")
    exit()

print(f"已连接方向盘：{sdl2.SDL_JoystickName(joystick).decode()}")

# 初始化虚拟 Xbox 控制器
gamepad = vg.VX360Gamepad()

# 定义映射参数
MAX_DEGREES = 450    # 方向盘单边最大转动角度
SCALE = 32767        # Xbox 手柄摇杆的最大值（-32767 到 32767）

HAT_UP = 1
HAT_RIGHT = 2
HAT_DOWN = 4
HAT_LEFT = 8

# 初始化屏蔽状态
block_wheel_input = False  # 默认不屏蔽方向盘输入


def map_to_circle(degrees):
    # 将角度范围 [-450, 450] 映射到圆周角度 [0, 2π]
    radians = -degrees * math.pi / 180 + math.pi / 2

    # 计算圆周坐标
    x = int(math.cos(radians) * SCALE)
    y = int(math.sin(radians) * SCALE)

    return x, y


try:
    print("开始监听方向盘输入（Ctrl+C 退出）")
    while True:
        # 处理 SDL2 事件
        events = sdl2.ext.get_events()
        for event in events:
            # 处理方向盘输入屏蔽功能
            if event.type == sdl2.SDL_JOYBUTTONDOWN or event.type == sdl2.SDL_JOYBUTTONUP:
                button_index = event.jbutton.button
                pressed = event.type == sdl2.SDL_JOYBUTTONDOWN

                if button_index == 24 and pressed:  # 24号键用于切换屏蔽状态
                    block_wheel_input = not block_wheel_input  # 切换屏蔽状态
                    print(f"方向盘输入 {'已屏蔽' if block_wheel_input else '已恢复'}")

                # 处理 ABXY 按键
                if button_index == 0:  # A 按键
                    if pressed:
                        gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
                    else:
                        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)

                elif button_index == 2:  # B 按键
                    if pressed:
                        gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
                    else:
                        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_B)

                elif button_index == 1:  # X 按键
                    if pressed:
                        gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
                    else:
                        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)

                elif button_index == 3:  # Y 按键
                    if pressed:
                        gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
                    else:
                        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)

                # 映射 降档键为左肩键（LB）
                elif button_index == 5:  # 左肩键
                    if pressed:
                        gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
                    else:
                        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)

                # 映射 升档键为右肩键（RB）
                elif button_index == 4:  # 右肩键
                    if pressed:
                        gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
                    else:
                        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)

            # 获取方向盘的 X 轴输入
            if not block_wheel_input and event.type == sdl2.SDL_JOYAXISMOTION:

                axis_index = event.jaxis.axis
                if axis_index == 0:  # 假设轴 0 是方向盘的主要输入轴
                    axis_value = event.jaxis.value / 32767.0  # 将轴值归一化为 [-1, 1]
                    degrees = axis_value * MAX_DEGREES  # 将输入范围 [-1, 1] 映射到 [-450, 450]

                    # 映射到摇杆圆周运动
                    xbox_x, xbox_y = map_to_circle(degrees)

                    # 更新虚拟 Xbox 手柄的左摇杆
                    gamepad.left_joystick(x_value=xbox_x, y_value=xbox_y)


            # 处理 D-Pad 的 Hat 输入
            elif event.type == sdl2.SDL_JOYHATMOTION:
                hat_value = event.jhat.value

                # 解析 D-Pad 的方向
                if hat_value & HAT_UP:
                    gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
                else:
                    gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)

                if hat_value & HAT_RIGHT:
                    gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
                else:
                    gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)

                if hat_value & HAT_DOWN:
                    gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
                else:
                    gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)

                if hat_value & HAT_LEFT:
                    gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                else:
                    gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                
            
            # 屏蔽方向盘输入时，摇杆固定为 (0, 0)
        if block_wheel_input:
            gamepad.left_joystick(x_value=0, y_value=0)

        # 提交更新到虚拟手柄
        gamepad.update()

        time.sleep(1/2400)

except KeyboardInterrupt:
    print("程序已退出。")

finally:
    sdl2.SDL_JoystickClose(joystick)
    sdl2.SDL_Quit()
