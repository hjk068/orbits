import pygame
import math
import random
pygame.init()

# Referenced Code 
# Overall program inspired by game 'Orbit' made by HIGHKEY Games
# petercollingridge 
# https://github.com/petercollingridge/code-for-blog/blob/master/pygame%20physics%20simulation/particle_tutorial_7.py

########################
# Variables
########################

screenWidth = 1200
midWidth = screenWidth // 2
screenHeight = 800 
midHeight = screenHeight // 2
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
light_gray = (200, 200, 200)
yellow = (255, 255, 0)
fontType = 'avenirnextttc'

########################
# Helper Functions
########################

# add two vectors, return the sum vector 
# https://github.com/petercollingridge/code-for-blog/blob/master/pygame%20physics%20simulation/particle_tutorial_12/PyParticles.py 
def addVectors(vec1, vec2):
    (angle1, mag1) = vec1
    (angle2, mag2) = vec2
    x  = math.sin(angle1) * mag1 + math.sin(angle2) * mag2
    y  = math.cos(angle1) * mag1 + math.cos(angle2) * mag2
    angle  = 0.5 * math.pi - math.atan2(y, x)
    magnitude = math.hypot(x, y)
    return (angle, magnitude)

# count number of stable orbits 
def countOrbit(allP):
    count = 0 
    for planet in allP:
        if planet.isOrbit:
            count += 1
    return count 

# read contents of a file
# http://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def readFile(path):
    with open(path, 'rt') as f:
        return f.read()

# write on a file 
# http://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def writeFile(path, contents):
    with open(path, 'w+') as f:
        f.write(contents)
    f.close()

# append on a file
def appendFile(path, contents):
    with open(path, 'a+') as f:
        f.write(contents)
    f.close()

# draw boundary to indicate that item is activated
def itemActivationDisplay(screen):
    boundary = pygame.Rect(0, 0, screenWidth, screenHeight)
    pygame.draw.rect(screen, yellow, boundary, width=4)

# convert string to 2d List (with integers and tuples)
def strTo2dList(data):
    result = []
    newList = []
    tupleElem = []
    num = ''
    listInside = False 
    tupleInside = False
    # exclude [ in the beginning and ] in the end
    for char in data[1:-1]:
        # ignore whitespace
        if char == ' ':
            continue
        # check if next character is in list 
        elif char == '[':
            listInside = True 
        elif char == ']':
            listInside = False 
            result.append(newList)
            newList = []
        # check if next character is in tuple 
        elif char == '(':
            tupleInside = True
        elif char == ')':
            tupleInside = False
            tupleElem.append(int(num))
            newTuple = (tupleElem[0], tupleElem[1])
            newList.append(newTuple)
            num = ''
            tupleElem = []
            # differentiate elements in tuple by comma
        elif tupleInside and listInside:
            if char == ',':
                tupleElem.append(int(num))
                num = ''
            else:
                num += char 
        else:
            if char != ',':
                result.append(int(char))
    return result

# save high score for different pre-built stages 
def saveHighScore(stageNum, score):
    contents = readFile('highScore.txt')
    replaced = False
    data = [stageNum, score]
    strData = str(data)
    for line in contents.splitlines():
        lineList = strTo2dList(line)
        # replace existing data with the same stage number
        if line != '' and lineList[0] == stageNum:
            newContents = contents.replace(line, strData)
            writeFile('highScore.txt', newContents + '\n')
            replaced = True
    # if not replaced, write new file with the data 
    if not replaced:
        appendFile('highScore.txt', strData + '\n')

# load existing high score using the stage number
def loadHighScore(stageNum):
    appendFile('highScore.txt', '')
    contents = readFile('highScore.txt')
    score = None
    for line in contents.splitlines():
        lineList = strTo2dList(line) 
        if line != '' and lineList[0] == stageNum:
            score = lineList[1] 
    return score

# save the data from sandbox mode to the file 
# map lists of black holes and items to keys, save as dictionary 
def save(slotNum, allB, allI, gConstant, BHSize):
    # create new file when file does not exist
    appendFile('stages.txt', '')
    # read file to get contents 
    contents = readFile('stages.txt')
    replaced = False
    data = [slotNum]
    bList = []
    # append position of black holes to the 2d list of data
    for blackHole in allB:
        bPos = (blackHole.x, blackHole.y)
        bList.append(bPos)
    data.append(bList)
    iList = []
    # append position of items to the 2d list of data
    for item in allI:
        iPos = (item.x, item.y)
        iList.append(iPos)
    data.append(iList)
    # append gravitational constant and black hole size to data
    data.append(gConstant)
    data.append(BHSize)
    strData = str(data)
    for line in contents.splitlines():
        lineList = strTo2dList(line)
        # replace existing data with the same slot number
        if line != '' and lineList[0] == slotNum:
            newContents = contents.replace(line, strData)
            writeFile('stages.txt', newContents + '\n')
            replaced = True
    # if not replaced, write new file with the 2d List 
    if not replaced:
        appendFile('stages.txt', strData + '\n')

