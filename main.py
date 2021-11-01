import pygame
import sys

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("CACmusic.mp3")

title = "Enduring Cavern: Exponential"
width = 800.
heigt = 450.
fps = 15
grid = 0  # I don't know what this actually lol
vol = 0.5

# controls: asdw
A = pygame.K_a
D = pygame.K_d
W = pygame.K_w
S = pygame.K_s
# controls: arrow keys
Aa = pygame.K_LEFT
Da = pygame.K_RIGHT
Wa = pygame.K_UP
Sa = pygame.K_DOWN
# control: space
Space = pygame.K_SPACE


def loadI(f, w=width, h=heigt):  # image loader; f = file path; w = width; h = heigt
    i = pygame.image.load(f)
    i = pygame.transform.scale(i, (w, h))
    return i


class Entity(pygame.sprite.Sprite):

    def __init__(self, x0, y0, f0, sc):  # x0 = initial x; y0 = initial y; f0 = initial frame; sc = scene
        super().__init__()

        self.x = x0  # initial x-value
        self.y = y0  # initial y-value
        self.m = 0  # initial movement speed
        self.f = f0  # initial frame
        self.sc = sc  # scene


bs = heigt / 9
box = [loadI("box/0.png", bs, bs), loadI("box/0.png", bs, bs), loadI("box/1.png", bs, bs), loadI("box/1.png", bs, bs),
       loadI("box/2.png", bs, bs), loadI("box/2.png", bs, bs), loadI("box/3.png", bs, bs), loadI("box/3.png", bs, bs),
       loadI("box/4.png", bs, bs), loadI("box/4.png", bs, bs)]


class Box(Entity):

    def __init__(self, x0, y0, sc):  # x0 = initial x; y0 = initial y; sc = scene
        super().__init__(x0, y0 - bs, box[0], sc)
        self.fl = box
        self.fi = 0


sqm = 5
sqw = int(width / sqm)
sqh = int(heigt / sqm)
sqf = [[loadI("idl/0.png", sqw, sqh),  # frames for idle animation
        loadI("run/0.png", sqw, sqh), loadI("run/1.png", sqw, sqh),
        loadI("run/2.png", sqw, sqh), loadI("run/3.png", sqw, sqh),
        loadI("run/4.png", sqw, sqh),
        loadI("pan/box.png", sqw, sqh), loadI("pan/stg.png", sqw, sqh)]]


# add to the list with a turn around frame and panel click frames


