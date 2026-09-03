#!/usr/bin/env python3
"""
Linux 屏幕坏点手动检测工具
功能：通过点击屏幕切换颜色检测坏点，界面包含退出按钮
"""

import pygame
import sys
import os

# 初始化pygame
pygame.init()

# 获取当前屏幕的分辨率，并设置为全屏
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("屏幕坏点检测 - 点击切换颜色，按钮退出")

# 定义用于测试的纯色序列 (R, G, B)
colors = [
    (0, 0, 0),  # 黑色 - 用于检测亮点
    (255, 255, 255),  # 白色 - 用于检测暗点
    (255, 0, 0),  # 红色
    (0, 255, 0),  # 绿色
    (0, 0, 255),  # 蓝色
    (255, 255, 0),  # 黄色
    (0, 255, 255),  # 青色
    (255, 0, 255)  # 洋红色
]

color_names = [
    "黑色（检查亮点）",
    "白色（检查暗点）",
    "红色",
    "绿色",
    "蓝色",
    "黄色",
    "青色",
    "洋红色"
]

current_color_index = 0

# 创建字体对象
font_large = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)


class Button:
    """按钮类，用于创建可点击的按钮[1,4](@ref)"""

    def __init__(self, x, y, width, height, text, color=(100, 100, 255), hover_color=(150, 150, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        """绘制按钮[1](@ref)"""
        # 检查鼠标是否悬停在按钮上
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        # 根据悬停状态选择颜色
        button_color = self.hover_color if self.is_hovered else self.color

        # 绘制按钮背景
        pygame.draw.rect(surface, button_color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)  # 白色边框

        # 绘制按钮文字
        text_surface = font_small.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, event):
        """检查按钮是否被点击[1](@ref)"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击
            return self.rect.collidepoint(event.pos)
        return False


# 创建退出按钮（放置在屏幕右下角）
exit_button = Button(
    screen_width - 150,  # x坐标
    screen_height - 80,  # y坐标
    120,  # 宽度
    50,  # 高度
    "ESC",  # 按钮文字
    (200, 50, 50),  # 正常颜色（红色系）
    (255, 80, 80)  # 悬停颜色（亮红色）
)


def draw_interface():
    """绘制整个界面"""
    # 填充背景色
    screen.fill(colors[current_color_index])

    # 根据背景色亮度调整文字颜色，确保可读性
    brightness = sum(colors[current_color_index]) / 3
    text_color = (0, 0, 0) if brightness > 127 else (255, 255, 255)

    #title_text = font_large.render("Screen Dead Pixel Test Tool", True, text_color)
    #color_text = font_small.render(f"Current Background: {color_names[current_color_index]}", True, text_color)
    #help_text = font_small.render("Click anywhere to switch colors | Press ESC or click Exit to quit", True, text_color)

    # 绘制文字（居中显示）
    #screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 50))
    #screen.blit(color_text, (screen_width // 2 - color_text.get_width() // 2, 120))
    #screen.blit(help_text, (screen_width // 2 - help_text.get_width() // 2, 170))

    # 绘制退出按钮
    exit_button.draw(screen)

    pygame.display.flip()


# 主循环
print("屏幕坏点检测程序已启动")
print("操作方法:")
print("  - 点击屏幕任意位置切换颜色")
print("  - 点击右下角退出按钮或按ESC键退出程序")
print("请仔细观察屏幕上是否有始终不随背景色变化的点")

running = True
draw_interface()  # 初始绘制

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # 按ESC退出
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if exit_button.is_clicked(event):  # 点击退出按钮
                running = False
            else:  # 点击屏幕其他位置切换颜色
                current_color_index = (current_color_index + 1) % len(colors)
                print(f"已切换到: {color_names[current_color_index]}")
                draw_interface()

    # 实时更新界面（用于按钮悬停效果）
    draw_interface()

# 退出程序
pygame.quit()
sys.exit()