import pygame
import sys
import numpy as np
import json
import os
import random
from pygame import gfxdraw

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 850
SAVE_FILE = "paint_save.json"

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
PANEL_COLOR = (240, 240, 245)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 150, 200)
PANEL_BORDER = (180, 180, 180)

COLOR_PALETTE = {
    1: (255, 0, 0),      # Красный
    2: (0, 0, 255),      # Синий
    3: (0, 255, 0),      # Зелёный
    4: (255, 255, 0),    # Жёлтый
    5: (255, 165, 0),    # Оранжевый
    6: (128, 0, 128),    # Фиолетовый
    7: (0, 255, 255),    # Голубой
    8: (255, 192, 203),  # Розовый
    9: (165, 42, 42),    # Коричневый
    10: (0, 0, 0),       # Чёрный
}

# Уровни
LEVELS = [
    {  # Уровень 1: Сердце (5x5)
        "name": "Сердце",
        "grid": [
            [0, 1, 0, 1, 0],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [0, 1, 1, 1, 0],
            [0, 0, 1, 0, 0],
        ],
        "cell_size": 80,
        "difficulty": "Легкий"
    },
    {  # Уровень 2: Кошка (8x8)
        "name": "хз",
        "grid": [
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 1, 4, 4, 1, 0, 0],
            [0, 1, 4, 4, 4, 4, 1, 0],
            [1, 4, 4, 4, 4, 4, 4, 1],
            [1, 4, 4, 4, 4, 4, 4, 1],
            [1, 4, 4, 4, 4, 4, 4, 1],
            [0, 1, 1, 5, 5, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
        ],
        "cell_size": 60,
        "difficulty": "Средний"
    }
]