class Squirrel(Entity):

    def __init__(self, x0, y0, sc):  # x0 = initial x value, y0 = initial y value, sc = Scene object
        super().__init__(x0, y0, sqf[0][0], sc)

        self.fl = sqf  # frame lists
        self.fl.append([pygame.transform.flip(i, True, False) for i in self.fl[0]])  # add flipped frame list
        self.hd = 0  # head direction; really just the list of self.fl the squirrel is using
        self.r = self.fl[self.hd][0].get_rect()  # all values inside will be pre-determined based upon the maximum
        # squirrel size; also heigt doesn't matter since there will be no heigt collision; the size of just any photo
        # should fit all the squirrels, but I can double check here for polish; I made the photo sizes already when
        # I loaded them - go back there to actually change the size
        self.r.x = x0  # x value
        self.r.bottom = y0  # y value
        self.f = self.fl[self.hd][0]  # current frame

        self.sta = "idl"  # state of squirrel: either "idl", "run", "pan1", "pan2", or "pan3"; difference between this
        # and self.pan is that this is the squirrel actually doing it, compared to the buffer command being initiated
        self.pan = 0  # click panel condition: if pan = 0, no panel buffer; if pan = 1, block panel buffer; if pan = 2,
        # stage translate panel buffer; if pan = 3, stage shift panel buffer
        self.pann = 0

        if not self.sc.c:
            self.dr = self.sc.dr
        else:
            self.dr = 2 * width

    def action(self, prs):  # prs = pressed buttons list
        if self.f in self.fl[0]:
            self.hd = 0
        elif self.f in self.fl[1]:  # The 1 index is just a backup in case I create a 2 index
            # Replace with a buffer frame between turn-around
            self.hd = 1

        if prs[S] or prs[Sa] and self.pan < 2:
            self.pan = 2

        elif prs[W] or prs[Wa] and self.pan < 1:
            self.pan = 1

        # if self.pan == 3 and self.sta == "idl":  # check for panel task being 3 and squirrel state being idle
        #     # click panel for shift stage; keep self.pan = 3 until it is the last frame
        #     pass
        # elif self.pan == 3 and self.sta == "pan3":  # check for panel task being 3 and squirrel state being clicking
        #     # panel 3
        #     pass

        elif self.pan == 2 and self.sta == "idl":  # check for panel task being 2 and squirrel state being idle
            # click panel for check if stage is correct; keep self.pan = 2 until it is the last frame
            if self.pann < 3:
                self.f = self.fl[self.hd][7]
                self.pann += 1
            else:
                self.pann = 0
                self.sta = "pan2"
        elif self.pan == 2 and self.sta == "pan2":  # check for panel task being 2 and squirrel state being clicking
            # panel 2
            self.f = self.fl[self.hd][0]
            self.sc.down(self)
            self.pan = 0
            self.sta = "idl"

        elif self.pan == 1 and self.sta == "idl":  # check for panel task being 1 and squirrel state being idle
            # click panel for add box; keep self.pan = 1 until it is the last frame
            if self.pann < 1:
                self.f = self.fl[self.hd][6]
                self.pann += 1
            else:
                self.pann = 0
                self.sta = "pan1"
        elif self.pan == 1 and self.sta == "pan1":  # check for panel task being 1 and squirrel state being clicking
            # panel 1
            self.f = self.fl[self.hd][0]
            self.sc.up(self.r, self.hd)
            self.pan = 0
            self.sta = "idl"

        elif (prs[A] or prs[Aa]) and (prs[D] or prs[Da]):
            if self.hd == 0:
                self.movement("0", 0, 0, 1)
            elif self.hd == 1:
                self.movement("0", 1, 1, 1)

        elif prs[D] or prs[Da]:
            if self.hd == 0:
                self.movement("+", 0, 0)
            elif self.hd == 1:  # The 1 index is just a backup in case I create a 2 index
                # Replace with a buffer frame between turn-around
                self.movement("+", 1, 0)

        elif prs[A] or prs[Aa]:
            if self.hd == 0:
                self.movement("-", 0, 1)
            elif self.hd == 1:  # The 0 index is just a backup in case I create a 2 index
                # Replace with buffer frame between turn-around
                self.movement("-", 1, 1)

        else:
            if self.hd == 0:
                self.movement("0", 0, 0, 0)
            elif self.hd == 1:
                self.movement("0", 1, 1, 0)

    def movement(self, d, lo, ld, r=100):  # d = direction; lo = frame list original index;
        # ld = frame list desired index; m = movement boolean; r = resting frame
        # remove m for a d option of 0
        i = self.fl[lo].index(self.f)  # i = index of frame in frame list
        ur = False  # use r boolean

        if r == 100:  # if there was no imputed resting frame
            ur = True  # make ur true so that animation will repeatedly loop
            r = 1  # when loop resets, it goes back to frame 1

        if d == "+":
            if self.m == -40:
                self.m = -10
            elif self.m == -20:
                self.m = -5
            elif self.m == -10:
                self.m = 0
            elif self.m == -5:
                self.m = 5
            elif self.m == 0:
                self.m = 5
            elif self.m == 5 or self.m == 10 or self.m == 20:
                self.m *= 2

            self.move(lo, ld, r, ur, i)

        elif d == "-":
            if self.m == 40:
                self.m = 10
            elif self.m == 20:
                self.m = 5
            elif self.m == 10:
                self.m = 0
            elif self.m == 5:
                self.m = -5
            elif self.m == 0:
                self.m = -5
            elif self.m == -5 or self.m == -10 or self.m == -20:
                self.m *= 2

            self.move(lo, ld, r, ur, i)

        elif d == "0":
            if abs(self.m) == 40 or abs(self.m) == 20 or abs(self.m) == 10:
                self.m /= 2
            elif abs(self.m) == 5:
                self.m = 0

            self.move(lo, ld, r, ur, i)

    def move(self, lo, ld, r, ur, i):
        if i == 5:
            if self.r.right + self.m >= self.dr and self.m > 0:
                self.r.right = self.dr
                self.m = 0
            # elif self.r.x + self.m <= 0 and self.m < 0:
            #     self.r.x = 0
            #     self.m = 0
            else:
                self.r.x += self.m
            self.f = self.fl[ld][r]
            i = r

        elif r == 0 and i == 1:
            self.f = self.fl[ld][r]
            i = r

        elif i != r or ur and not (self.m >= 0 and self.r.right == self.dr):
            # or (self.m < 0 and self.r.x + self.m < 0 and self.r.x == 0)):
            if i == 0 or i == 1:
                self.f = self.fl[ld][i + 1]
            else:
                self.f = self.fl[lo][i + 1]
            i = i + 1

            if self.r.right + self.m >= self.dr and self.m > 0:
                self.r.right = self.dr
                self.m = 0
            # elif self.r.x + self.m <= 0 and self.m < 0:
            #     self.r.x = 0
            #     self.m = 0
            else:
                self.r.x += self.m

        if 1 < i < 6:  # outer bounds of run frames; change as I go
            self.sta = "run"  # state set to run
        elif i < 2:  # idle frames
            self.sta = "idl"  # state set to idle


