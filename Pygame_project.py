import pygame
import random
from os import path
import os

# инициализируем pygame
pygame.init()

# Единственный звуковой эффект в игре, это звук столкновения управляемого шарика со вражеским
# Этот звуковой эффект здесь мы и добавляем

pygame.mixer.init()
snd_dir = path.join(path.dirname('Bump.wav'), 'snd')
boom_snd = pygame.mixer.Sound(path.join(snd_dir, 'Bump.wav'))

# В этом списке будет храниться каждое время, пройденное от левой стены до правой и наоборот
records = []

# Экран
size = width, height = 1000, 500
screen = pygame.display.set_mode(size)

# Время
clock = pygame.time.Clock()

# Это надо для столкновений
all_sprites = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
Crush = pygame.sprite.Group()

# Параметры нашего шарика
BLUE = (0, 70, 225)
x = 30
y = height // 2
r = 15

# Правда ложь
first = True
kill_them_all = False
wall_1_to_wall_2 = True
wall_2_to_wall_1 = False
menu = True
enemy = False
enemy_go = False
timer_started = True
done = False
play = False

# Цвет букв
font = pygame.font.Font(None, 54)
font_color = pygame.Color('black')
second_color = pygame.Color('blue')

# Прошедшее время
passed_time = 0

# Тоже для секундомера
old_tick = 0


