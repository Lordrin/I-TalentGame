import pygame, sys, os, random

clock = pygame.time.Clock()

from pygame.locals import *

pygame.init()  # initiate pygame
pygame.font.init()
myfont = pygame.font.SysFont('calibri', 20)

pygame.display.set_caption('Pygame Window')

WIDTH_SCREEN, HEIGHT_SCREEN = 830, 720
WINDOW_SIZE = (WIDTH_SCREEN, HEIGHT_SCREEN)  # set up window size

SCREEN = pygame.display.set_mode(WINDOW_SIZE, 0, 32)

# assets
BACKGROUND = pygame.image.load(os.path.join('assets\\background', 'binnenstraat.jpg'))
GOOD_RECTANGLE = pygame.image.load(os.path.join('assets\\good_rectangles', 'good_various.png'))
GOOD_RECTANGLES = []


class Rectangle(object):
    def __init__(self, x, y, width, height):
        self.rectangle = pygame.Rect(x, y, width, height)
        self.x = self.set_x(x)
        self.y = self.set_y(y)
        self.width = width
        self.height = height
        # 0 = down, 1= left, 2 = right
        self.movement = 0
        self.speed = 1
        self.collided = False

    def draw(self, screen, colour=(0, 0, 0)):
        pygame.draw.rect(screen, colour, self.rectangle)

    def off_screen(self):
        if self.rectangle.y >= 750:
            return True
        else:
            return False

    def set_x(self, x):
        # self.rectangle.move(x, 0)
        self.x = x
        self.rectangle.left = x
        return x

    def set_y(self, y):
        # self.rectangle.move(0, y)
        self.y = y
        self.rectangle.top = y
        return y

    def collision(self, player):
        if check_collision(player.rectangle, self.rectangle):
            # player.collided = True
            return True

    def collide(self, player):
        return


class Player(Rectangle):
    def __init__(self):
        super().__init__(0, HEIGHT_SCREEN - 50, 50, 50)
        self.image = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'Player.png')), (50, 50))
        self.y_momentum = 0
        self.x_momentum = 0
        self.score = 0
        # self.collision = False

        self.jumping = False
        self.falling = False
        self.moving_left = False
        self.moving_right = False

    def jump(self):
        if self.y <= HEIGHT_SCREEN - self.image.get_height() + 20:
            self.falling = False
            self.y_momentum += 0.2
            self.set_y(self.y - self.y_momentum)
            if self.y <= 0 + self.image.get_height():
                self.y = 0 + self.image.get_height()
                self.y_momentum = 0
            if self.y_momentum >= 4.5:
                self.y_momentum = 4.5
            self.set_y(self.y - self.y_momentum)

    def fall(self):
        if self.y < HEIGHT_SCREEN - self.image.get_height():
            self.y_momentum += 0.3
            self.set_y(self.y + self.y_momentum)
            if self.y > WINDOW_SIZE[1] - self.image.get_height():
                self.y = WINDOW_SIZE[1] - self.image.get_height()
                self.y_momentum = 0
                if self.y_momentum >= 4.5:
                    self.y_momentum = 4.5
            self.set_y(self.y + self.y_momentum)

    def move_left(self):
        if self.x >= 0:
            self.x_momentum += 0.2
            self.set_x(self.x - self.x_momentum)
            if self.x <= 0:
                self.x = WIDTH_SCREEN
                self.x_momentum = 0
            if self.x_momentum >= 4.5:
                self.x_momentum = 4.5
            self.set_x(self.x - self.x_momentum)

    def move_right(self):
        if self.x >= -50:
            self.x_momentum += 0.2
            self.set_x(self.x + self.x_momentum)
            if self.x >= WIDTH_SCREEN:
                self.x = -45
                self.x_momentum = 0
            if self.x_momentum >= 4.5:
                self.x_momentum = 4.5
            self.set_x(self.x + self.x_momentum)