class Scene:

    def __init__(self):
        self.l0 = pygame.Surface([width, heigt], pygame.SRCALPHA, 32)  # box layer to put behind box areas
        self.l1 = pygame.Surface([width, heigt], pygame.SRCALPHA, 32)  # background layer
        self.l2 = pygame.Surface([width, heigt], pygame.SRCALPHA, 32)  # squirrel layer
        self.l3 = pygame.Surface([width, heigt], pygame.SRCALPHA, 32)  # overlapping layer for ground and door

    def up(self, sqR, sqHD):  # action from upwards click; sqR = squirrel rectangle; sqHd = squirrel head direction
        pass

    def down(self, sq):  # action from downwards click; sq = squirrel
        pass


flrHt = int(5 * heigt / 6)
mmf1 = loadI("mainmenu/1.png")
mmf3 = loadI("mainmenu/3.png", width, heigt * 389./2153)


class MainMenu(Scene):

    def __init__(self):
        Scene.__init__(self)
        self.c = True
        self.dr = width * 2

    def up(self, sqR, sqHD):  # increases volume; sqR = squirrel rectangle; sqHd = squirrel head direction
        global vol
        if vol < 1:
            vol += .1
        elif vol < 1 and vol + .1 < 0:
            vol = 0

    def down(self, sq):  # decreases volume; sq = squirrel
        global vol
        if vol - .1 > 0:
            vol -= .1
        elif vol > 0 and vol - .1 < 0:
            vol = 0

    def updt(self, sq):
        self.l1.blit(mmf1, [0, 0])  # clear layer 3
        self.l3.blit(mmf3, [0, heigt - (heigt * 389./2153)])
        pygame.draw.rect(self.l3, (20, 20, 20), pygame.Rect(width - (width / (16./3) * (9./8)) + width / (20./3) * (vol + .09),
                                                            heigt - heigt / 6 + heigt / 20,
                                                            width / (20./3) * .1,
                                                            heigt / 6 - heigt / 15))
        self.l2.fill((255, 255, 255, 0))
        self.l2.blit(sq.f, [sq.r.x, sq.r.y])  # place squirrel on layer


