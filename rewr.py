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
PROGRESS_BAR_COLOR = (100, 200, 100)
PROGRESS_BG_COLOR = (220, 220, 220)
HOVER_COLOR = (220, 220, 220, 150)
COMPLETION_ANIMATION_COLOR = (50, 200, 50)
GRID_HIGHLIGHT_COLOR = (255, 255, 0, 100)
HINT_BG_COLOR = (240, 240, 245)  # Убрали альфа-канал

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
    11: (169, 169, 169), # Серый
    12: (255, 215, 0),   # Золотой
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
        "difficulty": "Легкий",
        "hint": "Начните с центральных клеток, чтобы понять форму сердца."
    },
    {  # Уровень 2: Кошка (8x8)
        "name": "Кошка",
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
        "difficulty": "Средний",
        "hint": "Сначала раскрасьте уши (желтые клетки), затем мордочку."
    },
    {  # Уровень 3: Машинка (10x10)
        "name": "Машинка",
        "grid": [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 2, 2, 2, 2, 1, 0, 0],
            [0, 1, 2, 2, 2, 2, 2, 2, 1, 0],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 3, 3, 3, 3, 2, 2, 1],
            [1, 2, 3, 3, 3, 3, 3, 3, 2, 1],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        ],
        "cell_size": 50,
        "difficulty": "Средний",
        "hint": "Начните с колес (зеленые клетки), затем кузов (синие)."
    },
    {  # Уровень 4: Дом (12x12)
        "name": "Дом",
        "grid": [
            [0, 0, 0, 0, 0, 4, 4, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 4, 4, 4, 4, 0, 0, 0, 0],
            [0, 0, 0, 4, 4, 4, 4, 4, 4, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 5, 5, 5, 5, 5, 5, 1, 1, 0],
            [1, 1, 5, 5, 5, 5, 5, 5, 5, 5, 1, 1],
            [1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1],
            [1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1],
            [1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1],
            [1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        "cell_size": 45,
        "difficulty": "Сложный",
        "hint": "Сначала крыша (желтая), затем стены (коричневые)."
    },
    {  # Уровень 5: Самолет (15x10)
        "name": "Самолет",
        "grid": [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        "cell_size": 40,
        "difficulty": "Сложный",
        "hint": "Начните с хвоста (красные клетки), затем крылья."
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
        self.target_progress = 0
        self.color_unlocked = False
        self.active_input = False
        self.palette_scroll = 0
        self.color_click_time = 0
        self.color_click_cooldown = 500
        self.completion_animation = False
        self.completion_alpha = 0
        self.hovered_cell = None
        self.last_hover_time = 0
        self.hint_alpha = 0
        self.show_hint = True
        self.progress_animation = 0
        self.show_level_complete = False
        self.level_complete_time = 0
        
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
        self.hint = level.get("hint", "Подсказка отсутствует")
        self.total_cells = np.count_nonzero(self.grid)
        self.update_progress(instant=True)
        self.completion_animation = False
        self.completion_alpha = 0
        self.show_level_complete = False

    def update_progress(self, instant=False):
        """Обновляет прогресс заполнения уровня"""
        colored_cells = np.count_nonzero(self.colored)
        self.target_progress = int((colored_cells / self.total_cells) * 100) if self.total_cells > 0 else 0
        
        if instant:
            self.progress = self.target_progress
            self.progress_animation = self.target_progress
        elif self.target_progress == 100:
            self.completion_animation = True
            self.show_level_complete = True
            self.level_complete_time = pygame.time.get_ticks()
            self.save_progress()

    def load_progress(self):
        """Загружает прогресс из файла с обработкой ошибок"""
        data = self.safe_load_json(SAVE_FILE)
        if str(self.current_level) in data:
            try:
                saved_data = np.array(data[str(self.current_level)])
                if saved_data.shape == self.colored.shape:
                    self.colored = saved_data
                    self.update_progress(instant=True)
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
        """Рисует палитру цветов с анимацией"""
        palette_x = 20
        palette_y = 150
        color_size = 50
        margin = 10
        cols = 5
        
        # Фон палитры с полупрозрачностью
        palette_rect = pygame.Rect(palette_x - 5, palette_y - 35, 
                                 cols * (color_size + margin) + 10, 
                                 min(3, (len(COLOR_PALETTE)+cols-1)//cols) * (color_size + margin) + 40)
        palette_surface = pygame.Surface((palette_rect.width, palette_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(palette_surface, (*PANEL_COLOR, 200), palette_surface.get_rect(), border_radius=10)
        pygame.draw.rect(palette_surface, (*PANEL_BORDER, 200), palette_surface.get_rect(), 2, border_radius=10)
        self.screen.blit(palette_surface, palette_rect)
        
        title = self.font_medium.render("Палитра цветов:", True, BLACK)
        title_rect = title.get_rect(center=(palette_x + (cols*(color_size + margin))//2, palette_y - 20))
        self.screen.blit(title, title_rect)
        
        # Отображение цветов
        for i, (color_num, color) in enumerate(COLOR_PALETTE.items()):
            row = i // cols
            col = i % cols
            
            x = palette_x + col * (color_size + margin)
            y = palette_y + row * (color_size + margin)
            
            rect = pygame.Rect(x, y, color_size, color_size)
            
            # Анимация при наведении
            mouse_pos = pygame.mouse.get_pos()
            hover = rect.collidepoint(mouse_pos)
            
            if hover:
                hover_surface = pygame.Surface((color_size, color_size), pygame.SRCALPHA)
                hover_surface.fill(HOVER_COLOR)
                self.screen.blit(hover_surface, rect)
                
                if pygame.mouse.get_pressed()[0]:
                    self.generate_math_problem(color_num)
            
            # Основной цвет
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            
            # Обводка для выбранного цвета
            if color_num == self.selected_color:
                if self.color_unlocked:
                    pygame.draw.rect(self.screen, (0, 255, 0), rect, 3, border_radius=5)
                else:
                    pygame.draw.rect(self.screen, (255, 0, 0), rect, 3, border_radius=5)
            else:
                pygame.draw.rect(self.screen, BLACK, rect, 1, border_radius=5)
            
            # Номер цвета (по центру)
            num_text = self.font_small.render(str(color_num), True, BLACK)
            num_rect = num_text.get_rect(center=rect.center)
            self.screen.blit(num_text, num_rect)

    def draw_math_panel(self):
        """Рисует панель с математической задачей"""
        if not self.show_math_panel:
            return
            
        # Фон панели с полупрозрачностью
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 150, 500, 300)
        panel_surface = pygame.Surface((500, 300), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*PANEL_COLOR, 220), panel_surface.get_rect(), border_radius=15)
        pygame.draw.rect(panel_surface, (*PANEL_BORDER, 220), panel_surface.get_rect(), 3, border_radius=15)
        self.screen.blit(panel_surface, panel_rect)
        
        # Заголовок (по центру)
        title = self.font_large.render(f"Решите задачу для цвета {self.selected_color}", True, BLACK)
        title_rect = title.get_rect(center=(panel_rect.centerx, panel_rect.y + 50))
        self.screen.blit(title, title_rect)
        
        # Математическая задача (по центру)
        problem_text = self.font_large.render(self.math_problem, True, (0, 0, 150))
        problem_rect = problem_text.get_rect(center=(panel_rect.centerx, panel_rect.y + 100))
        self.screen.blit(problem_text, problem_rect)
        
        # Поле ввода (по центру)
        input_rect = pygame.Rect(panel_rect.centerx - 100, panel_rect.y + 150, 200, 50)
        pygame.draw.rect(self.screen, WHITE, input_rect, border_radius=5)
        border_color = BUTTON_HOVER if self.active_input else PANEL_BORDER
        pygame.draw.rect(self.screen, border_color, input_rect, 3, border_radius=5)
        
        input_text = self.font_large.render(self.math_input, True, BLACK)
        input_text_rect = input_text.get_rect(center=input_rect.center)
        self.screen.blit(input_text, input_text_rect)
        
        # Кнопка проверки (по центру)
        check_rect = pygame.Rect(panel_rect.centerx - 100, panel_rect.y + 220, 200, 50)
        pygame.draw.rect(self.screen, BUTTON_COLOR, check_rect, border_radius=5)
        
        # Анимация наведения на кнопку
        if check_rect.collidepoint(pygame.mouse.get_pos()):
            hover_surface = pygame.Surface((200, 50), pygame.SRCALPHA)
            hover_surface.fill((*BUTTON_HOVER, 50))
            self.screen.blit(hover_surface, check_rect)
        
        check_text = self.font_medium.render("Проверить", True, WHITE)
        check_text_rect = check_text.get_rect(center=check_rect.center)
        self.screen.blit(check_text, check_text_rect)
        
        # Обратная связь (по центру)
        if self.math_feedback_timer > 0:
            color = (0, 180, 0) if "Правильно" in self.math_feedback else (180, 0, 0)
            feedback_text = self.font_medium.render(self.math_feedback, True, color)
            feedback_rect = feedback_text.get_rect(center=(panel_rect.centerx, panel_rect.y + 270))
            self.screen.blit(feedback_text, feedback_rect)
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
        """Рисует сетку с фигурой и подсветкой"""
        rows, cols = self.grid.shape
        start_x = (SCREEN_WIDTH - cols * self.cell_size) // 2
        start_y = 300
        
        # Подсветка клетки при наведении
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_cell = None
        
        for y in range(rows):
            for x in range(cols):
                rect = pygame.Rect(
                    start_x + x * self.cell_size,
                    start_y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                # Определяем наведение мыши
                if rect.collidepoint(mouse_pos):
                    self.hovered_cell = (x, y)
                    if pygame.time.get_ticks() - self.last_hover_time > 300:  # Задержка
                        hover_surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                        hover_surface.fill(GRID_HIGHLIGHT_COLOR)
                        self.screen.blit(hover_surface, rect)
                        self.last_hover_time = pygame.time.get_ticks()
                
                # Отрисовка клетки
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
        
        # Анимация завершения уровня
        if self.completion_animation:
            self.completion_alpha = min(self.completion_alpha + 4, 180)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((*COMPLETION_ANIMATION_COLOR, self.completion_alpha))
            self.screen.blit(overlay, (0, 0))
            
            if self.completion_alpha >= 180:
                congrats_text = self.font_large.render("Уровень пройден!", True, WHITE)
                text_rect = congrats_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(congrats_text, text_rect)
                
                # Кнопка "Следующий уровень"
                if self.current_level < len(LEVELS) - 1:
                    next_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 50)
                    pygame.draw.rect(self.screen, BUTTON_COLOR, next_btn, border_radius=5)
                    
                    if next_btn.collidepoint(pygame.mouse.get_pos()):
                        hover_surface = pygame.Surface((200, 50), pygame.SRCALPHA)
                        hover_surface.fill((*BUTTON_HOVER, 50))
                        self.screen.blit(hover_surface, next_btn)
                    
                    next_text = self.font_medium.render("Следующий уровень", True, WHITE)
                    next_text_rect = next_text.get_rect(center=next_btn.center)
                    self.screen.blit(next_text, next_text_rect)
        else:
            self.completion_alpha = 0

    def draw_ui(self):
        """Рисует улучшенный интерфейс с подсказками"""
        # Фон верхней панели с полупрозрачностью
        panel_surface = pygame.Surface((SCREEN_WIDTH, 100), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*PANEL_COLOR, 220), panel_surface.get_rect())
        pygame.draw.rect(panel_surface, (*PANEL_BORDER, 220), panel_surface.get_rect(), 2)
        self.screen.blit(panel_surface, (0, 0))
        
        # Название уровня и сложность (по центру)
        title = f"{self.level_name} (Уровень {self.current_level + 1}/{len(LEVELS)})"
        title_text = self.font_large.render(title, True, BLACK)
        title_rect = title_text.get_rect(midleft=(20, 30))
        self.screen.blit(title_text, title_rect)
        
        difficulty_text = self.font_medium.render(f"Сложность: {self.difficulty}", True, BLACK)
        difficulty_rect = difficulty_text.get_rect(midleft=(20, 70))
        self.screen.blit(difficulty_text, difficulty_rect)
        
        # Кнопки навигации
        prev_btn = pygame.Rect(SCREEN_WIDTH - 250, 20, 100, 40)
        next_btn = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 40)
        
        # Кнопка "Назад"
        pygame.draw.rect(self.screen, BUTTON_COLOR if self.current_level > 0 else GRAY, prev_btn, border_radius=5)
        prev_text = self.font_medium.render("Назад", True, WHITE)
        prev_text_rect = prev_text.get_rect(center=prev_btn.center)
        self.screen.blit(prev_text, prev_text_rect)
        
        # Анимация наведения на кнопку
        if prev_btn.collidepoint(pygame.mouse.get_pos()) and self.current_level > 0:
            hover_surface = pygame.Surface((100, 40), pygame.SRCALPHA)
            hover_surface.fill((*BUTTON_HOVER, 50))
            self.screen.blit(hover_surface, prev_btn)
        
        # Кнопка "Вперёд"
        pygame.draw.rect(self.screen, BUTTON_COLOR if self.current_level < len(LEVELS) - 1 else GRAY, next_btn, border_radius=5)
        next_text = self.font_medium.render("Вперёд", True, WHITE)
        next_text_rect = next_text.get_rect(center=next_btn.center)
        self.screen.blit(next_text, next_text_rect)
        
        if next_btn.collidepoint(pygame.mouse.get_pos()) and self.current_level < len(LEVELS) - 1:
            hover_surface = pygame.Surface((100, 40), pygame.SRCALPHA)
            hover_surface.fill((*BUTTON_HOVER, 50))
            self.screen.blit(hover_surface, next_btn)
        
        # Прогресс-бар (длинный) с анимацией
        progress_width = 300
        progress_rect = pygame.Rect(SCREEN_WIDTH - 550, 20, progress_width, 25)
        
        # Плавная анимация прогресса
        if self.progress_animation < self.target_progress:
            self.progress_animation += 1
        elif self.progress_animation > self.target_progress:
            self.progress_animation -= 1
        
        # Фон прогресс-бара
        pygame.draw.rect(self.screen, PROGRESS_BG_COLOR, progress_rect, border_radius=12)
        
        # Заполненная часть прогресс-бара
        fill_width = int(progress_width * self.progress_animation / 100)
        fill_rect = pygame.Rect(SCREEN_WIDTH - 550, 20, fill_width, 25)
        pygame.draw.rect(self.screen, PROGRESS_BAR_COLOR, fill_rect, border_radius=12)
        
        # Граница прогресс-бара
        pygame.draw.rect(self.screen, PANEL_BORDER, progress_rect, 2, border_radius=12)
        
        # Текст прогресса (по центру прогресс-бара)
        progress_text = self.font_medium.render(f"{self.progress_animation}%", True, BLACK)
        progress_text_rect = progress_text.get_rect(center=progress_rect.center)
        self.screen.blit(progress_text, progress_text_rect)
        
        # Подсказка (появляется при наведении на иконку)
        hint_rect = pygame.Rect(SCREEN_WIDTH - 600, 70, 30, 30)
        pygame.draw.rect(self.screen, BUTTON_COLOR, hint_rect, border_radius=15)
        hint_icon = self.font_small.render("?", True, WHITE)
        hint_icon_rect = hint_icon.get_rect(center=hint_rect.center)
        self.screen.blit(hint_icon, hint_icon_rect)
        
        # Показываем подсказку при наведении
        if hint_rect.collidepoint(pygame.mouse.get_pos()):
            self.hint_alpha = min(self.hint_alpha + 10, 200)
        else:
            self.hint_alpha = max(self.hint_alpha - 5, 0)
        
        if self.hint_alpha > 0:
            hint_surface = pygame.Surface((400, 100), pygame.SRCALPHA)
            pygame.draw.rect(hint_surface, (*HINT_BG_COLOR, self.hint_alpha), hint_surface.get_rect(), border_radius=10)
            pygame.draw.rect(hint_surface, (*PANEL_BORDER, self.hint_alpha), hint_surface.get_rect(), 2, border_radius=10)
            self.screen.blit(hint_surface, (SCREEN_WIDTH - 580, 110))
            
            hint_lines = [self.hint[i:i+50] for i in range(0, len(self.hint), 50)]
            for i, line in enumerate(hint_lines):
                hint_text = self.font_small.render(line, True, BLACK)
                self.screen.blit(hint_text, (SCREEN_WIDTH - 570, 120 + i * 25))

    def handle_events(self):
        """Обрабатывает события игры"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_progress()
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    # Обработка кликов по сетке
                    if self.hovered_cell and self.color_unlocked and not self.show_math_panel:
                        x, y = self.hovered_cell
                        if self.grid[y, x] != 0:  # Можно красить только ненулевые клетки
                            self.colored[y, x] = self.selected_color
                            self.update_progress()
                            self.save_progress()
                    
                    # Обработка кнопок навигации
                    prev_btn = pygame.Rect(SCREEN_WIDTH - 250, 20, 100, 40)
                    next_btn = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 40)
                    
                    if prev_btn.collidepoint(event.pos) and self.current_level > 0:
                        self.load_level(self.current_level - 1)
                    elif next_btn.collidepoint(event.pos) and self.current_level < len(LEVELS) - 1:
                        self.load_level(self.current_level + 1)
                    
                    # Обработка кнопки "Следующий уровень" после завершения
                    if self.completion_animation and self.target_progress == 100:
                        next_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 50)
                        if next_btn.collidepoint(event.pos) and self.current_level < len(LEVELS) - 1:
                            self.load_level(self.current_level + 1)
                            self.completion_animation = False
                
            elif event.type == pygame.KEYDOWN:
                if self.active_input and self.show_math_panel:
                    if event.key == pygame.K_RETURN:
                        self.check_math_answer()
                    elif event.key == pygame.K_BACKSPACE:
                        self.math_input = self.math_input[:-1]
                    elif event.unicode.isdigit():
                        self.math_input += event.unicode
                
                # Быстрые клавиши для смены уровней
                elif event.key == pygame.K_LEFT and self.current_level > 0:
                    self.load_level(self.current_level - 1)
                elif event.key == pygame.K_RIGHT and self.current_level < len(LEVELS) - 1:
                    self.load_level(self.current_level + 1)
                
                # Быстрая клавиша для подсказки
                elif event.key == pygame.K_h:
                    self.show_hint = not self.show_hint
            
            elif event.type == pygame.USEREVENT and self.completion_animation:
                self.completion_animation = False

    def run(self):
        """Главный цикл игры"""
        while True:
            self.handle_events()
            
            # Очистка экрана
            self.screen.fill(WHITE)
            
            # Отрисовка элементов
            self.draw_ui()
            self.draw_color_palette()
            self.draw_grid()
            self.draw_math_panel()
            
            # Обновление экрана
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = PaintByNumbers()
    game.run()