class BadRectangle(Rectangle):
    def __init__(self, x, y, width, height, comment="bad"):
        super().__init__(x, y, width, height)
        self.text = comment
        self.rectangle = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, speed):
        self.rectangle.move(0, self.y*speed)

    def draw(self, screen, colour=(0, 0, 0), colour_text=(255, 255, 255)):
        super().draw(screen, colour)

    def collision(self, player):
        if check_collision(player.rectangle, self.rectangle):
            player.collided = True
            self.collided = True
            return True

    def collide(self, player):
        self.draw(SCREEN, colour=(255, 0, 0))
        player.jumping = False
        player.falling = False
        player.moving_left = False
        player.moving_right = False
        if player.y < self.rectangle.y: # top
            player.set_y(player.y - player.y_momentum)
        else: # bottom
            if player.y > HEIGHT_SCREEN - player.rectangle.height - 5:
                player.set_y(player.y + self.speed)
                player.collided = True
                self.collided = True
            else:
                player.set_y(player.y + player.y_momentum)
                player.falling = True
                player.collided = False
                self.collided = False
        if player.x < self.rectangle.x: # left
            player.set_x(player.x - player.x_momentum)
        else: # right
            player.set_x(player.x + player.x_momentum)

        # smooth collision
        if player.y_momentum > 0.4:
            player.y_momentum -= 0.2
        if player.x_momentum > 0.4:
            player.x_momentum -= 0.2
        if player.y_momentum <= player.x_momentum:
            biggest = player.x_momentum
        else:
            biggest = player.y_momentum
        if biggest <= 0.4:
            player.collided = False
            self.collided = False
            player.x_momentum = 0.4
            player.y_momentum = 0.4
            return False


class GoodRectangle(Rectangle):
    def __init__(self, x, y, width, height, image, text="good"):
        super().__init__(x, y, width, height)
        self.image = pygame.transform.scale(image, (self.rectangle.width, self.rectangle.height))
        self.text = text
        self.rectangle = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen, colour=(0, 0, 0)):
        super().draw(screen, colour)
        SCREEN.blit(self.image, (self.rectangle.x, self.rectangle.y))

    def collision(self, player):
        if check_collision(player.rectangle, self.rectangle):
            return True

    def collide(self, player):
        self.rectangle.y = HEIGHT_SCREEN + self.rectangle.height + 50
        # self.draw(SCREEN, colour=(0, 255, 0))
        player.score += 1