# class LevelSelect(Scene):

#     def __init__(self):
#         Scene.__init__(self)
#         self.t = False  # t = transformed boolean - I don't know if I'm going to use it, but I could
#         self.b = pygame.sprite.Group()  # b = block sprite group

#     def upAction(self):  # enters level
#         pass

#     def downAction(self):  # returns to MainMenu
#         pass

#     def addBox(self, sqR, sqHd):  # adds box
#         pass

#     def update(self, sq):
#         for b in self.b:  # loop through boxes
#             self.l0.blit(b.f, [b.x, b.y])  # places boxes on screen
#         self.l2.fill((255, 255, 255, 0))  # clear layer 3
#         self.l2.blit(sq.f, [sq.r.x, sq.r.y])  # place squirrel on layer


stf = [[
    [loadI("stage1/part1/0.png"), loadI("stage1/part1/1.png"),
     loadI("stage1/part1/3.png", width, int(heigt * (424. / 2128))), int(heigt - heigt * (424. / 2128)),
     [[width / (16./3) * (2 + 3. / 8 - 1./20), 0,
       width / (16./3) * (2 + 3. / 4 - 1./20), heigt - heigt / 3 * (5. / 8 + 1./37),
       3, 0]], [3], round(width - width / (5 + 1. / 3) / 12),
     [loadI("stage1/part1/0.png"), loadI("stage1/part1/f1.png", width * (68./3783), heigt * (707./2128)),
      loadI("stage1/part1/f3.png", width * (78./3783), heigt * (697./2128)),
      loadI("stage1/part1/f3.png", width * (78./3783), heigt * (697./2128))],
     [0, width * (68./3783), width * (78./3783), width * (78./3783)]],

    [loadI("stage1/part2/0.png"), loadI("stage1/part2/1.png"),
     loadI("stage1/part2/3.png", width, heigt * (422. / 2132)), int(heigt - heigt * (422. / 2132)),
     [[width / (16./3) * (2 + 3. / 8) - bs, 0,
       width / (16./3) * (2 + 3. / 8), heigt - heigt / 3 * (5. / 8 + 1./38),
       3, 0],
      [width / (16./3) * (2 + 3. / 8), 0,
       width / (16./3) * (2 + 3. / 8) + bs, heigt - heigt / 3 * (5. / 8 + 1./38),
       3, 0],
      [width / (16./3) * (2 + 3. / 8) + bs, 0,
       width / (16./3) * (2 + 3. / 8) + 2 * bs, heigt - heigt / 3 * (5. / 8 + 1./38),
       3, 0]], [3, 3, 3], round(width - width / (5 + 1. / 3) / 9),
     [loadI("stage1/part2/0.png"), loadI("stage1/part2/f1.png", width * (72./3791), heigt * (719./2132)),
      loadI("stage1/part2/f2.png", width * (50./3783), heigt * (693./2128)),
      loadI("stage1/part2/f3.png", width * (81./3783), heigt * (708./2128))],
     [0, width * (72./3791), width * (50./3783), width * (81./3783)]],

    [loadI("stage1/part3/0.png"), loadI("stage1/part3/1.png"),
     loadI("stage1/part3/3.png", width, heigt * (402. / 2103)), int(heigt - heigt * (402. / 2103)),
     [[width / (16./3) * (3 + 7. / 8 + 1./30), 0,
       width / (16./3) * (3 + 7. / 8 + 1./30) + bs, heigt - heigt / 3 * (11./16),
       3, 0],
      [width / (16./3) * (3 + 7. / 8 + 1./30) + bs, 0,
       width / (16./3) * (3 + 7. / 8 + 1./30) + 2 * bs, heigt - heigt / 3 * (11./16),
       3, 0],
      [width / (16./3) * (3 + 7. / 8 + 1./30) + 2 * bs, 0,
       width / (16./3) * (4 + 7. / 8 + 1./30), heigt - heigt / 3 * (11./16),
       3, 0]], [3, 3, 3], round(width - width / (5 + 1. / 3) / 9),
     [loadI("stage1/part3/0.png"), loadI("stage1/part3/f1.png", width * (72./3738), heigt * (708./2102)),
      loadI("stage1/part3/f2.png", width * (64./3738), heigt * (722./2102)),
      loadI("stage1/part3/f3.png", width * (99./3738), heigt * (721./2102))],
     [0, width * (72./3738), width * (64./3738), width * (99./3738)]],

     [loadI("stage1/part4/0.png"), loadI("stage1/part4/0.png"),
      loadI("stage1/part4/3.png"), 0,
      [[width / (16./3) * (2 + 3. / 8 - 1./20), 0,
        width / (16./3) * (2 + 3. / 4 - 1./20), heigt - heigt / 3 * (5. / 8 + 1./37),
        0, 0]], [0], round(width - width / (5 + 1. / 3) / 12),
     [loadI("stage1/part4/0.png"), loadI("stage1/part4/f1.png", width * ((1634.-766)/3738), heigt * ((1220-566.)/2102)),
      loadI("stage1/part4/f2.png", width * ((1634.-766)/3738), heigt * ((1220-566.)/2102)),
      loadI("stage1/part4/f3.png", width * ((1634.-766)/3738), heigt * ((1220-566.)/2102))],
     [0, width * (68./3783), width * (78./2880), width * (78./2880)]]
]]


