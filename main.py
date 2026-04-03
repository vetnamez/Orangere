import pygame
import sys
from game_logic import Farm, SORTS
from save_load import save_game, load_game
from graph import generate_income_graph
import os

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 30
PLOT_SIZE = 100
PLOT_MARGIN = 10
GRID_OFFSET_X = 150  # отступ слева для сетки
GRID_OFFSET_Y = 80   # отступ сверху
COLS, ROWS = 4, 4

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHT_GREEN = (144, 238, 144)
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)

# Шрифты
font_small = pygame.font.Font(None, 24)
font_medium = pygame.font.Font(None, 28)
font_large = pygame.font.Font(None, 36)

#


data_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], "data")


def load_img(file):
    return pygame.image.load(os.path.join(data_dir, file))
#Спрайты растений и фона
flower1 = load_img('flower1.png')
flower2 = load_img('flower2.png')
flower3 = load_img('flower3.png')
flower4 = load_img('flower4.png')
background = load_img("background.jpg")

flower1 = pygame.transform.scale(flower1, (100, 50))
flower2 = pygame.transform.scale(flower2, (100, 50))
flower3 = pygame.transform.scale(flower3, (100, 50))
flower4 = pygame.transform.scale(flower4, (100, 50))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Марсианская ферма")
        self.clock = pygame.time.Clock()
        self.running = True
        self.farm = None
        self.load_or_new_game()
        self.active_sort = "Аресис"  # выбранный сорт для посадки
        self.message = None
        self.message_end_time = 0
        self.last_save_time = pygame.time.get_ticks()
        self.showing_graph = False
        self.graph_surface = None

    def load_or_new_game(self):
        loaded = load_game()
        if loaded:
            self.farm = loaded
        else:
            self.farm = Farm()

    def save_current_game(self):
        save_game(self.farm)

    def show_message(self, text, duration_ms=2000):
        self.message = text
        self.message_end_time = pygame.time.get_ticks() + duration_ms

    def draw_background(self):
        self.screen.blit(background, (0,0))
        self.screen.blit(flower1, (WIDTH/16, HEIGHT/2))
        self.screen.blit(flower3, (WIDTH / 3, HEIGHT / 16 * 14))
        self.screen.blit(flower2, (WIDTH / 3 * 2, HEIGHT / 32 * 29))
        self.screen.blit(flower4, (WIDTH / 3 * 2 + 50, HEIGHT / 32 * 29 - 50))

    def draw_grid(self):
        for x in range(COLS):
            for y in range(ROWS):
                rect = pygame.Rect(GRID_OFFSET_X + x * (PLOT_SIZE + PLOT_MARGIN),
                                   GRID_OFFSET_Y + y * (PLOT_SIZE + PLOT_MARGIN),
                                   PLOT_SIZE, PLOT_SIZE)
                plot = self.farm.plots[x][y]
                # Цвет в зависимости от состояния
                if plot['state'] == 'empty':
                    color = BROWN
                elif plot['state'] == 'growing':
                    color = LIGHT_GREEN
                else:  # ready
                    color = YELLOW
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 2)
                # Текст
                if plot['state'] == 'growing':
                    sort_name = plot['sort_name']
                    remaining = max(0, SORTS[sort_name].grow_time_ms - (pygame.time.get_ticks() - plot['plant_time']))
                    sec = remaining // 1000 + 1
                    text = font_small.render(f"{sort_name[0]} {sec}c", True, BLACK)
                    self.screen.blit(text, (rect.x+5, rect.y+5))
                elif plot['state'] == 'ready':
                    sort_name = plot['sort_name']
                    text = font_small.render(f"{sort_name[0]} ГОТОВ", True, BLACK)
                    self.screen.blit(text, (rect.x+5, rect.y+35))
                else:
                    text = font_small.render("ПУСТО", True, BLACK)
                    self.screen.blit(text, (rect.x+25, rect.y+40))

    def draw_top_panel(self):
        scores_text = font_large.render(f"Очки биохакинга: {self.farm.scores}", True, BLACK)
        self.screen.blit(scores_text, (10, 10))

    def draw_left_panel(self):
        panel_x = 10
        panel_y = 80
        title = font_medium.render("Посадка:", True, BLACK)
        self.screen.blit(title, (panel_x, panel_y))
        y_offset = panel_y + 40
        for sort_name in self.farm.purchased_sorts:
            sort = SORTS[sort_name]
            color = GREEN if self.active_sort == sort_name else GRAY
            btn_rect = pygame.Rect(panel_x, y_offset, 130, 40)
            pygame.draw.rect(self.screen, color, btn_rect)
            pygame.draw.rect(self.screen, BLACK, btn_rect, 2)
            text = font_small.render(f"{sort_name} ({sort.plant_cost})", True, BLACK)
            self.screen.blit(text, (panel_x+5, y_offset+10))
            y_offset += 50
        # Инструкция
        inst = font_small.render("Кликни по грядке", True, BLACK)
        self.screen.blit(inst, (WIDTH/2-20, 20))

    def draw_right_panel(self):
        panel_x = WIDTH - 150
        panel_y = 80
        title = font_medium.render("Биохакинг:", True, BLACK)
        self.screen.blit(title, (panel_x, panel_y))
        y_offset = panel_y + 40
        for sort_name in ["Элизиум", "Тарсикс"]:
            sort = SORTS[sort_name]
            purchased = sort_name in self.farm.purchased_sorts
            if purchased:
                color = GRAY
                text_str = f"{sort_name} (куплен)"
            else:
                color = BLUE if self.farm.scores >= sort.buy_cost else RED
                text_str = f"{sort_name} {sort.buy_cost}"
            btn_rect = pygame.Rect(panel_x, y_offset, 140, 40)
            pygame.draw.rect(self.screen, color, btn_rect)
            pygame.draw.rect(self.screen, BLACK, btn_rect, 2)
            text = font_small.render(text_str, True, BLACK)
            self.screen.blit(text, (panel_x+5, y_offset+10))
            y_offset += 50
        # Кнопка Графика

    def draw_bottom_panel(self):
        # Кнопка "Сбросить игру"
        reset_rect = pygame.Rect(10, HEIGHT-50, 150, 40)
        pygame.draw.rect(self.screen, ORANGE, reset_rect)
        pygame.draw.rect(self.screen, BLACK, reset_rect, 2)
        reset_text = font_small.render("Сбросить игру", True, BLACK)
        self.screen.blit(reset_text, (20, HEIGHT-40))
        # Кнопка "График доходов"
        graph_rect = pygame.Rect(WIDTH-160, HEIGHT-50, 150, 40)
        pygame.draw.rect(self.screen, BLUE, graph_rect)
        pygame.draw.rect(self.screen, BLACK, graph_rect, 2)
        graph_text = font_small.render("График доходов", True, BLACK)
        self.screen.blit(graph_text, (WIDTH-150, HEIGHT-35))
        return reset_rect, graph_rect

    def draw_message(self):
        if self.message and pygame.time.get_ticks() < self.message_end_time:
            text_surf = font_medium.render(self.message, True, RED)
            text_rect = text_surf.get_rect(center=(WIDTH//2, HEIGHT-20))
            self.screen.blit(text_surf, text_rect)

    def handle_click(self, pos):
        x, y = pos
        # Проверка клика по грядке
        for gx in range(COLS):
            for gy in range(ROWS):
                rect = pygame.Rect(GRID_OFFSET_X + gx * (PLOT_SIZE + PLOT_MARGIN),
                                   GRID_OFFSET_Y + gy * (PLOT_SIZE + PLOT_MARGIN),
                                   PLOT_SIZE, PLOT_SIZE)
                if rect.collidepoint(x, y):
                    plot = self.farm.plots[gx][gy]
                    if plot['state'] == 'empty':
                        if self.farm.plant(gx, gy, self.active_sort):
                            pass  # успешно
                        else:
                            # Проверка причин
                            if self.active_sort not in self.farm.purchased_sorts:
                                self.show_message("Сорт ещё не куплен")
                            elif self.farm.scores < SORTS[self.active_sort].plant_cost:
                                self.show_message("Недостаточно очков")
                            else:
                                self.show_message("Грядка занята")
                    elif plot['state'] == 'growing':
                        self.show_message("Цветок ещё не вырос")
                    elif plot['state'] == 'ready':
                        income = self.farm.harvest(gx, gy)
                        if income is not None:
                            self.show_message(f"+{income} очков", 1000)
                    return
        # Левая панель - выбор сорта
        left_x = 10
        left_y = 120
        for i, sort_name in enumerate(self.farm.purchased_sorts):
            btn_rect = pygame.Rect(left_x, left_y + i*50, 130, 40)
            if btn_rect.collidepoint(x, y):
                self.active_sort = sort_name
                return
        # Правая панель - покупка сортов
        right_x = WIDTH - 150
        right_y = 120
        for i, sort_name in enumerate(["Элизиум", "Тарсикс"]):
            btn_rect = pygame.Rect(right_x, right_y + i*50, 140, 40)
            if btn_rect.collidepoint(x, y):
                if sort_name not in self.farm.purchased_sorts:
                    if self.farm.buy_sort(sort_name):
                        self.show_message(f"Куплен {sort_name}", 1000)
                    else:
                        self.show_message("Недостаточно очков")
                else:
                    self.show_message("Уже куплен")
                return
        # Нижняя панель
        reset_rect, graph_rect = self.draw_bottom_panel()  # повторно для получения rect
        if reset_rect.collidepoint(x, y):
            self.show_confirm_reset()
        if graph_rect.collidepoint(x, y):
            self.show_graph()

    def show_confirm_reset(self):
        # Простое диалоговое окно подтверждения
        dialog_rect = pygame.Rect(WIDTH//2-150, HEIGHT//2-60, 300, 120)
        pygame.draw.rect(self.screen, WHITE, dialog_rect)
        pygame.draw.rect(self.screen, BLACK, dialog_rect, 3)
        text = font_medium.render("Сбросить игру?", True, BLACK)
        self.screen.blit(text, (WIDTH//2-100, HEIGHT//2-40))
        yes_rect = pygame.Rect(WIDTH//2-100, HEIGHT//2, 80, 40)
        no_rect = pygame.Rect(WIDTH//2+20, HEIGHT//2, 80, 40)
        pygame.draw.rect(self.screen, GREEN, yes_rect)
        pygame.draw.rect(self.screen, RED, no_rect)
        yes_text = font_small.render("Да", True, BLACK)
        no_text = font_small.render("Нет", True, BLACK)
        self.screen.blit(yes_text, (WIDTH//2-70, HEIGHT//2+10))
        self.screen.blit(no_text, (WIDTH//2+50, HEIGHT//2+10))
        pygame.display.flip()
        waiting = True
        while waiting:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False
                    return
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = ev.pos
                    if yes_rect.collidepoint(mx, my):
                        self.farm.reset_game()
                        self.active_sort = "Аресис"
                        self.show_message("Игра сброшена", 1000)
                        waiting = False
                    elif no_rect.collidepoint(mx, my):
                        waiting = False
            self.clock.tick(30)

    def show_graph(self):
        if not self.farm.income_history:
            self.show_message("Нет данных для графика", 1500)
            return
        # Генерируем график в PNG
        img_path = generate_income_graph(self.farm.income_history, "temp_plot.png")
        if not os.path.exists(img_path):
            self.show_message("Ошибка генерации графика", 1500)
            return
        # Загружаем поверхность
        graph_surf = pygame.image.load(img_path)
        graph_surf = pygame.transform.scale(graph_surf, (600, 400))
        self.showing_graph = True
        # Отображаем до нажатия Esc
        while self.showing_graph:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.showing_graph = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.showing_graph = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # можно кликнуть вне графика для закрытия
                    self.showing_graph = False
            # Рисуем игру под графиком, но не обновляем игровые действия
            self.draw_background()
            self.draw_top_panel()
            self.draw_grid()
            self.draw_left_panel()
            self.draw_right_panel()
            self.draw_bottom_panel()
            self.draw_message()
            # Накладываем график по центру
            rect = graph_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
            self.screen.blit(graph_surf, rect)
            pygame.display.flip()
            self.clock.tick(FPS)
        # Удаляем временный файл
        try:
            os.remove(img_path)
        except:
            pass

    def run(self):
        while self.running:
            # Автосохранение каждые 30 секунд
            now = pygame.time.get_ticks()
            if now - self.last_save_time >= 30000:
                self.save_current_game()
                self.last_save_time = now

            #Обновление состояния грядок
            self.farm.update_growing_plots()

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_current_game()
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and not self.showing_graph:
                    self.handle_click(event.pos)

            # Отрисовка
            self.draw_background()
            self.draw_top_panel()
            self.draw_grid()
            self.draw_left_panel()
            self.draw_right_panel()
            self.draw_bottom_panel()
            self.draw_message()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()