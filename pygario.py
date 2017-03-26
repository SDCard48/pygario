import pygame
from random import randint
from pygame.locals import *
import time

COLOURS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]

pygame.init()

SCREEN_SIZE = (1000, 500)
FONT = pygame.font.Font(None, 14)
FEED = []
ADERSARS = []

class Player(object):
    def __init__(self, name, colour):
        self.name = name
        self.colour = colour
        self.level = 1
        self.feed = 0
        self.size = 2
        self.speed = 6
        self.location = (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2)
        self.destination = self.location
        self.stopDis = 5    #Stopping distance

    def update(self):
        mousePosX, mousePosY = pygame.mouse.get_pos()   #Finds most recent mouse position on window
        self.destination = (mousePosX, mousePosY)       #Sets destination
        selfPosX, selfPosY = self.location

        disToDes = (mousePosX-selfPosX, mousePosY-selfPosY) #Works out the distance to the mouse
        if disToDes[0] > 0:
            disToDes = (disToDes[0]+self.stopDis, disToDes[1])  #If the distance is less than 0, add the stopping distance
        if disToDes[1] > 0:
            disToDes = (disToDes[0], disToDes[1]+self.stopDis)
        disToAdd = (int(disToDes[0]/self.speed),int(disToDes[1]/self.speed))    #Add distance/speed to current location to get a new location
        self.location = (self.location[0]+disToAdd[0], self.location[1]+disToAdd[1])

        if self.feed >= 10: #Leveling Up
            self.levelUp()

        if self.feed <= -1: #Leveling Down
            self.levelDown()

    def render(self, screen):
        pygame.draw.circle(screen, (128, 128, 128), (self.location[0]-1, self.location[1]-1), self.size+1)  #Draw shadow
        pygame.draw.circle(screen, self.colour, self.location, self.size)   #Draw circle
        w, h = FONT.size(self.name)
        my_font = FONT.render(self.name, True, (0, 0, 0))
        screen.blit(my_font, (self.location[0]-w/2, self.location[1]-h/2))  #Render the name

    def levelUp(self):
        self.level += 1
        self.size = 2**self.level
        if self.size > 64:
            self.size = 64
        self.speed = int(self.speed*2)  #* slows down the entity (increases amount of sections distance divided by)
        if self.speed > 192:
            self.speed = 192
        self.feed = 0
        self.stopDis = self.speed-1

    def levelDown(self):
        self.level -= 1
        self.size = 2**self.level
        if self.size < 2:
            self.size = 2
        if self.size > 64:
            self.size = 64
        self.speed = int(self.speed/2) #Opposite of *
        if self.speed < 6:
            self.speed = 6
        self.feed = 9
        self.stopDis = self.speed-1


class Adversary(object):
    def __init__(self, name, player, colour, startLevel):
        self.name = name
        self.player = player
        self.colour = colour
        self.level = startLevel
        self.feed = 0
        self.size = 2**self.level
        if self.size > 64:
            self.size = 64
        self.speed = 3*(2**self.level)
        self.location = (randint(1, SCREEN_SIZE[0]-1), randint(1, SCREEN_SIZE[1]-1))    #Spawns at a random location
        self.destination = self.location
        self.targetNo = 0
        self.stopDis = self.speed-1

    def update(self):
        if self.location == self.destination or FEED[self.targetNo].location != self.destination:   #Choose a random piece of food to aim for
            self.targetNo = randint(0, len(FEED)-1)
            target = FEED[self.targetNo]
            self.destination = target.location

        for item in ADERSARS:   #If there are lower leveled adversaries nearby, aim for them
            if item.level < self.level:
                disToItem = (self.location[0]-item.location[0], self.location[1]-self.player.location[1])
                if disToItem[0] < 80 and disToItem[0] > -80:
                    if disToItem[1] < 80 and disToItem[1] > -80:
                        self.destination = item.location
        
        if self.player.level < self.level:  #If the player has a lower level and is nearby, aim for them
            disToPlay = (self.location[0]-self.player.location[0], self.location[1]-self.player.location[1])
            if disToPlay[0] < 80 and disToPlay[0] > -80:
                if disToPlay[1] < 80 and disToPlay[1] > -80:
                    self.destination = self.player.location


        mousePosX, mousePosY = self.destination
        selfPosX, selfPosY = self.location

        disToDes = (mousePosX-selfPosX, mousePosY-selfPosY) #Moving around
        if disToDes[0] > 0:
            disToDes = (disToDes[0]+self.stopDis, disToDes[1])
        if disToDes[1] > 0:
            disToDes = (disToDes[0], disToDes[1]+self.stopDis)
        disToAdd = (int(disToDes[0]/self.speed),int(disToDes[1]/self.speed))
        self.location = (self.location[0]+disToAdd[0], self.location[1]+disToAdd[1])
        
        playX, playY = self.player.location
        size = self.player.size
        if playX+size >= self.location[0]-self.size and playX-size <= self.location[0]+self.size:   #Feeding off player
            if playY+size >= self.location[1]-self.size and playY-size <= self.location[1]+self.size:
                if self.player.level > self.level:
                    self.feed -=1
                    self.player.feed += 1
                if self.player.level < self.level:  #Player feeding off entity
                    self.feed += 1
                    self.player.feed -= 1

        for item in ADERSARS:
            playX, playY = item.location
            size = item.size
            if playX+size >= self.location[0]-self.size and playX-size <= self.location[0]+self.size:   #Feeding off lesser entities
                if playY+size >= self.location[1]-self.size and playY-size <= self.location[1]+self.size:
                    if item.level < self.level:
                        self.feed +=1
                        item.feed -= 1
        
        if self.feed >= 10:
            self.levelUp()
        if self.feed <= -1:
            self.levelDown()

    def render(self, screen):
        pygame.draw.circle(screen, (128, 128, 128), (self.location[0]-1, self.location[1]-1), self.size+1)
        pygame.draw.circle(screen, self.colour, self.location, self.size)
        w, h = FONT.size(self.name)
        screen.blit(FONT.render(self.name, True, (0, 0, 0)), (self.location[0]-w/2, self.location[1]-h/2))

    def levelUp(self):
        self.level += 1
        self.size = 2**self.level
        if self.size > 64:
            self.size = 64
        self.speed = int(self.speed*2)
        self.feed = 0
        self.stopDis = self.speed-1

    def levelDown(self):
        self.level -= 1
        self.size = 2**self.level
        if self.size < 2:
            self.size = 2
        if self.size > 64:
            self.size = 64
        self.speed = int(self.speed/2)
        self.feed = 9
        self.stopDis = self.speed-1
        if self.stopDis < 11:
            self.stopDis = 11
        