class Stage(Scene):

    def __init__(self, num, part):  # num = scene number; part = scene part number
        Scene.__init__(self)
        self.n = num  # n = scene number
        self.p = part  # p = part number
        self.l0.blit(stf[self.n][self.p][0], [0, 0])
        self.l1.blit(stf[self.n][self.p][1], [0, 0])  # draw background
        self.l3.blit(stf[self.n][self.p][2], [0, stf[self.n][self.p][3]])  # draw background
        self.t = False  # t = transformed boolean
        self.b = pygame.sprite.Group()  # b = block sprite group
        self.ba = stf[self.n][self.p][4]
        self.cr = stf[self.n][self.p][5]
        self.c = False
        self.dr = stf[self.n][self.p][6]  # door's x position; if there is no door, makes it 2 * width (useless)
        self.drf = 0  # door frame; changes l1; when door is removed, goes from 0.png to f1.png to f2.png to f3.png
        self.drfl = stf[self.n][self.p][7]  # lists of frames for l1 when door is removed
        self.drwl = stf[self.n][self.p][8]

    def up(self, sqR, sqHd):  # adds block to stage; sqR = squirrel rectangle; sqHd = squirrel head direction
        for a in self.ba:
            if (sqHd == 0 and a[0] <= sqR.right < a[2]) or (sqHd == 1 and a[0] <= sqR.x < a[2]):
                if a[5] < a[4]:
                    self.b.add(Box(a[0], a[3] - (bs * .95) * a[5], self))
                    a[5] += 1

    def down(self, sq):  # checks to see if puzzle is correct; if not, clears boxes (and shakes screen?); sq = squirrel
        self.c = True
        if self.p != 3:
            for a in self.ba:
                for r in self.cr:
                    if a[5] != r:
                        self.c = False

        if self.c:
            self.dr = 2 * width
            sq.dr = 2 * width
            # remove visible door
        else:
            for b in self.b:
                b.fi = 6
            for a in self.ba:
                a[5] = 0

    def updt(self, sq):  # sq = squirrel
        if self.c:
            if self.p < 3:
                if self.drf < 2:
                    self.l1.blit(self.drfl[3], [width - self.drwl[3], heigt / 3 * 1.5])
                    self.l1.blit(self.drfl[self.drf + 1], [width - self.drwl[self.drf + 1],
                                                           heigt / 3 * 1.5])
                    self.drf += 1
                elif self.drf == 2:
                    self.l1.blit(self.drfl[3], [width - self.drwl[3], heigt / 3 * 1.5])
                    self.drf += 1
            else:
                if self.drf < 32:
                    self.l1.blit(self.drfl[0], [0, 0])
                    if 4 < self.drf < 16:
                        self.l1.blit(self.drfl[1], [width * (900./2880), heigt * (566./1616)])
                    elif self.drf > 15:
                        self.l1.blit(self.drfl[2], [width * (900./2880), heigt * (566./1616)])
                    self.drf += 1
                elif self.drf == 32:
                    self.l1.blit(self.drfl[0], [0, 0])
                    self.l1.blit(self.drfl[3], [width * (900./2880), heigt * (566./1616)])
        self.l0.blit(stf[self.n][self.p][0], [0, 0])
        for b in self.b:
            b.f = b.fl[b.fi]
            self.l0.blit(b.f, [b.x, b.y])
            if b.fi < 4:
                b.fi += 1
            elif 5 < b.fi < 9:
                b.fi += 1
            elif b.fi == 9:
                self.b.remove(b)
        self.l2.fill((255, 255, 255, 0))
        self.l2.blit(sq.f, [sq.r.x, sq.r.y])