# Для загрузки изображений
def load_image(name, color_key=None):
    fullname = os.path.join('img', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


# Загрузка изображений
small_image = load_image("small_ball.png")
average_image = load_image("average_ball.png")
big_image = load_image("big_ball.png")
enemy_image = load_image("enemy_ball.png")


# Это класс хитбокса шарика игрока, при его столкновении с красным шариком, игрок отправляется в начало
class Hitbox(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        global x
        global y
        global r
        self.add(Crush)
        self.image = pygame.Surface((r, r), pygame.SRCALPHA, 32)
        self.rect = pygame.Rect(x, y, r, r)

    def update(self, X):
        global x
        global y
        global r
        self.rect = pygame.Rect(x, y, r, r)


# Здесь описано поведение красного шарика: в какую сторону он будет лететь изначально и после столкновения с
# поверхностью, а также именно в этом классе прописанно куда отправится игрок после столкновения с красным шариком

class Ball(pygame.sprite.Sprite):
    def __init__(self, radius, X, Y):
        super().__init__(all_sprites)
        self.radius = radius
        self.image = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("red"), (radius, radius), radius)
        self.rect = pygame.Rect(X, Y, 2 * radius, 2 * radius)
        self.vx = random.randint(-6, 6)
        self.vy = random.randint(-6, 6)

    def update(self, X):
        global x
        global y
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx
        if pygame.sprite.spritecollideany(self, Crush):
            boom_snd.play()
            print(x, y)
            if wall_1_to_wall_2:
                x = 30
                y = height // 2
            if wall_2_to_wall_1:
                x = width - 30
                y = height // 2


# Это класс шарика, который следует за тобой
class Following_Ball(pygame.sprite.Sprite):
    def __init__(self, radius, X, Y):
        super().__init__(all_sprites)
        self.radius = radius
        self.x = X
        self.y = Y
        self.radius = radius
        self.image = pygame.Surface((2 * self.radius, 2 * self.radius), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("black"), (self.radius, self.radius), self.radius)
        self.rect = pygame.Rect(self.x, self.y, 2 * self.radius, 2 * self.radius)
        self.x = X
        self.y = Y

    def update(self, X):
        global x
        global y
        global stop
        if self.x < x:
            self.x += 5
            self.rect = self.rect.move(5, 0)
        elif self.x > x:
            self.x -= 5
            self.rect = self.rect.move(-5, 0)

        if self.y < y:
            self.y += 5
            self.rect = self.rect.move(0, 5)

        elif self.y > y:
            self.y -= 5
            self.rect = self.rect.move(0, -5)

        if self.x < 60 or self.x > width - 60:
            self.x = width // 2
            self.y = height // 2
            self.rect = pygame.Rect(self.x, self.y, 2 * self.radius, 2 * self.radius)

        if pygame.sprite.spritecollideany(self, Crush):
            boom_snd.play()
            if wall_1_to_wall_2:
                x = 30
                y = height // 2
            if wall_2_to_wall_1:
                x = width - 30
                y = height // 2


# Класс стен
class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


# Собственно сами стены
Border(5, 0, width - 5, 0)
Border(10, height, width - 5, height)
Border(50, 5, 50, height - 5)
Border(width - 50, 5, width - 50, height - 5)

# Для секундомера
text = font.render(str(passed_time / 1000), True, font_color)

# Хитбокс, снизойди на этот синий шар
Hitbox()

# Задержка перед повторным собитием клавиатуры
pygame.key.set_repeat(25)

# Время со старта
start_time = pygame.time.get_ticks()

keys = pygame.key.get_pressed()

# Флаги для функций меню и основной программы
running = True
run = True


# Кнопка, которая при нажатии запускает игру
class button():
    def __init__(self, surf, x, y, width, height):
        self.x = x
        self.y = y
        self.surf = surf  # Поверхность для отрисовки
        self.width = width
        self.height = height
        self.counter = 0  # Счетчик нажатий кнопки. Зависит от clock.tick()

    def draw(self):
        global run
        global running
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if self.x < mouse[0] < self.x + self.width and self.y < mouse[1] < self.y + self.height:
            pygame.draw.rect(self.surf, (150, 150, 40), (self.x, self.y, self.width, self.height))
            if click[0] == 1:
                run = False
                running = True
                return True
            else:
                pygame.draw.rect(self.surf, (100, 100, 150), (self.x, self.y, self.width, self.height))

        else:
            pygame.draw.rect(self.surf, (100, 200, 100), (self.x, self.y, self.width, self.height))


# Просто кнопка
class button2():
    def __init__(self, surf, x, y, width, height):
        self.x = x
        self.y = y
        self.surf = surf  # Поверхность для отрисовки
        self.width = width
        self.height = height
        self.counter = 0  # Счетчик нажатий кнопки. Зависит от clock.tick()

    def draw(self):
        global run
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if self.x < mouse[0] < self.x + self.width and self.y < mouse[1] < self.y + self.height:
            pygame.draw.rect(self.surf, (150, 150, 40), (self.x, self.y, self.width, self.height))
            if click[0] == 1:
                return True
            else:
                pygame.draw.rect(self.surf, (100, 100, 150), (self.x, self.y, self.width, self.height))

        else:
            pygame.draw.rect(self.surf, (100, 200, 100), (self.x, self.y, self.width, self.height))


# Меню
def drawMenu():
    global r
    global enemy
    global enemy_go
    pygame.init()
    pygame.display.set_caption('game')
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))

    startGame = button(screen, 10, 10, 120, 60)
    textEasy = font.render('Easy', True, font_color)
    screen.blit(textEasy, (10, 70))

    startGame2 = button(screen, 330, 10, 120, 60)
    textNormal = font.render('Normal', True, font_color)
    screen.blit(textNormal, (330, 70))

    startGame3 = button(screen, 650, 10, 120, 60)
    textHard = font.render('Hard', True, font_color)
    screen.blit(textHard, (650, 70))

    Ball_size = button2(screen, 10, 300, 120, 60)
    textSmall = font.render('Small', True, font_color)
    screen.blit(small_image, (100, 300))
    screen.blit(textSmall, (10, 380))

    Ball_size2 = button2(screen, 330, 300, 120, 60)
    textAverage = font.render('Average', True, font_color)
    screen.blit(average_image, (430, 290))
    screen.blit(textAverage, (330, 380))

    Ball_size3 = button2(screen, 650, 300, 120, 60)
    textBig = font.render('Big', True, font_color)
    screen.blit(big_image, (750, 285))
    screen.blit(textBig, (650, 380))

    Follow_for_you = button2(screen, 10, 160, 120, 60)
    textFollow = font.render('Enemy', True, font_color)
    screen.blit(enemy_image, (130, 160))
    screen.blit(textFollow, (10, 220))

    Not_Follow_for_you = button2(screen, 650, 160, 120, 60)
    textNot_follow = font.render('Not enemy', True, font_color)
    screen.blit(textNot_follow, (650, 220))

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        if startGame.draw():
            for i in range(10):
                Ball(15, width // 2, 9)

            for i in range(10):
                Ball(15, width // 2, height - 30)

            for i in range(10):
                Ball(15, width // 2, height // 2)

        if startGame2.draw():
            for i in range(20):
                Ball(15, width // 2, 9)

            for i in range(20):
                Ball(15, width // 2, height - 30)

            for i in range(20):
                Ball(15, width // 2, height // 2)

        if startGame3.draw():
            for i in range(100):
                Ball(15, random.randint(60, 900), random.randint(25, 475))

        if Ball_size.draw():
            textSmall = font.render('Small', True, second_color)
            screen.blit(textSmall, (10, 380))

            textBig = font.render('Big', True, font_color)
            screen.blit(textBig, (650, 380))

            r = 5
            Hitbox()
        if Ball_size2.draw():
            textAverage = font.render('Average', True, second_color)
            screen.blit(textAverage, (330, 380))

            textSmall = font.render('Small', True, font_color)
            screen.blit(textSmall, (10, 380))

            textBig = font.render('Big', True, font_color)
            screen.blit(textBig, (650, 380))

            r = 15
            Hitbox()
        if Ball_size3.draw():
            textBig = font.render('Big', True, second_color)
            screen.blit(textBig, (650, 380))

            textAverage = font.render('Average', True, font_color)
            screen.blit(textAverage, (330, 380))

            textSmall = font.render('Small', True, font_color)
            screen.blit(textSmall, (10, 380))

            r = 25
            Hitbox()
        if Follow_for_you.draw():
            textNot_follow = font.render('Not enemy', True, font_color)
            textFollow = font.render('Enemy', True, second_color)
            screen.blit(textFollow, (10, 220))
            screen.blit(textNot_follow, (650, 220))
            enemy_go = True

        if Not_Follow_for_you.draw():
            textFollow = font.render('Enemy', True, font_color)
            textNot_follow = font.render('Not enemy', True, second_color)
            screen.blit(textFollow, (10, 220))
            screen.blit(textNot_follow, (650, 220))
            enemy_go = False

        clock.tick(20)

        pygame.display.update()


# Заппускаем меню
drawMenu()

if enemy_go:
    Following_Ball(10, random.randint(60, 900), random.randint(25, 475))

# Загружаем песню(Да не засудят меня Team meat и Дэнни Барановски)
file = f'{os.path.abspath("snd")}\Forest Funk.mp3'
pygame.mixer.music.load(file)
pygame.mixer.music.play(-1)
# Ставим эту песню на бесконечное повторение
pygame.mixer.music.set_volume(0.2)


# Основной игровой цикл
def game():
    global running
    global start_time
    global passed_time
    global x
    global y
    global wall_1_to_wall_2
    global wall_2_to_wall_1
    global first
    global text
    global run
    global enemy_go
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Движение мыши заставляет игровые объекты делать лишние действия, поэтому если у нас встречается это
            # Событие, мы пропускаем его
            if event.type != pygame.MOUSEMOTION:
                if timer_started:
                    # Определяем прошедшее время
                    passed_time = pygame.time.get_ticks() - start_time

                # Белый фон
                screen.fill(pygame.Color("white"))

                # Рисуем все объекты
                all_sprites.draw(screen)

                # Управляемый нами шарик здесь отрисовывается отдельно
                pygame.draw.circle(screen, BLUE, (x, y), r)

                # Нажатия на клавиатуру
                keys = pygame.key.get_pressed()

                # Содержит в себе координаты шарики перед следующим событием
                old_pos = (x, y)

                if wall_1_to_wall_2:
                    if x > 50:
                        if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                            text = font.render(str(passed_time / 1000), True, font_color)
                            screen.blit(text, (55, 30))
                    else:
                        start_time = pygame.time.get_ticks()

                if wall_2_to_wall_1:
                    if x < width - 50:
                        if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                            text = font.render(str(passed_time / 1000), True, font_color)
                            screen.blit(text, (55, 30))
                    else:
                        start_time = pygame.time.get_ticks()

                # Когда игрок пересекает финишную прямую(стену), время записывается в список, записывается только то время,
                # которое считалось с момента пересечения от одной стены до другой, тоесть если начать путь и вернуться,
                # это учитываться не будет

                if x == (width - 50):
                    if wall_1_to_wall_2:
                        records.append(passed_time / 1000)
                    wall_2_to_wall_1 = True
                    wall_1_to_wall_2 = False
                    first = False

                if x == 50:
                    if wall_2_to_wall_1:
                        records.append(passed_time / 1000)
                    wall_1_to_wall_2 = True
                    wall_2_to_wall_1 = False

                # Выбирается минимальное время из списка
                if first:
                    pass
                else:
                    text2 = font.render(str(min(records)), True, font_color)
                    screen.blit(text2, (width - 145, 30))

                # Перемещение
                if keys[pygame.K_UP] and keys[pygame.K_LEFT]:
                    x -= 10
                    y -= 10
                elif keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
                    x += 10
                    y -= 10

                elif keys[pygame.K_DOWN] and keys[pygame.K_LEFT]:
                    x -= 10
                    y += 10

                elif keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]:
                    x += 10
                    y += 10

                elif keys[pygame.K_LEFT]:
                    x -= 10
                elif keys[pygame.K_RIGHT]:
                    x += 10
                elif keys[pygame.K_UP]:
                    y -= 10
                elif keys[pygame.K_DOWN]:
                    y += 10
                elif keys[pygame.K_ESCAPE]:
                    run = True
                    running = False
                    drawMenu()

                # Не дает шарику уйти за пределы поля
                screen.blit(text, (55, 30))
                if x < 0:
                    x = 0
                if x > width:
                    x = width
                if y < 0:
                    y = 0
                if y > height:
                    y = height - 5

                # Если игрок не изменил своего положения, то все объекты также остаются статичными.
                # Даже течение времени секундомера зависит от движения игрока
                if (x, y) != old_pos:
                    all_sprites.update(event)

        pygame.display.flip()


game()
pygame.quit()
