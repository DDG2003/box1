import pygame
import random
import sys


# 初始化Pygame
pygame.init()

# 设置窗口大小和标题
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)  # 添加RESIZABLE标志
pygame.display.set_caption("Word Guessing Game")

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 100, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)

# 设置字体
font = pygame.font.Font(None, 50)       # 用于大文本
small_font = pygame.font.Font(None, 30) # 用于小文本

# 从文件加载单词
def load_words(filename):
    try:
        with open(filename, 'r') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        sys.exit()

# 单词列表
WORDS = load_words('words.txt')
if not WORDS:
    print("Error: No words found in the file.")
    sys.exit()

# 游戏变量
block_size = 100
gap = 20  # 方块之间的间隙
offset_x = 150  # 水平偏移量用于居中
max_attempts = 3
score = 0
attempts = max_attempts

# 生成新单词的函数
def generate_word():
    global current_word, shuffled_word, blocks, target_positions, attempts, game_over, success, message
    current_word = random.choice(WORDS)
    shuffled_word = ''.join(random.sample(current_word, len(current_word)))

    # 初始化方块
    block_positions = [(offset_x + i * (block_size + gap), 200) for i in range(len(shuffled_word))]
    blocks = [{
        'char': char,
        'rect': pygame.Rect(pos, (block_size, block_size)),
        'dragging': False,
        'placed': False
    } for char, pos in zip(shuffled_word, block_positions)]

    # 初始化目标区域
    target_positions = [(offset_x + i * (block_size + gap), 400) for i in range(len(current_word))]

    # 重置尝试次数
    attempts = max_attempts

    # 重置游戏状态
    game_over = False
    success = False
    message = ""

# 初始化第一个单词
generate_word()

# 游戏状态变量
running = True
game_over = False
success = False
message = ""  # 要显示的信息

# 主游戏循环
while running:
    screen.fill(WHITE)

    # 绘制标题
    title = font.render("Word Guessing Game", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    # 绘制分数和剩余尝试次数
    score_text = small_font.render(f"Score: {score}", True, BLACK)
    attempts_text = small_font.render(f"Attempts Left: {attempts}", True, BLACK)
    screen.blit(score_text, (20, 20))
    screen.blit(attempts_text, (20, 60))

    # 绘制信息
    if message:
        message_color = GREEN if success else RED
        message_text = small_font.render(message, True, message_color)
        screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, 100))

    # 绘制目标区域和已放置的字母
    placed_blocks = [None] * len(target_positions)
    for i, pos in enumerate(target_positions):
        pygame.draw.rect(screen, RED, pygame.Rect(pos, (block_size, block_size)), 2)
        # 显示已放置的字母
        for block in blocks:
            if block['placed'] and block['rect'].colliderect(pygame.Rect(pos, (block_size, block_size))):
                placed_blocks[i] = block['char']
                text = font.render(block['char'], True, BLACK)
                text_rect = text.get_rect(center=(pos[0] + block_size // 2, pos[1] + block_size // 2))
                screen.blit(text, text_rect)
                break  # 每个目标框只能有一个字母

    # 绘制可拖动的方块
    for block in blocks:
        # 仅绘制未放置的方块
        if not block['placed']:
            pygame.draw.rect(screen, BLUE, block['rect'])
            text = font.render(block['char'], True, WHITE)
            text_rect = text.get_rect(center=block['rect'].center)
            screen.blit(text, text_rect)

    # 绘制刷新按钮
    refresh_button = pygame.Rect(WIDTH - 200, HEIGHT - 90, 140, 50)
    pygame.draw.rect(screen, YELLOW, refresh_button)
    refresh_text = small_font.render("Refresh Word", True, BLACK)
    refresh_text_rect = refresh_text.get_rect(center=refresh_button.center)
    screen.blit(refresh_text, refresh_text_rect)

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 检查是否点击了刷新按钮
            if refresh_button.collidepoint(event.pos):
                generate_word()
                continue  # 如果点击了刷新，跳过拖动逻辑

            # 检查是否点击了任何方块进行拖动
            for block in blocks:
                if not block['placed'] and block['rect'].collidepoint(event.pos):
                    block['dragging'] = True
                    mouse_x, mouse_y = event.pos
                    block['offset_x'] = block['rect'].x - mouse_x
                    block['offset_y'] = block['rect'].y - mouse_y
                    break  # 一次只能拖动一个方块

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # 释放拖动
            for block in blocks:
                if block['dragging']:
                    block['dragging'] = False
                    # 检查方块是否放置在目标区域
                    placed = False
                    for i, target_pos in enumerate(target_positions):
                        target_rect = pygame.Rect(target_pos, (block_size, block_size))
                        if block['rect'].colliderect(target_rect) and placed_blocks[i] is None:
                            block['rect'].topleft = target_pos
                            block['placed'] = True
                            placed = True
                            break
                    if not placed:
                        # 如果未正确放置，则返回原位置
                        generate_word()
                    break  # 一次只能拖动一个方块

        elif event.type == pygame.MOUSEMOTION:
            # 拖动逻辑
            for block in blocks:
                if block['dragging']:
                    mouse_x, mouse_y = event.pos
                    block['rect'].x = mouse_x + block['offset_x']
                    block['rect'].y = mouse_y + block['offset_y']

    # 检查是否所有目标框都已填满
    if None not in placed_blocks:
        assembled_word = ''.join(placed_blocks)
        if assembled_word == current_word:
            message = "Congratulations! You guessed correctly!"
            score += 1
            success = True
            generate_word()
        else:
            attempts -= 1
            if attempts > 0:
                message = "Incorrect! Try again."
                generate_word()
            else:
                message = f"Failed! The correct word was: {current_word}"
                success = False
                generate_word()

    # 显示结果信息
    if game_over:
        result_color = GREEN if success else RED
        result_text = small_font.render(
            "Congratulations! You guessed correctly!" if success else f"Failed! The correct word was: {current_word}",
            True,
            result_color
        )
        screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2))
        # 显示信息后重置游戏状态
        game_over = False

    # 更新显示
    pygame.display.flip()

    # 控制帧率
    pygame.time.Clock().tick(30)

# 退出Pygame
pygame.quit()
sys.exit()

