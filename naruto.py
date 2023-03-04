import pygame
import numpy as np
from pygame.transform import rotozoom, flip
from tool import get_img, form

# initialize
size = width, height = 1425, 513
win = pygame.display.set_mode(size)
bg = rotozoom(pygame.image.load('./naruto/background.png').convert(), 0, 1)
win.fill((255, 255, 255))
win.blit(bg, (0, 0))
pygame.display.update()

pygame.mixer.init(buffer=128)
pygame.init()
clock = pygame.time.Clock()

# Load images
rGuard = get_img('Guard')
lGuard = get_img('Guard', isflip=True)
rCannon = get_img('EnergyCannon', mag=0.6)
lCannon = get_img('EnergyCannon', mag=0.6, isflip=True)

RunRight = get_img('Run', num=6, ang=-1)
RunLeft = get_img('Run', num=6, ang=1, isflip=True)
IdleRight = get_img('Idle', num=6)
IdleLeft = get_img('Idle', num=6, isflip=True)
JumpRight = get_img('Jump', num=6)
JumpLeft = get_img('Jump', num=6, isflip=True)
AttackRight = get_img('Attack', num=7)
AttackLeft = get_img('Attack', num=7, isflip=True)
EnergyRight = get_img('Energy', num=6)
EnergyLeft = get_img('Energy', num=6, isflip=True)
FoxRight = get_img('Fox', num=6)
FoxLeft = get_img('Fox', num=6, isflip=True)
DownRight = get_img('Down', num=6)
DownLeft = get_img('Down', num=6, isflip=True)
quake = get_img('Quake', num=3)
RStrongAttack = get_img('StrongAttack', num=7)
LStrongAttack = get_img('StrongAttack', num=7, isflip=True)

vel = 6  # running velocity of naruto
x, y = 50, 245
head = 'Right'
dy = [-20, -120, -214, -214, -120, -20]
skillList = ['idle', 'run', 'jump', 'guard', 'down', 'attack', 'strong', 'energy', 'fox']
maxFrame  = [  6,      6,     6,       1,      6,        7,       7,        6,       6]
durFrame  = [  4,      4,     6,    None,      7,        3,       5,        6,       7]
countList = [  0,      0,     0,    None,      0,        0,       0,        0,       0]
adx       = [  0,      0,    35,       0,      0,        0,       0,        0,       0]
ady       = [  4,     22,  None,      -8,    -36,        4,     -25,       -8,     -40]
skillState = [True, False, False,  False,  False,    False,   False,    False,   False]
skillKey = [None, None, pygame.K_SPACE, pygame.K_UP, pygame.K_DOWN, pygame.K_a, pygame.K_f, pygame.K_s, pygame.K_d]
skillNum = len(skillList)

skillMotion = [[IdleRight, IdleLeft], [RunRight, RunLeft],
               [JumpRight, JumpLeft], [rGuard, lGuard],
               [DownRight, DownLeft], [AttackRight, AttackLeft],
               [RStrongAttack, LStrongAttack], [EnergyRight, EnergyLeft],
               [FoxRight, FoxLeft]]

# numpy array for determining hit zone
area = np.zeros(shape=(width, height))
hit_effect = pygame.mixer.Sound('./scarecrow.wav')
hit_delay = False

# Cannon parameter
xlist, ylist, hlist = [], [], []
speed = 7
buffer = 0


def count(str):
    return countList[skillList.index(str)]


def state(str):
    return skillState[skillList.index(str)]


def frame(str):
    return durFrame[skillList.index(str)]


def add(xx, yy, pos):
    xlist.append(xx)
    ylist.append(yy)
    hlist.append(pos)


def scarecrow():
    crow = rotozoom(pygame.image.load('./naruto/scarecrow.png'), 0, 1.7)
    win.blit(crow, (width/2+50, 255))


def status_check():
    global skillState, countList
    global x, y, head, hit_delay

    #   skillList = ['idle', 'run', 'jump', 'guard', 'down', 'attack', 'strong', 'energy', 'fox']
    keys = pygame.key.get_pressed()
    pressState = [keys[item] for item in skillKey if item is not None]

    # 가드 풀어
    if not pressState[3-2]:
        skillState[3] = False
    
    # x축 이동
    if sum(skillState[3:]) == 0:
        if keys[pygame.K_RIGHT]:
            head = 'Right'
            x += vel
            x = form(x)
        elif keys[pygame.K_LEFT]:
            head = 'Left'
            x -= vel
            x = form(x)

    # Fox에 의한 이동
    if head == 'Right':
        x = form(x + count('fox') * 0.38)
    else:
        x = form(x - count('fox') * 0.38)

    if sum(skillState [2:]) == 0:
        # 우측 이동
        if keys[pygame.K_RIGHT]:
            hit_delay = False
            skillState[0] = False
            skillState[1] = True
        # 좌측 이동
        elif keys[pygame.K_LEFT]:
            hit_delay = False
            skillState[0] = False
            skillState[1] = True
        # 완전 정지
        else:
            skillState[0] = True
            skillState[1] = False
            countList[1] = 0
            hit_delay = False

    # 가만히 있거나, 달리고 있거나, 스트레이트라면 다른 공격 가능
    # 단, 스트레이트 도중 달릴 수는 없음
    if state('idle') or state('run') or state('attack'):
        for idx in range(2, skillNum):
            if pressState[idx-2]:
                skillState = [False] * skillNum
                skillState[idx] = True
                countList[1] = 0
                if not skillState[5]:
                    countList[5] = 0
                break