class Feed(object):
    def __init__(self, player, value=1):
        self.value = value
        self.location = (randint(1, SCREEN_SIZE[0]-1), randint(1, SCREEN_SIZE[1]-1))    #Random spawn location
        self.player = player
        self.colour = COLOURS[randint(0, 5)]

    def update(self):
        playX, playY = self.player.location #Player feeding
        size = self.player.size
        if playX+size >= self.location[0]-self.value and playX-size <= self.location[0]+self.value:
            if playY+size >= self.location[1]-self.value and playY-size <= self.location[1]+self.value:
                self.value -=1
                self.player.feed += 1

        for adversary in ADERSARS:  #Other entities feeding
            if adversary.location[0]+adversary.size >= self.location[0]-self.value and adversary.location[0]-adversary.size <= self.location[0]+self.value:
                if adversary.location[1]+adversary.size >= self.location[1]-self.value and adversary.location[1]-adversary.size <= self.location[1]+self.value:
                    self.value -= 1
                    adversary.feed += 1

    def render(self, screen):
        pygame.draw.circle(screen, (128, 128, 128), (self.location[0]-1, self.location[1]-1), self.value+1)
        pygame.draw.circle(screen, self.colour, self.location, self.value)


def populate(player):   #Ensures that 10 feed is always on screen
    while len(FEED) < 10:
        food = Feed(player, randint(1, 3))
        FEED.append(food)

def scoreBoard(screen, player): #Displays scores
    y = 0
    scores = []
    for item in ADERSARS:
        scores.append((item.feed+item.level*10, item.name))
    scores.append((player.feed+player.level*10, player.name))
    scores.sort()
    scores.reverse()
    for score in scores:
        w, h = FONT.size("%s : %i" % (score[1], score[0]))
        y += 2+h/2
        screen.blit(FONT.render("%s : %i" % (score[1], score[0]), True, (0, 0, 0)), (SCREEN_SIZE[0]-w, y))
    


def main(name, colour):
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
    pygame.display.set_caption("Py-gario")

    clock = pygame.time.Clock()

    player = Player(name, colour)   #Creates the player

    populate(player)    #Creates food

    for item in ['Fred', 'James', 'Bob']:   #Creates adversaries
        adversar = Adversary(item, player, COLOURS[randint(0, len(COLOURS)-1)], randint(1, 3))
        ADERSARS.append(adversar)

    text = 'You Died...'

    while player.level > 0: #Mainloop
        clock.tick()
    
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
        if len(ADERSARS) == 0:
            text = 'You Won!'
            break

        screen.fill((255, 255, 255))

        populate(player)
    
        player.update()
        for item in ADERSARS:   #Updates the enemies
            item.update()
            if item.level <= 0:
                ADERSARS.remove(item)
            else:
                item.render(screen)
        for item in FEED:   #Updates the food
            item.update()
            if item.value <= 0:
                FEED.remove(item)
            else:
                item.render(screen)
        player.render(screen)

        scoreBoard(screen, player)  #Dispalays scores

        pygame.display.update()

    endFont = pygame.font.Font(None, 36)
    w, h = endFont.size(text)
    screen.blit(endFont.render(text, True, (0, 0, 0)), ((SCREEN_SIZE[0]/2)-w/2, (SCREEN_SIZE[1]/2)-h/2))
    pygame.display.update()
    time.sleep(2)
    
    pygame.quit()

if __name__ == "__main__":
    from Tkinter import *
    from tkColorChooser import askcolor

    def askColour():
        triple = None
        while triple == None:
            triple, hexstr = askcolor()
        return triple
    
    name = ''
    while name == '':
        name = raw_input("Name: ")
    colour = askColour()
    main(name, colour)
    quit
