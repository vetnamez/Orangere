import pygame

#Класс сортировки сортов
class FlowerSort:
    def __init__(self, name, buy_cost, plant_cost, harvest_income, grow_time_sec):
        self.name = name
        self.buy_cost = buy_cost
        self.plant_cost = plant_cost
        self.harvest_income = harvest_income
        self.grow_time_ms = grow_time_sec * 1000

# Предопределённые сорта
SORTS = {
    "Аресис": FlowerSort("Аресис", 0, 10, 20, 15),
    "Элизиум": FlowerSort("Элизиум", 100, 30, 70, 30),
    "Тарсикс": FlowerSort("Тарсикс", 250, 50, 150, 45)
}

class Farm:
    def __init__(self):
        self.scores = 100
        self.purchased_sorts = ["Аресис"]
        self.plots = [[{'state': 'empty', 'sort_name': None, 'plant_time': None} for _ in range(4)] for _ in range(4)]
        self.income_history = []  # максимум 20 элементов

    #Проверка на возможность посадки
    def can_plant(self, plot_x, plot_y, sort_name):
        if not (0 <= plot_x < 4 and 0 <= plot_y < 4):
            return False
        if self.plots[plot_x][plot_y]['state'] != 'empty':
            return False
        if sort_name not in self.purchased_sorts:
            return False
        if self.scores < SORTS[sort_name].plant_cost:
            return False
        return True
    #Функция посадки
    def plant(self, plot_x, plot_y, sort_name):
        if not self.can_plant(plot_x, plot_y, sort_name):
            return False
        sort = SORTS[sort_name]
        self.scores -= sort.plant_cost
        self.plots[plot_x][plot_y] = {
            'state': 'growing',
            'sort_name': sort_name,
            'plant_time': pygame.time.get_ticks()
        }
        return True
    #Проверка возможности сбора
    def can_harvest(self, plot_x, plot_y):
        if not (0 <= plot_x < 4 and 0 <= plot_y < 4):
            return False
        plot = self.plots[plot_x][plot_y]
        if plot['state'] != 'ready':
            return False
        return True
    #Функция сбора
    def harvest(self, plot_x, plot_y):
        if not self.can_harvest(plot_x, plot_y):
            return None
        plot = self.plots[plot_x][plot_y]
        sort = SORTS[plot['sort_name']]
        income = sort.harvest_income
        self.scores += income
        self.income_history.append(income)
        if len(self.income_history) > 20:
            self.income_history.pop(0)
        self.plots[plot_x][plot_y] = {'state': 'empty', 'sort_name': None, 'plant_time': None}
        return income

    def buy_sort(self, sort_name):
        if sort_name in self.purchased_sorts:
            return False
        sort = SORTS[sort_name]
        if self.scores >= sort.buy_cost:
            self.scores -= sort.buy_cost
            self.purchased_sorts.append(sort_name)
            return True
        return False

    def update_growing_plots(self):
        current_time = pygame.time.get_ticks()
        for x in range(4):
            for y in range(4):
                plot = self.plots[x][y]
                if plot['state'] == 'growing':
                    sort = SORTS[plot['sort_name']]
                    if current_time - plot['plant_time'] >= sort.grow_time_ms:
                        plot['state'] = 'ready'
    #Сброс игры
    def reset_game(self):
        self.__init__()

    def get_state_for_save(self):
        # Сохраняем состояние грядок (оставляем только необходимые данные)
        plots_data = []
        for x in range(4):
            row = []
            for y in range(4):
                p = self.plots[x][y]
                if p['state'] == 'empty':
                    row.append({'state': 'empty'})
                elif p['state'] == 'growing':
                    row.append({
                        'state': 'growing',
                        'sort_name': p['sort_name'],
                        'plant_time': p['plant_time']
                    })
                else:  # ready
                    row.append({
                        'state': 'ready',
                        'sort_name': p['sort_name'],
                        'plant_time': p['plant_time']
                    })
            plots_data.append(row)
        return {
            'scores': self.scores,
            'purchased_sorts': self.purchased_sorts,
            'plots': plots_data,
            'income_history': self.income_history
        }

    def load_from_state(self, state):
        self.scores = state['scores']
        self.purchased_sorts = state['purchased_sorts']
        self.income_history = state['income_history']
        # Восстановление грядок
        for x in range(4):
            for y in range(4):
                p = state['plots'][x][y]
                if p['state'] == 'empty':
                    self.plots[x][y] = {'state': 'empty', 'sort_name': None, 'plant_time': None}
                elif p['state'] == 'growing':
                    self.plots[x][y] = {
                        'state': 'growing',
                        'sort_name': p['sort_name'],
                        'plant_time': p['plant_time']
                    }
                else:  # ready
                    self.plots[x][y] = {
                        'state': 'ready',
                        'sort_name': p['sort_name'],
                        'plant_time': p['plant_time']
                    }