def finish_move():
    global hit_delay, skillState, countList

    # 프레임을 처음으로 되돌림
    for idx in range(skillNum):
        if durFrame[idx] is not None and countList[idx] >= maxFrame[idx] * durFrame[idx]:
            countList[idx] = 0
            skillState[idx] = False
            hit_delay = False

    if skillState == [False] * skillNum:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT]:
            skillState[1] = True
        else:
            skillState[0] = True

    if count('energy') == 4 * frame('energy'):
        if head == 'Right':
            add(x+258, y+13, 1)
        else:
            add(x-78, y+13, -1)


def draw_character():
    global countList

    # 상태 체크 + 캐릭터 그리기
    if sum(skillState) > 1:
        raise AssertionError

    for idx in range(skillNum):
        pos = 0 if head == 'Right' else 1
        if skillState[idx]:
            if durFrame[idx] is None:
                win.blit(skillMotion[idx][pos], (x+adx[idx], y+ady[idx]))
            else:
                cframe = countList[idx]//durFrame[idx]
                if ady[idx] is not None:
                    win.blit(skillMotion[idx][pos][cframe], (x+adx[idx], y+ady[idx]))
                elif state('jump'):
                    win.blit(skillMotion[idx][pos][cframe], (x+adx[idx], y+dy[cframe]))
                else:
                    raise AssertionError
                countList[idx] += 1

    if (count('down')-1) >= 3 * frame('down'):
        win.blit(quake[((count('down')-1)//frame('down'))-3], (x-150, y+105))


def draw_cannon():
    delList = []
    for idx in range(len(xlist)):
        xlist[idx] = xlist[idx] + speed * hlist[idx]
        xx, yy = xlist[idx], ylist[idx]
        area[xx+30:xx+30+speed, yy+41:yy+92] = 2
        if xlist[idx] > width + 150 or xlist[idx] < -150:
            delList.append(idx)

        if hlist[idx] == 1:
            win.blit(rCannon, (xlist[idx], ylist[idx]))
        else:
            win.blit(lCannon, (xlist[idx], ylist[idx]))

    for idx in delList:
        del xlist[idx]
        del ylist[idx]
        del hlist[idx]


def check_mouse():
    global x, y
    jumpFrame = (count('jump')-1)//frame('jump')
    mouse = pygame.mouse.get_pos()
    font = pygame.font.Font('Noto-Black.otf', 30)
    text = font.render("mouse: ({}, {})".format(mouse[0], mouse[1]), True, (28, 28, 0))
    if state('jump'):
        text2 = font.render("character: ({}, {})".format(x, y+dy[jumpFrame]), True, (28, 28, 0))
    else:
        text2 = font.render("character: ({}, {})".format(x, y), True, (28, 28, 0))
    text3 = font.render("{:+}, {:+}".format(mouse[0]-x, mouse[1]-y), True, (28, 28, 0))
    win.blit(text, (50, 80))
    win.blit(text2, (50, 40))
    win.blit(text3, (50, 120))


def fill_rect(a, b, c, d):
    global area
    area[x+a:x+b, y+c:y+d] = 1


def hit_zone():
    if state('attack'):
        if count('attack')//frame('attack') in [1, 2, 4, 5]:
            if head == 'Right':
                fill_rect(184, 267, 82, 100)
            else:
                fill_rect(11, 94, 82, 100)
    if state('strong'):
        if count('strong')//frame('strong') > 2:
            if head == 'Right':
                fill_rect(184, 257, 69, 137)
            else:
                fill_rect(16, 89, 69, 137)
    if state('down'):
        if (count('down')//frame('down'))-3 >= 0:
            fill_rect(-130, 400, 129, 212)
    if state('fox'):
        if count('fox')//frame('fox') in [1, 2, 3, 4]:
            if head == 'Right':
                fill_rect(214, 421, 21, 166)
            else:
                fill_rect(-90, 117, 21, 166)


def hit_enemy():
    global hit_delay, buffer
    temp = area[778:969, 287:459]
    s = temp.shape[0]//4
    temp_sect = np.stack((temp[s-20], temp[s*2-20], temp[s*3-20], temp[s*4-20]), axis=0)
    if np.max(temp_sect) == 2:
        hit_effect.play()
        if buffer == 0:
            buffer = 4
        area[area == 2] = 0
    elif np.max(temp) == 1:
        font = pygame.font.Font('Noto-Black.otf', 20)
        text = font.render("Hit!", True, (28, 28, 0))
        win.blit(text, (850, 230))
        if state('attack'):
            if count('attack') == 2 * frame('attack') + 1 or count('attack') == 5 * frame('attack') + 1:
                hit_effect.play()
        elif hit_delay is False:
            hit_effect.play()
            hit_delay = True

    if count('fox') % 8 == 1:
        hit_delay = False


def hit_message():
    global buffer
    if buffer != 0:
        font = pygame.font.Font('Noto-Black.otf', 20)
        text = font.render("Hit!", True, (28, 28, 0))
        win.blit(text, (850, 230))
        buffer -= 1


def redraw():
    global area
    win.blit(bg, (0, 0))
    area = np.zeros(shape=(width, height))

    scarecrow()
    status_check()
    finish_move()
    draw_character()
    draw_cannon()


run = True

while run:
    clock.tick(48)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    redraw()
    check_mouse()
    hit_zone()
    hit_enemy()
    hit_message()
    pygame.display.update()


pygame.quit()