def game_start_menu():
    running = True
    load_images()
    while running:
        SCREEN.blit(BACKGROUND, (0,0))
        title = pygame.font.SysFont("calibri", 80)
        title_label = title.render("Click to begin...", 1, (255, 255, 255))
        SCREEN.blit(title_label, (WIDTH_SCREEN / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                game_loop()
    pygame.quit()


def check_collision(player, rectangle):
    if player.colliderect(rectangle):
        return True
    else:
        return False


def load_images():
    files = os.listdir(os.path.join("assets\\good_rectangles"))
    for image in files:
        GOOD_RECTANGLES.append(pygame.image.load(os.path.join("assets\\good_rectangles", image)))


def game_loop():
    bad_rectangles = []
    good_rectangles = []
    rectangles = []
    player = Player()
    lost = False
    wave = 0
    won = False
    base_speed = 100

    def update_screen_elements():
        # SCREEN.fill((146, 244, 255))
        SCREEN.blit(BACKGROUND, (0, 0))

        wave_text = myfont.render('Wave: %.f' % wave, False, (0, 0, 0))
        SCREEN.blit(wave_text, (WIDTH_SCREEN / 2, 0))

        score_text = myfont.render('Score: %.f' % player.score, False, (0, 0, 0))
        SCREEN.blit(score_text, (WIDTH_SCREEN - 100, 0))

        # textsurface = myfont.render(
            # 'x: %.1f, y:%.1f, m: %.1f   %.1f' % (player.rectangle.x, player.rectangle.y, player.y_momentum, player.x_momentum), False, (0, 0, 0))
        # SCREEN.blit(textsurface, (0, 0))

        # text = myfont.render(
            # 'up: %s, down: %s, left: %s,right %s, c: %s' % (
            # player.jumping, player.falling, player.moving_left, player.moving_right, player.collided), False, (0, 0, 0))
        # SCREEN.blit(text, (0, 40))

        SCREEN.blit(player.image, (player.x, player.y))



        if lost:
            lost_font = pygame.font.SysFont('calibri', 90)
            lost_label = lost_font.render("You Lost!!", 1, (255, 0, 0))
            SCREEN.blit(lost_label, (WIDTH_SCREEN / 2 - lost_label.get_width() / 2, 350))
        if won:
            won_font = pygame.font.SysFont('calibri', 90)
            won_label = won_font.render("You Won!!", 1, (0, 255, 0))
            SCREEN.blit(won_label, (WIDTH_SCREEN / 2 - won_label.get_width() / 2, 350))
        else:
            for rectangle in rectangles:
                if rectangle.collision(player):
                    player.collided = True
                    rectangle.collided = True
                else:
                    rectangle.draw(SCREEN)
                    # player.collision = False
                if player.collided is True and rectangle.collided is True:
                    rectangle.collide(player)
                if rectangle.off_screen():
                    rectangles.remove(rectangle)
                    continue
                rectangle.rectangle.top += rectangle.speed
                if rectangle.movement == 1:
                    rectangle.rectangle.left -= rectangle.speed
                    if rectangle.rectangle.left <= 0:
                        rectangle.movement = 2
                        rectangle.speed += 1
                elif rectangle.movement == 2:
                    rectangle.rectangle.left += rectangle.speed
                    if rectangle.rectangle.left >= WIDTH_SCREEN - rectangle.width:
                        rectangle.movement = 1
                        rectangle.speed += 1
                rectangle.speed += 0.01

    while True:  # game loop
        clock.tick(60)

        if player.y > HEIGHT_SCREEN - player.image.get_height() + 15 or player.y < 0 - player.image.get_width():
            lost = True

        if player.score > 24:
            won = True
        update_screen_elements()
        pygame.display.update()

        if len(rectangles) == 0:
            wave += 1
            for i in range(wave):
                bad_rectangle = BadRectangle(random.randrange(0, WIDTH_SCREEN), 0, random.randrange(50, 201), random.randrange(25, 75))
                bad_rectangle.movement = random.randrange(0, 3, 1)
                if wave % 10 == 0:
                    base_speed += 10
                bad_rectangle.speed = random.randrange(base_speed, base_speed*10) / 1000
                bad_rectangles.append(bad_rectangle)
                if random.randrange(0,10) < 2:
                    good_rectangle = GoodRectangle(random.randrange(0, WIDTH_SCREEN), 0, 65, 65, GOOD_RECTANGLES[random.randrange(0, len(GOOD_RECTANGLES))])
                    good_rectangle.speed = random.randrange(base_speed, base_speed*10) / 1000
                    good_rectangles.append(good_rectangle)
            rectangles = bad_rectangles + good_rectangles

        if not lost:
            if player.jumping is False and player.falling is False and player.collided is False:
                player.y_momentum = 0.4
            if player.jumping is True and player.falling is True and player.collided is False:
                player.y_momentum = 0.4

            if player.moving_left is False and player.moving_right is False and player.collided is False:
                player.x_momentum = 0.4

            if player.jumping is True:
                player.jump()

            if player.falling is True:
                player.fall()

            if player.moving_right is True:
                player.move_right()

            if player.moving_left is True:
                player.move_left()

        for event in pygame.event.get():  # event loop
            if event.type == QUIT:  # check for window quit
                pygame.quit()  # stop pygame
                sys.exit()  # stop script
            if event.type == KEYDOWN:
                if event.key == K_RIGHT or event.key == K_d:
                    player.moving_right = True
                if event.key == K_LEFT or event.key == K_a:
                    player.moving_left = True
                if event.key == K_SPACE or event.key == K_UP or event.key == K_w:
                    player.jumping = True
                if event.key == K_LCTRL or event.key == K_DOWN or event.key == K_s:
                    player.falling = True
            if event.type == KEYUP:
                if event.key == K_RIGHT or event.key == K_d:
                    player.moving_right = False
                if event.key == K_LEFT or event.key == K_a:
                    player.moving_left = False
                if event.key == K_SPACE or event.key == K_UP or event.key == K_w:
                    player.jumping = False
                if event.key == K_LCTRL or event.key == K_DOWN or event.key == K_s:
                    player.falling = False
            if lost:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    game_start_menu()


game_start_menu()