class PaintByNumbers:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Рисование по номерам")
        self.clock = pygame.time.Clock()
        self.current_level = 0
        self.selected_color = 1
        self.math_problem = ""
        self.math_answer = None
        self.math_input = ""
        self.math_feedback = ""
        self.math_feedback_timer = 0
        self.show_math_panel = False
        self.font_large = pygame.font.SysFont("Arial", 36)
        self.font_medium = pygame.font.SysFont("Arial", 28)
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.progress = 0
        self.color_unlocked = False
        self.active_input = False
        self.palette_scroll = 0
        self.color_click_time = 0
        self.color_click_cooldown = 500
        
        # Инициализация уровня
        self.load_level(self.current_level)
        self.load_progress()

    def safe_load_json(self, filepath):
        """Безопасная загрузка JSON с обработкой ошибок"""
        try:
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                with open(filepath, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка загрузки файла {filepath}: {e}")
        return {}

    def load_level(self, level_idx):
        """Загружает уровень по индексу с проверкой границ"""
        if level_idx < 0:
            level_idx = 0
        elif level_idx >= len(LEVELS):
            level_idx = len(LEVELS) - 1
            
        self.current_level = level_idx
        level = LEVELS[level_idx]
        self.grid = np.array(level["grid"])
        self.colored = np.zeros(self.grid.shape, dtype=int)
        self.cell_size = level["cell_size"]
        self.level_name = level["name"]
        self.difficulty = level.get("difficulty", "Не указана")
        self.total_cells = np.count_nonzero(self.grid)
        self.update_progress()

    def update_progress(self):
        """Обновляет прогресс заполнения уровня"""
        colored_cells = np.count_nonzero(self.colored)
        self.progress = int((colored_cells / self.total_cells) * 100) if self.total_cells > 0 else 0

    def load_progress(self):
        """Загружает прогресс из файла с обработкой ошибок"""
        data = self.safe_load_json(SAVE_FILE)
        if str(self.current_level) in data:
            try:
                saved_data = np.array(data[str(self.current_level)])
                if saved_data.shape == self.colored.shape:
                    self.colored = saved_data
                    self.update_progress()
            except (ValueError, KeyError) as e:
                print(f"Ошибка загрузки прогресса: {e}")

    def save_progress(self):
        """Сохраняет прогресс с обработкой ошибок"""
        try:
            data = self.safe_load_json(SAVE_FILE)
            data[str(self.current_level)] = self.colored.tolist()
            
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Ошибка сохранения прогресса: {e}")

    def generate_math_problem(self, color_num):
        """Генерирует математическую задачу для выбранного цвета"""
        current_time = pygame.time.get_ticks()
        if current_time - self.color_click_time < self.color_click_cooldown:
            return
            
        self.color_click_time = current_time
        
        operations = ['+', '-', '*']
        op = random.choice(operations)
        
        if op == '+':
            a = random.randint(1, 15)
            b = random.randint(1, 15)
            answer = a + b
        elif op == '-':
            a = random.randint(5, 20)
            b = random.randint(1, a)
            answer = a - b
        else:  # '*'
            a = random.randint(1, 9)
            b = random.randint(1, 9)
            answer = a * b
        
        self.math_problem = f"{a} {op} {b} = ?"
        self.math_answer = answer
        self.math_input = ""
        self.show_math_panel = True
        self.selected_color = color_num
        self.color_unlocked = False
        self.active_input = True

    def check_math_answer(self):
        """Проверяет ответ на математическую задачу"""
        try:
            user_answer = int(self.math_input)
            if user_answer == self.math_answer:
                self.math_feedback = "Правильно! Цвет разблокирован."
                self.color_unlocked = True
                self.math_feedback_timer = 120  # 2 секунды при 60 FPS
            else:
                self.math_feedback = f"Ошибка! Правильно: {self.math_answer}"
                self.color_unlocked = False
                self.math_feedback_timer = 120
                self.active_input = True
        except ValueError:
            self.math_feedback = "Введите число!"
            self.math_feedback_timer = 120
            self.active_input = True

    def draw_color_palette(self):
        """Рисует палитру цветов"""
        palette_x = 20
        palette_y = 150
        color_size = 50
        margin = 10
        cols = 5
        
        # Фон палитры
        palette_rect = pygame.Rect(palette_x - 5, palette_y - 35, 
                                 cols * (color_size + margin) + 10, 
                                 min(3, (len(COLOR_PALETTE)+cols-1)//cols) * (color_size + margin) + 40)
        pygame.draw.rect(self.screen, PANEL_COLOR, palette_rect, border_radius=10)
        pygame.draw.rect(self.screen, PANEL_BORDER, palette_rect, 2, border_radius=10)
        
        title = self.font_medium.render("Палитра цветов:", True, BLACK)
        self.screen.blit(title, (palette_x, palette_y - 30))
        
        # Отображение цветов
        for i, (color_num, color) in enumerate(COLOR_PALETTE.items()):
            row = i // cols
            col = i % cols
            
            x = palette_x + col * (color_size + margin)
            y = palette_y + row * (color_size + margin)
            
            rect = pygame.Rect(x, y, color_size, color_size)
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            
            # Обводка для выбранного цвета
            if color_num == self.selected_color:
                if self.color_unlocked:
                    pygame.draw.rect(self.screen, (0, 255, 0), rect, 3, border_radius=5)
                else:
                    pygame.draw.rect(self.screen, (255, 0, 0), rect, 3, border_radius=5)
            else:
                pygame.draw.rect(self.screen, BLACK, rect, 1, border_radius=5)
            
            # Номер цвета
            num_text = self.font_small.render(str(color_num), True, BLACK)
            self.screen.blit(num_text, (x + color_size//2 - 5, y + color_size//2 - 10))
            
            # Обработка клика
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (255, 255, 255, 150), rect, 2, border_radius=5)
                if mouse_pressed[0]:
                    self.generate_math_problem(color_num)

    def draw_math_panel(self):
        """Рисует панель с математической задачей"""
        if not self.show_math_panel:
            return
            
        # Фон панели
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 150, 500, 300)
        pygame.draw.rect(self.screen, PANEL_COLOR, panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, PANEL_BORDER, panel_rect, 3, border_radius=15)
        
        # Заголовок
        title = self.font_large.render(f"Решите задачу для цвета {self.selected_color}", True, BLACK)
        self.screen.blit(title, (panel_rect.x + 20, panel_rect.y + 30))
        
        # Математическая задача
        problem_text = self.font_large.render(self.math_problem, True, (0, 0, 150))
        self.screen.blit(problem_text, (panel_rect.x + 50, panel_rect.y + 100))
        
        # Поле ввода
        input_rect = pygame.Rect(panel_rect.x + 150, panel_rect.y + 150, 200, 50)
        pygame.draw.rect(self.screen, WHITE, input_rect, border_radius=5)
        border_color = BUTTON_HOVER if self.active_input else PANEL_BORDER
        pygame.draw.rect(self.screen, border_color, input_rect, 3, border_radius=5)
        
        input_text = self.font_large.render(self.math_input, True, BLACK)
        self.screen.blit(input_text, (input_rect.x + 20, input_rect.y + 15))
        
        # Кнопка проверки
        check_rect = pygame.Rect(panel_rect.x + 150, panel_rect.y + 220, 200, 50)
        pygame.draw.rect(self.screen, BUTTON_COLOR, check_rect, border_radius=5)
        if check_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(self.screen, BUTTON_HOVER, check_rect, border_radius=5)
        check_text = self.font_medium.render("Проверить", True, WHITE)
        self.screen.blit(check_text, (check_rect.x + 60, check_rect.y + 15))
        
        # Обратная связь
        if self.math_feedback_timer > 0:
            color = (0, 180, 0) if "Правильно" in self.math_feedback else (180, 0, 0)
            feedback_text = self.font_medium.render(self.math_feedback, True, color)
            self.screen.blit(feedback_text, (panel_rect.x + 50, panel_rect.y + 270))
            self.math_feedback_timer -= 1
            
            if self.math_feedback_timer == 0 and self.color_unlocked:
                self.show_math_panel = False
        
        # Обработка кликов
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        if mouse_pressed[0]:
            if input_rect.collidepoint(mouse_pos):
                self.active_input = True
            elif check_rect.collidepoint(mouse_pos):
                self.check_math_answer()
            elif not panel_rect.collidepoint(mouse_pos):
                pass

    def draw_grid(self):
        """Рисует сетку с фигурой"""
        rows, cols = self.grid.shape
        start_x = (SCREEN_WIDTH - cols * self.cell_size) // 2
        start_y = 300
        
        for y in range(rows):
            for x in range(cols):
                rect = pygame.Rect(
                    start_x + x * self.cell_size,
                    start_y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                if self.colored[y, x] != 0:
                    pygame.draw.rect(self.screen, COLOR_PALETTE[self.colored[y, x]], rect, border_radius=3)
                elif self.grid[y, x] != 0:
                    pygame.draw.rect(self.screen, WHITE, rect, border_radius=3)
                    text = self.font_small.render(str(self.grid[y, x]), True, BLACK)
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)
                else:
                    pygame.draw.rect(self.screen, LIGHT_GRAY, rect, border_radius=3)
                
                pygame.draw.rect(self.screen, BLACK, rect, 1, border_radius=3)

    def draw_ui(self):
        """Рисует основной интерфейс"""
        # Фон верхней панели
        pygame.draw.rect(self.screen, PANEL_COLOR, (0, 0, SCREEN_WIDTH, 100))
        pygame.draw.rect(self.screen, PANEL_BORDER, (0, 100, SCREEN_WIDTH, 2))
        
        # Название уровня и сложность
        title = f"{self.level_name} (Уровень {self.current_level + 1}/{len(LEVELS)})"
        title_text = self.font_large.render(title, True, BLACK)
        self.screen.blit(title_text, (20, 20))
        
        difficulty_text = self.font_medium.render(f"Сложность: {self.difficulty}", True, BLACK)
        self.screen.blit(difficulty_text, (20, 60))
        
        # Кнопки навигации
        prev_btn = pygame.Rect(SCREEN_WIDTH - 250, 20, 100, 40)
        next_btn = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 40)
        
        # Кнопка "Назад"
        pygame.draw.rect(self.screen, BUTTON_COLOR if self.current_level > 0 else GRAY, prev_btn, border_radius=5)
        prev_text = self.font_medium.render("Назад", True, WHITE)
        self.screen.blit(prev_text, (prev_btn.x + 25, prev_btn.y + 10))
        
        # Кнопка "Вперёд"
        pygame.draw.rect(self.screen, BUTTON_COLOR if self.current_level < len(LEVELS) - 1 else GRAY, next_btn, border_radius=5)
        next_text = self.font_medium.render("Вперёд", True, WHITE)
        self.screen.blit(next_text, (next_btn.x + 20, next_btn.y + 10))
        
        # Прогресс
        progress_rect = pygame.Rect(SCREEN_WIDTH - 400, 20, 120, 40)
        pygame.draw.rect(self.screen, PANEL_COLOR, progress_rect, border_radius=5)
        pygame.draw.rect(self.screen, PANEL_BORDER, progress_rect, 2, border_radius=5)
        progress_text = self.font_medium.render(f"Прогресс: {self.progress}%", True, BLACK)
        self.screen.blit(progress_text, (progress_rect.x + 10, progress_rect.y + 10))
        
        # Индикатор выбранного цвета
        if self.selected_color:
            color_rect = pygame.Rect(SCREEN_WIDTH - 550, 20, 120, 40)
            pygame.draw.rect(self.screen, PANEL_COLOR, color_rect, border_radius=5)
            pygame.draw.rect(self.screen, PANEL_BORDER, color_rect, 2, border_radius=5)
            
            color_text = self.font_medium.render(f"Цвет: {self.selected_color}", True, BLACK)
            color_sample = pygame.Rect(SCREEN_WIDTH - 570, 25, 20, 30)
            pygame.draw.rect(self.screen, COLOR_PALETTE[self.selected_color], color_sample, border_radius=3)
            pygame.draw.rect(self.screen, BLACK, color_sample, 1, border_radius=3)
            
            self.screen.blit(color_text, (color_rect.x + 30, color_rect.y + 10))
        
        return prev_btn, next_btn

    def handle_click(self, pos):
        """Обрабатывает клики по игровому полю"""
        if self.show_math_panel:
            return
            
        rows, cols = self.grid.shape
        start_x = (SCREEN_WIDTH - cols * self.cell_size) // 2
        start_y = 300
        
        if (start_x <= pos[0] <= start_x + cols * self.cell_size and
            start_y <= pos[1] <= start_y + rows * self.cell_size):
            grid_x = (pos[0] - start_x) // self.cell_size
            grid_y = (pos[1] - start_y) // self.cell_size
            
            if (self.grid[grid_y, grid_x] == self.selected_color and 
                self.color_unlocked and
                self.colored[grid_y, grid_x] == 0):
                
                self.colored[grid_y, grid_x] = self.selected_color
                self.save_progress()
                self.update_progress()

    def run(self):
        """Основной игровой цикл"""
        running = True
        while running:
            self.screen.fill(WHITE)
            
            # Отрисовка интерфейса
            prev_btn, next_btn = self.draw_ui()
            self.draw_color_palette()
            self.draw_grid()
            self.draw_math_panel()
            
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if prev_btn.collidepoint(event.pos) and self.current_level > 0:
                        self.save_progress()
                        self.current_level -= 1
                        self.load_level(self.current_level)
                        self.show_math_panel = False
                    elif next_btn.collidepoint(event.pos) and self.current_level < len(LEVELS) - 1:
                        self.save_progress()
                        self.current_level += 1
                        self.load_level(self.current_level)
                        self.show_math_panel = False
                    elif not self.show_math_panel:
                        self.handle_click(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    if self.show_math_panel and self.active_input:
                        if event.key == pygame.K_RETURN:
                            self.check_math_answer()
                        elif event.key == pygame.K_BACKSPACE:
                            self.math_input = self.math_input[:-1]
                        elif event.unicode.isdigit():
                            if len(self.math_input) < 3:
                                self.math_input += event.unicode
            
            pygame.display.flip()
            self.clock.tick(60)

        self.save_progress()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PaintByNumbers()
    game.run()