# load existing data using the slot number
def load(slotNum, screen):
    contents = readFile('stages.txt')
    allB = []
    allI = []
    gConstant = None
    BHSize = None
    for line in contents.splitlines():
        lineList = strTo2dList(line) 
        if line != '' and lineList[0] == slotNum:
            bPos = lineList[1] 
            for b in bPos:
                allB.append(BlackHole(*b, screen))
            iPos = lineList[2]
            for i in iPos:
                allI.append(Item(*i, screen))
            gConstant = lineList[3]
            BHSize = lineList[4]
    return (allB, allI, gConstant, BHSize)

# show message in the middle of the screen
def showMsg(screen, text):
    FONT = pygame.font.SysFont(fontType, 40)
    (x, y) = (screenWidth // 2, screenHeight // 2)
    menuBar = pygame.Rect(0, y, screenWidth, 70)
    pygame.draw.rect(screen, black, menuBar)
    message = FONT.render(text, True, white)
    screen.blit(message, (300, y))

# draw predicted trail
def drawPrediction(screen, prediction, color):
    for point in prediction: 
            (x, y) = point
            pygame.draw.circle(screen, color, (int(x), int(y)), 2)

########################
# Class Definitions
########################

class Button(object):
    def __init__(self, text, x, y, w, h, color1, color2, fontSize, screen, action):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.pressed = False
        self.textColor = black
        self.color1 = color1
        self.color2 = color2
        self.action = action
        self.rect = pygame.Rect(x, y, w, h)
        self.font = pygame.font.SysFont(fontType, fontSize)

    #draw button with correct color 
    #if pressed, with color2 and if not pressed, color1
    def display(self, screen):
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        if self.pressed:
            pygame.draw.rect(screen, self.color2, self.rect)
        else:
            pygame.draw.rect(screen, self.color1, self.rect)
        message = self.font.render(self.text, True, self.textColor)
        messageRect = message.get_rect(center=((self.x +(self.w//2)), (self.y+(self.h//2))))
        screen.blit(message, messageRect)
    
    # check if the mouse is on the button or not
    def isPressed(self, mouseX, mouseY):
        if (self.x+self.w > mouseX > self.x) and (self.y+self.h > mouseY > self.y):
            self.pressed = True
        else:
            self.pressed = False 

    # run function when button is pressed 
    def runFunction(self, funcParam):
        # when there's no function parameter
        if funcParam == None:
            self.action()
        # when there are multiple function parameters
        elif type(funcParam) == tuple:
            self.action(*funcParam)
        # when there is only one function parameter 
        else:
            self.action(funcParam)

class BlackHole(object):
    def __init__(self, x, y, screen):
        self.x = x
        self.y = y
        self.r = 30
        self.mass = 160 
        self.color = black
        self.r2 = self.r * 2
        self.r3 = self.r * 3

    #draw blackhole as circle 
    def display(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r2, width=1)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r3, width=1)
    
    #animate blackhole
    def animate(self):
        animationSpeed = 2
        self.r2 -= animationSpeed
        if self.r2 <= self.r:
            self.r2 = self.r * 3
        self.r3 -= animationSpeed 
        if self.r3 <= self.r:
            self.r3 = self.r * 3

class Planet(object):
    def __init__(self, x, y, screen):
        self.x = x
        self.y = y
        self.r = 15
        self.mass = 10 
        self.color = (random.randint(0,255), random.randint(0,255), \
            random.randint(0,255))
        self.angle = 0
        self.speed = 0
        self.trail = []
        #relative angle to a blackhole 
        self.relAngle = None
        self.isOrbit = False
        self.orbitDir = None
        self.prediction = []
        self.lenPred = 100
        self.nearest = None 

    #draw planet as circle 
    def display(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r)

    #launch planet initially 
    # https://github.com/petercollingridge/code-for-blog/blob/master/pygame%20physics%20simulation/particle_tutorial_7.py
    def launch(self, x1, y1, x2, y2):
        scale = 0.03
        dy = y2 - y1
        dx = x2 - x1
        self.angle = math.pi + math.atan2(dy, dx)
        self.speed = math.hypot(dy, dx) * scale

    # predict trail using orbit and move function
    # return list of tuples of the planet's predicted position
    def predictTrail(self, x, y, allB, gConstant):
        self.launch(self.x, self.y, x, y)
        self.move()
        self.prediction.append((self.x, self.y))
        while len(self.prediction) < self.lenPred:
            self.orbit(allB, gConstant)
            self.move()
            checkCollision = self.checkBPCollision(allB, [self])
            if checkCollision == []:
                return self.prediction
            self.prediction.append((self.x, self.y))        
        return self.prediction

    #calculate the angle of planet relative to a blackHole
    def calcRelAngle(self, allB):
        minDist = screenWidth
        # find the nearest black hole 
        if (self.nearest == None):
            for blackHole in allB:
                dy = self.y - blackHole.y
                dx = self.x - blackHole.x  
                distance = math.hypot(dx, dy)
                if (distance < minDist):
                    minDist = distance 
                    self.nearest = blackHole 
        dy = self.y - self.nearest.y
        dx = self.x - self.nearest.x 
        angle = math.atan2(dy, dx)
        if (angle < 0):
            angle = 2 * math.pi + angle 
        return angle
        
    #move planet according to angle and speed
    #update trail of planet 
    # https://github.com/petercollingridge/code-for-blog/blob/master/pygame%20physics%20simulation/particle_tutorial_7.py
    def move(self):
        trailLength = 50
        if (len(self.trail) > 100):
            self.trail.pop(0)
        self.trail.append((self.x, self.y))
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    #draw trail of the planet 
    def drawTrail(self, screen):
        for point in self.trail: 
            (x, y) = point
            pygame.draw.circle(screen, self.color, (int(x), int(y)), 2)

    #take gravitational force into account 
    #need to find how to update self.angle and self.speed 
    #as vectors  
    #https://astronomy.stackexchange.com/questions/7806/exercise-2d-orbital-mechanics-simulation-python
    def orbit(self, allB, gConstant):
        #there can be multiple blackHoles 
        for blackHole in allB:
            dx = blackHole.x - self.x
            dy = blackHole.y - self.y
            distance = math.hypot(dx, dy) 
            angle = math.atan2(dy, dx)
            force = gConstant * blackHole.mass * self.mass / (distance ** 1.8)
            #calculate acceleration of planet due to gravitational force
            acceleration = (angle, force / self.mass)
            #update angle and speed by the acceleration
            (self.angle, self.speed) = addVectors((self.angle, self.speed), acceleration)

    # planet bounce off walls when item is activated
    # http://www.petercollingridge.co.uk/tutorials/pygame-physics-simulation/boundaries/
    def bounce(self):
        if (self.x + self.r > screenWidth) or (self.x - self.r < 0):
            self.angle = math.pi + self.angle
        if (self.y + self.r > screenHeight) or (self.y - self.r < 0):
            self.angle = - self.angle

    #check if the planet has collided with any blackhole 
    #if it did, it will be absorbed into the blackhole 
    #return new all_planets list 
    def checkBPCollision(self, allB, all_planets):
        for blackHole in allB:
            dx = blackHole.x - self.x
            dy = blackHole.y - self.y
            distance = math.hypot(dx, dy) 
            #the planet has collided into the blackhole if their distance is
            #less than their radii combined 
            if distance <= (self.r + blackHole.r):
                c = self.color 
                i = 0 
                for planet in all_planets: 
                    if (planet.color == c):
                        all_planets.pop(i)
                    i += 1
        return all_planets 

    # check if planet is within viable range 
    def checkInsideScreen(self):
        if (self.x > screenWidth * 2) or (self.x < screenWidth * -2):
            return False 
        if (self.y > screenHeight * 2) or (self.y < screenHeight * -2):
            return False 
        return True 

    # check if planet is orbitting in clockwise or counterclockwise direction
    def checkOrbitDir(self, allB):
        criterionAngle = math.pi 
        dy = self.y - self.nearest.y
        dx = self.x - self.nearest.x
        if (0 < self.angle < criterionAngle):
            # divided into 4 quadrants 
            # 2 directions for each quadrant, so 8 cases 
            if (dy > 0):
                if (dx > 0):
                    return 'c'
                elif (dx < 0):
                    return 'a'
            elif (dy < 0):
                if (dx > 0):
                    return 'c'  
                elif (dx < 0):
                    return 'a'
        else:
            if (dy > 0):
                if (dx > 0):
                    return 'a'
                elif (dx < 0):
                    return 'c'
            if (dy < 0):
                if (dx > 0):
                    return 'a'
                elif (dx < 0):
                    return 'c'

    #check if planet is on stable orbit or not 
    def checkOrbit(self, allB): 
        currRelAngle = self.calcRelAngle(allB)
        relAngle = self.relAngle
        blackHole = allB[0]
        dx = blackHole.x - self.x
        dy = blackHole.y - self.y
        distance = math.hypot(dx, dy) 
        if distance > screenWidth * 2:
            self.isOrbit = False 
        elif self.orbitDir == 'c':
            if (relAngle > currRelAngle > relAngle - 0.2):
                self.isOrbit = True
            else: 
                self.isOrbit = False 
        else:
            if (relAngle + 0.2 > currRelAngle > relAngle):
                self.isOrbit = True
            else:
                self.isOrbit = False
    
    # check if planet collided with item 
    def checkIPCollision(self, item):
        dx = item.x - self.x
        dy = item.y - self.y
        distance = math.hypot(dx, dy) 
        if distance <= (item.width + self.r):
            return True
        return False 

class Item(object):
    def __init__(self, x, y, screen):
        self.width = 25 
        if x == None:
            self.x = random.randint(0, screenWidth)
            self.y = random.randint(0, screenHeight-20)
        else:
            self.x = x
            self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.width, self.width)
        self.color = red

    # draw item as square
    def display(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

########################
# sub loops 
########################

# main menu loop 
# https://pythonprogramming.net/placing-text-pygame-buttons/
def gameIntro():
    pygame.font.init()
    x = screenWidth // 2
    y = screenHeight // 2
    screen = pygame.display.set_mode([screenWidth, screenHeight])
    
    # set 4 buttons
    button1 = Button('Play',x-100,y,200,50, white, light_gray, 20, screen, stages)
    button2 = Button('Sandbox Mode',x-100,y+60,200,50, white, light_gray, 20, screen, sandboxMode)
    button3 = Button('Instructions', x-100,y+120,200,50, white, light_gray, 20, screen, instruction)
    button4 = Button('Quit', x-100,y+180,200,50, white, light_gray, 20, screen, quitGame)
    all_buttons = [button1, button2, button3, button4]
    
    # for animation in 'O'
    planet = Planet(x - 108, y - 130, screen)
    planet.r = 5
    planet.speed = 1
    planet.angle = math.pi 

    intro = True
    while intro:
        (mouseX, mouseY) = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in all_buttons:
                    if button.pressed:
                        button.runFunction(None)
        screen.fill(black)
       
        #display game logo 
        pygame.font.init()
        FONT = pygame.font.SysFont(fontType, 100)
        logoText = FONT.render('rbits', True, white)
        screen.blit(logoText, (x - 50, y - 150))
        
        #game logo for 'O'
        pygame.draw.circle(screen, white, (x - 108, y - 100), 50, width=0)
        pygame.draw.circle(screen, black, (x - 108, y - 100), 20)
        
        #display 3 buttons 
        for button in all_buttons:
            button.isPressed(mouseX, mouseY)
            button.display(screen)
        
        planet.move()
        planet.angle -= 0.03
        planet.display(screen)

        #update display
        pygame.display.flip()

#user can choose which stages to play from
def stages():
    screen = pygame.display.set_mode([screenWidth, screenHeight])
    x = screenWidth//2
    y = screenHeight//2
    all_items = [Item(None, None, screen)]
    blackHolePos = dict()
    show = False

    # set 8 buttons
    button1 = Button('Stage 1',x-100,100,200,50, light_gray, white, 20, screen, main_loop)
    button2 = Button('Stage 2',x-100,160,200,50, light_gray, white, 20, screen, main_loop)
    button3 = Button('Stage 3', x-100,220,200,50, light_gray, white, 20, screen, main_loop)
    button4 = Button('Stage 4', x-100,280,200,50, light_gray, white, 20, screen, main_loop)
    button5 = Button('Saved stage 1',x-150,340,300,50, light_gray, white, 20, screen, main_loop)
    button6 = Button('Saved stage 2',x-150,400,300,50, light_gray, white, 20, screen, main_loop)
    button7 = Button('Saved stage 3',x-150,460,300,50, light_gray, white, 20, screen, main_loop)
    button8 = Button('Back',20,screenHeight-70,70,50, light_gray, white, 20, screen, gameIntro)
    stage_buttons = [button1, button2, button3, button4, button8]
    load_buttons = [button5, button6, button7]
    all_buttons = stage_buttons + load_buttons
    
    # list of black hole positions for each stage
    blackHolePos[1] = [BlackHole(x, y, screen)]
    stage2 = [BlackHole(x * 2/3, y, screen), BlackHole(x * 4/3, y, screen)]
    stage3 = [BlackHole(x, y * 1/2, screen), BlackHole(x, y, screen), BlackHole(x, y * 3/2, screen)]
    stage4 = [BlackHole(x * 1/2, y * 3/2, screen), BlackHole(x, y, screen), BlackHole(x * 3/2, y * 1/2, screen)]
    blackHolePos[2] = stage2
    blackHolePos[3] = stage3
    blackHolePos[4] = stage4

    stageView = True
    while stageView:
        (mouseX, mouseY) = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                i = 1
                for button in stage_buttons:
                    if button.pressed:
                        if button.action == main_loop:
                            all_blackHoles = blackHolePos[i]
                            button.runFunction((all_blackHoles, all_items, None, 30, i))
                        else:
                            button.runFunction(None)
                    i += 1
                i = 1
                for button in load_buttons:
                    if button.pressed:
                        (all_blackHoles, all_items, gConstant, BHSize) = load(i, screen)
                        if (all_blackHoles == []):
                            show = True 
                            startTime = pygame.time.get_ticks()
                        else:
                            if BHSize != None:
                                BHSize *= 10
                            button.runFunction((all_blackHoles, all_items, gConstant, BHSize, None))
                    i += 1
        screen.fill(white)

        # display buttons
        for button in all_buttons:
            button.isPressed(mouseX, mouseY)
            button.display(screen)

        # if slot is empty, show message 
        if show:
            showMsg(screen, 'The slot is empty.')
            elapsed = pygame.time.get_ticks() - startTime
            if elapsed > 1000:
                show = False
                
        pygame.display.flip()


# show instructions
def instruction():
    screen = pygame.display.set_mode([screenWidth, screenHeight])
    # back button
    button1 = Button('Back', 40 ,screenHeight-70,70,50, white, light_gray, 20, screen, gameIntro)
    showing = True
    FONT = pygame.font.SysFont(fontType, 30)
    text1 = 'Launch planets so that they can maintain stable orbits around' 
    text2 = 'one or more black holes for more than 3 seconds.'
    text3 = 'Try to reach the goal number of stable orbits.' 
    text4 = 'Red squares are items. Obtaining them builds a shield around the' 
    text5 = 'screen boundary for a few seconds and planets will bounce off the walls.'
    text6 = 'Build, save and play your own stages in the sandbox mode.'
    all_text = [text1, text2, text3, text4, text5, text6]
    
    while showing:
        (mouseX, mouseY) = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button1.pressed:
                    button1.runFunction(None)
        screen.fill(black)
        i = 0
        for text in all_text:
            message = FONT.render(text, True, white)
            screen.blit(message, (20, 10 + 40 * i))
            i += 1
        button1.isPressed(mouseX, mouseY)
        button1.display(screen)
        pygame.display.flip()

# user can make own stage
def sandboxMode():
    clock = pygame.time.Clock()
    FONT = pygame.font.SysFont(fontType, 20)
    pygame.init()
    screen = pygame.display.set_mode([screenWidth, screenHeight])
    screen.fill(white)
    all_blackHoles = []
    all_items = []
    sandBox = True
    saveWindow = False
    add = False
    delete = False
    saveMode = False
    loadMode = False 
    show = False
    # black hole mode --> can add or delete black holes
    BHMode = True
    # item mode --> can add or delete items 
    itemMode = False
    gConstant = 5
    BHSize = 30 
    dragged1 = False
    dragged2 = False

    #define black hole animation as an event
    #to set timer for black hole animation
    blackHole_animation = pygame.USEREVENT + 1
    blackHoleTimer = 1000
    pygame.time.set_timer(blackHole_animation, blackHoleTimer)
    
    # set 6 buttons
    button1 = Button('Play',160,10,50,50, white, light_gray, 20, screen, main_loop)
    button2 = Button('Back', screenWidth - 60,10,50,50, white, light_gray, 20, screen, gameIntro)
    button3 = Button('Add',10,10,50,50, white, light_gray, 20, screen, None)
    button4 = Button('Delete',70,10,80,50, white, light_gray, 20, screen, None)
    button5 = Button('Save', screenWidth - 120,10,50,50, white, light_gray, 20, screen, gameIntro)
    button6 = Button('Load', screenWidth - 180,10,50,50, white, light_gray, 20, screen, gameIntro)
    button7 = Button('Item',220,10,50,50, white, light_gray, 20, screen, None)
    button8 = Button('Black Hole',280,10,110,50, white, light_gray, 20, screen, None)
    all_buttons1 = [button1, button2, button3, button4, button5, button6, button7, button8]
    # buttons for saving and loading
    slot1 = Button('Slot 1', midWidth, midHeight-60, 80, 50, light_gray, white, 20, screen, save)
    slot2 = Button('Slot 2', midWidth, midHeight, 80, 50, light_gray, white, 20, screen, save)
    slot3 = Button('Slot 3', midWidth, midHeight+60, 80, 50, light_gray, white, 20, screen, save)
    all_buttons2 = [slot1, slot2, slot3]
    # sliders for changing gConstant and black hole size 
    slider1 = Button(' ', screenWidth-165, 110, 20, 20, light_gray, light_gray, 20, screen, None)
    slider2 = Button(' ', screenWidth-165, 180, 20, 20, light_gray, light_gray, 20, screen, None)
    slider1.textColor = light_gray
    slider2.textColor = light_gray
    all_buttons3 = [slider1, slider2]
    while sandBox == True:
        (mouseX, mouseY) = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sandBox = False 
            # animate black holes
            elif event.type == blackHole_animation:
                for blackhole in all_blackHoles:
                    blackhole.animate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # can save or load in any of the three slots 
                if saveWindow:
                    i = 1
                    for button in all_buttons2:
                        if button.pressed:
                            # save
                            if saveMode:
                                funcParam = (i, all_blackHoles, all_items, gConstant, BHSize)
                                button.runFunction(funcParam)
                                show = True 
                                startTime = pygame.time.get_ticks()
                                message = 'Successfully Saved!'
                            # load 
                            elif loadMode:
                                (all_blackHoles, all_items, gConstant, BHSize) = load(i, screen)
                                if not (all_blackHoles == []):
                                    BHSize *= 10
                                    for blackhole in all_blackHoles: 
                                        blackhole.r = BHSize
                                        blackhole.r2 = blackhole.r * 2
                                        blackhole.r3 = blackhole.r * 3
                                    show = True 
                                    startTime = pygame.time.get_ticks()
                                    message = 'Successfully Loaded!'
                            break 
                        else:
                            i += 1
                    saveMode = False
                    loadMode = False 
                    saveWindow = False
                # otherwise, check if other buttons are pressed
                elif button1.pressed:
                    button1.runFunction((all_blackHoles, all_items, gConstant, BHSize, None))
                elif button2.pressed:
                    button2.runFunction(None)
                elif button3.pressed:
                    add = True 
                    delete = False
                elif button4.pressed:
                    delete = True
                    add = False 
                elif button5.pressed:
                    saveMode = True
                    saveWindow = True
                elif button6.pressed:
                    loadMode = True 
                    saveWindow = True
                elif button7.pressed:
                    itemMode = True
                    BHMode = False
                elif button8.pressed:
                    itemMode = False
                    BHMode = True
                elif slider1.pressed:
                    dragged1 = True
                elif slider2.pressed:
                    dragged2 = True 
                # add black hole 
                elif add == True and not button3.pressed and BHMode:
                    blackHole = BlackHole(mouseX, mouseY, screen)
                    all_blackHoles.append(blackHole)
                # add item 
                elif add == True and not button3.pressed and itemMode:
                    item = Item(mouseX, mouseY, screen)
                    all_items.append(item)
                # delete black hole 
                elif delete == True and not button4.pressed and BHMode:
                    i = 0
                    for blackHole in all_blackHoles:
                        xMin = blackHole.x - blackHole.r
                        xMax = blackHole.x + blackHole.r
                        yMin = blackHole.y - blackHole.r
                        yMax = blackHole.y + blackHole.r
                        if (xMin <= mouseX <= xMax):
                            if (yMin <= mouseY <= yMax):
                                all_blackHoles.pop(i)
                            else: i += 1
                        else:
                            i += 1
                # delete item
                elif delete == True and not button4.pressed and itemMode:
                    i = 0
                    for item in all_items:
                        xMin = item.x - item.width
                        xMax = item.x + item.width
                        yMin = item.y - item.width
                        yMax = item.y + item.width
                        if (xMin <= mouseX <= xMax):
                            if (yMin <= mouseY <= yMax):
                                all_items.pop(i)
                            else: i += 1
                        else:
                            i += 1
            # if mouse is no longer dragged,
            # change gConstant and size of black hole 
            # according to the position of the slider 
            elif event.type == pygame.MOUSEBUTTONUP:
                if dragged1:
                    scale = (slider1.x - screenWidth + 310)/300 
                    gConstant = int(round(scale * 10)) 
                    dragged1 = False
                elif dragged2:
                    scale = (slider2.x - screenWidth + 310)/300 
                    BHSize = int(round(scale * 80))
                    for blackhole in all_blackHoles: 
                        blackhole.r = BHSize
                        blackhole.r2 = blackhole.r * 2
                        blackhole.r3 = blackhole.r * 3
                    dragged2 = False

        screen.fill(white)
        # draw black holes
        for blackhole in all_blackHoles:
            blackhole.display(screen)
        # draw items 
        for item in all_items:
            item.display(screen)
        # draw menu bar
        menuBar = pygame.Rect(0, 0, screenWidth, 70)
        pygame.draw.rect(screen, black, menuBar)
        # if save or load button is pressed 
        if saveWindow:
            for button in all_buttons2:
                button.isPressed(mouseX, mouseY)
                button.display(screen)
            pygame.display.flip()
            continue 
        # display buttons on the menu bar
        for button in all_buttons1:
            button.isPressed(mouseX, mouseY)
            button.display(screen)
        if dragged1:
            if (mouseX < screenWidth-310):
                slider1.x = screenWidth-310
            elif (mouseX > screenWidth-10):
                slider1.x = screenWidth-10
            else:
                slider1.x = mouseX
        elif dragged2:
            if (mouseX < screenWidth-310):
                slider2.x = screenWidth-310
            elif (mouseX > screenWidth-10):
                slider2.x = screenWidth-10
            else:
                slider2.x = mouseX

        # display sliders 
        sliderBar1 = pygame.Rect(screenWidth-310, 115, 300, 10)
        sliderBar2 = pygame.Rect(screenWidth-310, 185, 300, 10)
        pygame.draw.rect(screen, black, sliderBar1)
        pygame.draw.rect(screen, black, sliderBar2)
        for button in all_buttons3:
            button.isPressed(mouseX, mouseY)
            button.display(screen)
        # text description of sliders 
        slider1Text = FONT.render('Gravitational Constant', True, black)
        slider2Text = FONT.render('Blackhole Size', True, black)
        screen.blit(slider1Text, (screenWidth-250, 70))
        screen.blit(slider2Text, (screenWidth-250, 145))
        # if successfully saved or loaded, show message for 1 second
        if show:
            showMsg(screen, message)
            elapsed = pygame.time.get_ticks() - startTime
            if elapsed > 1000:
                show = False

        pygame.display.flip()

# quit game from main menu
def quitGame():
    pygame.display.quit()
    pygame.quit()

########################
# main loop for game
########################

def main_loop(allB, allI, gConstant, BHSize, stageNum):
    clock = pygame.time.Clock()
    FONT = pygame.font.SysFont(fontType, 40)
    screen = pygame.display.set_mode([screenWidth, screenHeight])
    activationLength = 7000
    startX = None
    startY = None
    all_blackHoles = allB
    all_items = allI
    all_planets = []
    mouseDrag = False
    activated = False
    running = True
    countStable = False
    clear = False
    achieve = False
    numLaunched = 0
    goal = 3
    if (gConstant == None):
        gConstant = 5
    
    # load high score with stage number
    if (stageNum == None):
        highScore = None
    else:
        highScore = loadHighScore(stageNum)

    # event and timer setting for black hole animation 
    blackHole_animation = pygame.USEREVENT + 1
    blackHoleTimer = 1000
    pygame.time.set_timer(blackHole_animation, blackHoleTimer)

    # set 'Back' button --> go back to main menu
    button1 = Button('Back', screenWidth-80,10,70,50, white, light_gray, 20, screen, gameIntro)

    while running:
        (mouseX, mouseY) = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            #animate black holes every 2000ms
            elif event.type == blackHole_animation:
                for blackhole in all_blackHoles:
                    blackhole.animate()
            #drag and launch planet 
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button1.pressed:
                    button1.runFunction(None)
                else: 
                    mouseDrag = True 
                    (startX, startY) = (mouseX, mouseY)
                    planet = Planet(mouseX, mouseY, screen)
                    all_planets.append(planet)
            elif event.type == pygame.MOUSEBUTTONUP:
                mouseDrag = False
                #launch and set relative angle of planet 
                if all_planets != []:
                    planet.launch(startX, startY, mouseX, mouseY)
                    numLaunched += 1
            #erase planets when spacebar is pressed
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    all_planets = []  
                    clear = False 
                    numLaunched = 0 
                    all_items = allI

        if mouseDrag:
            #draw gauge bar when launching planet 
            pygame.draw.circle(screen, planet.color, (int(mouseX), int(mouseY)), 10)
            pygame.draw.line(screen, planet.color, \
                (int(mouseX), int(mouseY)), (int(startX), int(startY)))
            planet2 = Planet(startX, startY, screen)
            prediction = planet2.predictTrail(mouseX, mouseY, all_blackHoles, gConstant)
            drawPrediction(screen, prediction, planet.color)
            pygame.display.flip()

        #background color: white
        screen.fill(white)

        #loop through list of blackholes
        for blackhole in all_blackHoles:
            blackhole.r = BHSize
            blackhole.display(screen)

        # if item is activated, display boundary
        # add elapsed time to timer 
        # so activation only lasts for certain amount
        if activated:
            itemActivationDisplay(screen)
            elapsed = pygame.time.get_ticks() - startTime 
            if elapsed > activationLength:
                activated = False
        
        i = 0
        # loop through list of planets
        for planet in all_planets: 
            if planet.speed != 0 and planet.relAngle == None:
                planet.relAngle = planet.calcRelAngle(all_blackHoles)
            if planet.speed != 0 and planet.orbitDir == None:
                planet.orbitDir = planet.checkOrbitDir(allB)
            planet.move()
            if activated:
                planet.bounce()
            all_planets = planet.checkBPCollision(all_blackHoles, all_planets)
            planet.drawTrail(screen)
            if (mouseDrag == False):
                planet.orbit(all_blackHoles, gConstant)
            if (planet.relAngle != None) and (planet.isOrbit == False):
                planet.checkOrbit(all_blackHoles)
            i2 = 0
            for item in all_items:
                if planet.checkIPCollision(item):
                    all_items.pop(i2)
                    activated = True 
                    startTime = pygame.time.get_ticks()
                else:
                    i2 += 1
            # if planet not inside range, delete it 
            if planet.checkInsideScreen() == False:
                all_planets.pop(i)
            else: 
                planet.display(screen)
                i += 1
        # replenish item
        if all_items == []:
            all_items = [Item(None, None, screen)]

        # display items 
        for item in all_items:
            item.display(screen)

        x = 50
        y = screenHeight - 50
        count = countOrbit(all_planets)
        # check if the game is cleared 
        if not countStable and count >= goal:
            countStable = True
            countStartTime = pygame.time.get_ticks()
        # have to maintain stable orbit for 3 seconds to win
        if countStable:
            if count < goal:
                countStable = False
            else:
                elapsed = pygame.time.get_ticks() - countStartTime
                if elapsed > 3000:
                    if (highScore == None) or (numLaunched < highScore):
                        achieve = True 
                        hScoreTime = pygame.time.get_ticks()
                        highScore = numLaunched 
                        saveHighScore(stageNum, numLaunched)
                    clearTime = pygame.time.get_ticks()
                    clear = True 

        # display orbit count
        countText = FONT.render('Orbit Count: ' + str(count), True, black)
        screen.blit(countText, (x, y))
        
        # display goal number of orbit
        goalText = FONT.render('Goal: ' + str(goal), True, black)
        screen.blit(goalText, (x, y - 50))
        
        # display highest score for the stage
        if (highScore == None):
            highScoreText = FONT.render('High Score: ', True, black)
        else:
            highScoreText = FONT.render('High Score: ' + str(highScore), True, black)
        screen.blit(highScoreText, (screenWidth - 300, y))

        #display Back button
        button1.isPressed(mouseX, mouseY)
        button1.display(screen)

        # if game is cleared, show stage clear message 
        if clear:
            showMsg(screen, 'Stage Clear! You launched ' + str(numLaunched) + ' planets')
            elapsed2 = pygame.time.get_ticks() - clearTime
            if elapsed2 > 3000:
                clear = False

        # if new high score is achieved, display message 
        if achieve:
            showMsg(screen, "Congrats! You got a new high score!")
            elapsed1 = pygame.time.get_ticks() - hScoreTime
            if elapsed1 > 1000:
                achieve = False

        # update the contents of entire display
        pygame.display.flip()

if __name__ == '__main__':
    gameIntro()