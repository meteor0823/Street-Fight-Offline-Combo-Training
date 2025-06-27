import keyboard
import time
import threading
from collections import defaultdict


class ComboTrainer:
    def __init__(self):
        self.combo_sequence = []  # 存储连招序列
        self.current_step = 0  # 当前训练步骤
        self.start_time = 0  # 连招开始时间
        self.active = False  # 训练状态
        self.combo_thread = None  # 训练线程
        self.last_key_time = defaultdict(float)  # 按键最后触发时间
        self.key_events = []  # 记录按键事件

    def add_combo_step(self, keys, max_delay, simultaneous=False):
        """添加连招步骤
        :param keys: 按键列表 (e.g. ['a'] 或 ['ctrl', 'c'])
        :param max_delay: 允许的最大延迟（秒）
        :param simultaneous: 是否需要同时按下
        """
        self.combo_sequence.append({
            'keys': set(keys),
            'max_delay': max_delay,
            'simultaneous': simultaneous
        })

    def key_event_handler(self, event):
        """键盘事件监听回调"""
        if event.event_type == keyboard.KEY_DOWN and self.active:
            current_time = time.time()
            self.key_events.append((event.name, current_time))
            self.last_key_time[event.name] = current_time

    def check_simultaneous_press(self, required_keys, max_delay):
        """检查组合键是否同时按下"""
        key_times = []
        for key in required_keys:
            if key in self.last_key_time:
                key_times.append(self.last_key_time[key])
            else:
                return False

        # 检查所有按键是否在指定时间差内按下
        return max(key_times) - min(key_times) <= max_delay

    def run_combo_training(self):
        """执行连招训练"""
        print("===== 连招训练开始! =====")
        self.current_step = 0
        self.start_time = time.time()
        self.key_events.clear()
        self.last_key_time.clear()

        while self.active and self.current_step < len(self.combo_sequence):
            step = self.combo_sequence[self.current_step]
            required_keys = step['keys']
            step_start = time.time()
            deadline = step_start + step['max_delay']

            # 等待按键或超时
            while time.time() < deadline and self.active:
                pressed_keys = {k for k in required_keys if self.last_key_time.get(k, 0) >= step_start}

                # 检查组合键要求
                if step['simultaneous']:
                    if pressed_keys == required_keys:
                        if self.check_simultaneous_press(required_keys, 0.1):  # 0.1秒内视为同时
                            break
                # 检查独立按键
                elif pressed_keys:
                    break

            # 检查步骤结果
            current_time = time.time()
            if current_time < deadline:
                print(f"步骤 {self.current_step + 1}: 成功! ({current_time - step_start:.2f}s)")
                self.current_step += 1
            else:
                print(f"步骤 {self.current_step + 1}: 失败! 超时或按键错误")
                print(f"预期按键: {', '.join(step['keys'])}")
                self.show_key_events()
                self.reset_step(step_start)

    def reset_step(self, step_start):
        """重置当前步骤"""
        # 清除步骤开始后的按键记录
        self.key_events = [e for e in self.key_events if e[1] < step_start]
        for key in list(self.last_key_time.keys()):
            if self.last_key_time[key] >= step_start:
                del self.last_key_time[key]

    def show_key_events(self):
        """显示输入的按键序列"""
        if not self.key_events:
            print("未检测到按键输入")
            return

        print("你的输入: ", end="")
        for i, (key, t) in enumerate(self.key_events):
            if i > 0:
                delay = t - self.key_events[i - 1][1]
                print(f" -> {key}(+{delay:.3f}s)", end="")
            else:
                print(key, end="")
        print()

    def start_training(self):
        """开始训练"""
        if not self.combo_sequence:
            print("错误: 未添加连招序列!")
            return

        self.active = True
        keyboard.hook(self.key_event_handler)
        self.combo_thread = threading.Thread(target=self.run_combo_training)
        self.combo_thread.start()
        print("训练进行中... 按ESC结束训练")

    def stop_training(self):
        """结束训练"""
        self.active = False
        if self.combo_thread and self.combo_thread.is_alive():
            self.combo_thread.join()
        keyboard.unhook_all()
        print("===== 训练结束! =====")


# ===== 使用示例 =====
if __name__ == "__main__":
    trainer = ComboTrainer()

    # 定义连招序列 (可根据需要修改)
    # trainer.add_combo_step(['j'], 0.5)  # 单键: 0.5秒内按J
    # trainer.add_combo_step(['k'], 0.5)  # 单键: 0.5秒内按K
    # trainer.add_combo_step(['u'], 0io.5)  # 单键: 0.5秒内按U
    trainer.add_combo_step(['i', 'o'], 0.5, True)  # 组合键: 0.3秒内同时按I+O
    # trainer.add_combo_step(['l'], 1.0)  # 单键: 1秒内按L

    # 开始训练
    trainer.start_training()

    # 设置退出键
    keyboard.wait('esc')
    trainer.stop_training()