class Game:

    def __init__(self):
        self.wd = pygame.display.set_mode([width, heigt])  # window
        pygame.display.set_caption(title)
        self.cl = pygame.time.Clock()  # clock
        self.qt = False  # quit
        self.scl = [MainMenu(), Stage(0, 0), Stage(0, 1), Stage(0, 2), Stage(0, 3)]
        self.scn = 0
        self.sc = self.scl[self.scn]
        self.sq = Squirrel(0, flrHt + heigt / 60, self.sc)
        pygame.mixer.music.set_volume(vol)

        self.draw()

    def evpc(self):  # event processor
        pygame.display.update()
        pygame.mixer.music.set_volume(vol)

        for e in pygame.event.get():  # just for quit check
            if e.type == pygame.QUIT:
                self.qt = True

        # WASD or arrow keys
        prs = pygame.key.get_pressed()  # provides list of keys pressed
        self.sq.action(prs)  # changes squirrel actions; will change stage accordingly (due to panel click animation
        # needing to play) (unless it is main menu, where volume will change without squirrel reaction)
        if self.sq.r.centerx >= width and self.sc.c:
            if self.scn < len(self.scl) - 1:
                self.scn += 1
                self.sc = self.scl[self.scn]
                self.sq.sc = self.sc
                self.sq.dr = self.sc.dr
                self.sq.r.x -= width
        elif self.sq.r.centerx <= 0:
            if self.scn > 0:
                self.scn -= 1
                self.sc = self.scl[self.scn]
                self.sq.sc = self.sc
                self.sq.dr = self.sc.dr
                self.sq.r.x += width

    def draw(self):
        self.sc.updt(self.sq)  # update the scene with the squirrel
        self.wd.blit(self.sc.l0, [0, 0])  # update layer 0
        self.wd.blit(self.sc.l1, [0, 0])  # update layer 1
        self.wd.blit(self.sc.l2, [0, 0])  # update layer 2
        self.wd.blit(self.sc.l3, [0, 0])  # update layer 3

        pygame.display.flip()  # updates the entire screen
        # pygame.display.update((0, 500, width, 600))  # updates this section of screen

    def loop(self):  # loop for the game to be stuck in until quit
        while not self.qt:
            self.evpc()  # process inputs
            self.draw()  # update screen
            self.cl.tick(fps)  # update clock
            input=sys.argv[1]
            print(input)

if __name__ == "__main__":
    pygame.mixer.music.play()
    g = Game()  # initialize game
    g.loop()  # put game in loop
    pygame.quit()
    sys.exit()
