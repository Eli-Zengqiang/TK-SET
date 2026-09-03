#!/usr/bin/env python3
"""
Linux触屏准确性测试工具
功能：在屏幕上随机生成圆圈，用户点击后记录测试结果，测试轮数可配置
"""

import pygame
import sys
import random
import time
from datetime import datetime

# 初始化pygame
pygame.init()

# 获取屏幕分辨率并设置全屏
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("触屏准确性测试")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
GRAY = (200, 200, 200)

# 测试配置参数
TARGET_RADIUS = 40  # 目标圆圈的半径
MIN_DISTANCE = 100  # 圆圈之间的最小距离

# 创建字体
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 28)


class Button:
    """按钮类"""

    def __init__(self, x, y, width, height, text, color=(100, 100, 255), hover_color=(150, 150, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        button_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, button_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)

        text_surface = font_medium.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False


class TouchTest:
    """触屏测试类"""

    def __init__(self, total_rounds=5, targets_per_round=10):
        self.total_rounds = total_rounds
        self.targets_per_round = targets_per_round
        self.current_round = 0
        self.current_target = 0
        self.targets = []
        self.results = []
        self.start_time = 0
        self.round_start_time = 0
        self.testing = False
        self.finished = False

        # 创建控制按钮
        button_width, button_height = 150, 50
        self.start_button = Button(
            SCREEN_WIDTH // 2 - button_width - 20,
            SCREEN_HEIGHT - 100,
            button_width, button_height,
            "开始测试", GREEN, (100, 255, 100)
        )
        self.exit_button = Button(
            SCREEN_WIDTH // 2 + 20,
            SCREEN_HEIGHT - 100,
            button_width, button_height,
            "退出程序", RED, (255, 100, 100)
        )
        self.next_round_button = Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            SCREEN_HEIGHT - 100,
            button_width, button_height,
            "下一轮", BLUE, (100, 150, 255)
        )

    def generate_targets(self):
        """生成随机目标圆圈"""
        self.targets = []
        attempts = 0
        max_attempts = 1000

        while len(self.targets) < self.targets_per_round and attempts < max_attempts:
            attempts += 1
            radius = TARGET_RADIUS
            x = random.randint(radius, SCREEN_WIDTH - radius)
            y = random.randint(radius + 100, SCREEN_HEIGHT - radius - 100)  # 避开顶部和底部区域

            # 检查新圆圈是否与现有圆圈重叠
            valid_position = True
            for target in self.targets:
                dx = target[0] - x
                dy = target[1] - y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance < MIN_DISTANCE:
                    valid_position = False
                    break

            if valid_position:
                self.targets.append((x, y))

    def check_hit(self, pos):
        """检查点击是否命中目标"""
        if not self.targets:
            return False, -1

        x, y = pos
        for i, (target_x, target_y) in enumerate(self.targets):
            distance = ((target_x - x) ** 2 + (target_y - y) ** 2) ** 0.5
            if distance <= TARGET_RADIUS:
                return True, i
        return False, -1

    def start_test(self):
        """开始测试"""
        self.testing = True
        self.finished = False
        self.current_round = 1
        self.current_target = 0
        self.results = []
        self.start_time = time.time()
        self.round_start_time = time.time()
        self.generate_targets()

    def next_round(self):
        """进入下一轮测试"""
        if self.current_round < self.total_rounds:
            self.current_round += 1
            self.current_target = 0
            self.round_start_time = time.time()
            self.generate_targets()
            return True
        else:
            self.finished = True
            self.testing = False
            return False

    def draw_interface(self):
        """绘制测试界面"""
        screen.fill(BLACK)

        if not self.testing:
            # 显示开始界面
            title = font_large.render("触屏准确性测试", True, WHITE)
            instructions = [
                f"测试轮数: {self.total_rounds}",
                f"每轮目标: {self.targets_per_round}个圆圈",
                "测试方法: 点击屏幕上出现的彩色圆圈",
                "目标: 尽可能快速准确地点击所有圆圈"
            ]

            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

            for i, line in enumerate(instructions):
                text = font_medium.render(line, True, WHITE)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + i * 50))

            self.start_button.draw(screen)
            self.exit_button.draw(screen)

        elif not self.finished:
            # 显示测试界面
            # 绘制状态信息
            status_text = font_medium.render(
                f"轮次: {self.current_round}/{self.total_rounds} | 目标: {self.current_target}/{self.targets_per_round}",
                True, WHITE
            )
            screen.blit(status_text, (20, 20))

            elapsed_time = time.time() - self.round_start_time
            time_text = font_small.render(f"时间: {elapsed_time:.1f}秒", True, WHITE)
            screen.blit(time_text, (SCREEN_WIDTH - 150, 20))

            # 绘制目标圆圈
            for i, (x, y) in enumerate(self.targets):
                color = GREEN if i == 0 else BLUE  # 下一个目标为绿色，其他为蓝色
                pygame.draw.circle(screen, color, (x, y), TARGET_RADIUS)
                pygame.draw.circle(screen, WHITE, (x, y), TARGET_RADIUS, 2)

                # 绘制目标编号
                number = font_medium.render(str(i + 1), True, WHITE)
                screen.blit(number, (x - number.get_width() // 2, y - number.get_height() // 2))

            # 绘制点击指引
            if self.targets:
                next_x, next_y = self.targets[0]
                pygame.draw.circle(screen, RED, (next_x, next_y), TARGET_RADIUS + 5, 2)

        else:
            # 显示结果界面
            total_time = time.time() - self.start_time
            avg_time_per_target = total_time / (self.total_rounds * self.targets_per_round)

            title = font_large.render("测试完成!", True, GREEN)
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

            results_text = [
                f"总测试轮数: {self.total_rounds}",
                f"总目标数: {self.total_rounds * self.targets_per_round}",
                f"总用时: {total_time:.2f}秒",
                f"平均每个目标用时: {avg_time_per_target:.2f}秒",
                "",
                "测试结果已保存到文件"
            ]

            for i, line in enumerate(results_text):
                text = font_medium.render(line, True, WHITE)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 180 + i * 40))

            self.exit_button.draw(screen)

            # 保存结果到文件
            self.save_results(total_time, avg_time_per_target)

        pygame.display.flip()

    def save_results(self, total_time, avg_time):
        """保存测试结果到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/tmp/touch_test_results_{timestamp}.txt"

        with open(filename, "w") as f:
            f.write("触屏准确性测试报告\n")
            f.write("=" * 50 + "\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"屏幕分辨率: {SCREEN_WIDTH}x{SCREEN_HEIGHT}\n")
            f.write(f"测试轮数: {self.total_rounds}\n")
            f.write(f"每轮目标数: {self.targets_per_round}\n")
            f.write(f"总目标数: {self.total_rounds * self.targets_per_round}\n")
            f.write(f"总用时: {total_time:.2f}秒\n")
            f.write(f"平均每个目标用时: {avg_time:.2f}秒\n")
            f.write("\n")

            if self.results:
                f.write("详细点击记录:\n")
                for i, round_result in enumerate(self.results):
                    f.write(f"第{i + 1}轮: {round_result}\n")

        print(f"测试结果已保存到: {filename}")

    def handle_event(self, event):
        """处理事件"""
        if self.start_button.is_clicked(event) and not self.testing:
            self.start_test()
            return True
        elif self.exit_button.is_clicked(event):
            return False
        elif self.next_round_button.is_clicked(event) and self.testing and not self.targets:
            self.next_round()
            return True
        elif event.type == pygame.MOUSEBUTTONDOWN and self.testing and not self.finished:
            hit, index = self.check_hit(event.pos)
            if hit and index == 0:  # 只允许按顺序点击
                self.targets.pop(0)
                self.current_target += 1

                # 记录点击结果
                if len(self.results) < self.current_round:
                    self.results.append([])
                self.results[self.current_round - 1].append({
                    'target': index + 1,
                    'position': self.targets[0] if self.targets else (0, 0),
                    'time': time.time() - self.round_start_time
                })

                # 如果所有目标都已完成，准备下一轮
                if not self.targets:
                    if not self.next_round():
                        self.finished = True
                        self.testing = False
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
        return True


def main():
    """主函数"""
    # 配置测试参数
    TOTAL_ROUNDS = 5  # 总测试轮数
    TARGETS_PER_ROUND = 3  # 每轮目标数量

    test = TouchTest(total_rounds=TOTAL_ROUNDS, targets_per_round=TARGETS_PER_ROUND)
    clock = pygame.time.Clock()
    running = True

    print("触屏准确性测试程序已启动")
    print(f"配置: {TOTAL_ROUNDS}轮测试，每轮{TARGETS_PER_ROUND}个目标")
    print("操作方法:")
    print("  - 点击'开始测试'按钮开始测试")
    print("  - 按照数字顺序点击彩色圆圈")
    print("  - 按ESC键或点击退出按钮结束程序")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                running = test.handle_event(event)

        test.draw_interface()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()