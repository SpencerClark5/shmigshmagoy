 #imports
import os
import pygame
import math
from pygame import *
from pygame.math import Vector2,Vector3
from pygame.locals import *
from forces import *
from physics_objects import *
from contact import *
from sqlalchemy import null
from beanbag import *

#clear terminal before you run
os.system("cls||clear")

#initialize pygame and open window
pygame.init()
width, height = 1920, 1080
window = pygame.display.set_mode([width, height])

fontpath = pygame.font.match_font("arial")
font = pygame.font.SysFont('arial', round(window.get_width()/30))

#timing
fps = 1000
dt = 1 / fps
clock = pygame.time.Clock()


#variables
objects = []
nonPhysicsObjects = []
fixedObjects = []
slingshot = []
beanbags = []
xOffset = 0
yOffset = -75
LeftScoringZone3Points = [Vector2(200,807), Vector2(200,907), Vector2(500,907)]
LeftScoringZone1Point = [Vector2(255,725),Vector2(255,772),Vector2(525,825),Vector2(525,884)]
RightScoringZone3Points = [Vector2(1400,907),Vector2(1400,807),Vector2(1700,907)]
RightScoringZone1Point = [Vector2(1375,832),Vector2(1700,713),Vector2(1375,882),Vector2(1700,736)]


#grab related variables
ballGrabbed = False
ballLaunched = False
coeff_of_friction = 0.3
grabbedObj = null
mousePosCur = Vector2(pygame.mouse.get_pos())
mousePosPre = Vector2(pygame.mouse.get_pos())
mouseVel = Vector2(0,0)

#create boards
#left board
leftBoardTop = Polygon(window,local_points=[[0,0],[80,28],[96,0],[32/2,-28]],pos=Vector2(210 +xOffset,727 - yOffset),mass=math.inf,color=Vector3(255,0,0))
objects.append(leftBoardTop)
leftBoardBottom = Polygon(window,local_points=[[0,0],[150,53],[165,28],[32/2,-28]],pos=Vector2(360 +xOffset,782 - yOffset),mass=math.inf,color=Vector3(255,0,0))
objects.append(leftBoardBottom)

#left board scoring zones
#left3PointZone = Polygon(window,local_points=[[0,0],])

#right board
rightBoardTop = Polygon(window,local_points=[[0,0],[80,-28],[96,0],[32/2,28]],pos=Vector2(1610 -xOffset,722 - yOffset),mass=math.inf,color=Vector3(255,0,0))
objects.append(rightBoardTop)
fixedObjects.append(True)
rightBoardBottom = Polygon(window,local_points=[[0,0],[150,-53],[165,-28],[32/2,28]],pos=Vector2(1380 - xOffset,807 - yOffset),mass=math.inf,color=Vector3(255,0,0))
objects.append(rightBoardBottom)
fixedObjects.append(True)

#create floor
#floor = Wall(window, start_point=Vector2(0,910),end_point=(1920,910),color=Vector3(0,255,0), reverse=True)
# objects.append(floor)
# fixedObjects.append(True)

#create sticks
leftStick = Polygon(window,local_points=[[0,0], [10,0],[10,105],[0,105]],color=(0,0,0),pos=Vector2(215 + xOffset,730 - yOffset),mass=math.inf)
nonPhysicsObjects.append(leftStick)
fixedObjects.append(True)
rightStick = Polygon(window,local_points=[[0,0], [10,0],[10,110],[0,110]],color=(0,0,0),pos=Vector2(1690 + xOffset,725 - yOffset),mass=math.inf)
nonPhysicsObjects.append(rightStick)
fixedObjects.append(True)

#slingshot creation
topCircle = Circle(window, mass=10, pos=(window.get_width()/2, window.get_height()/2), radius=10, vel=Vector2(0,0), color=Vector3(100,100,100), width=2) 

#beanbag creation
beanbag1 = Beanbag(color=Vector3(255,0,0), pos=Vector2(window.get_width()/2 - 100, 400), launchOrigin=topCircle)

beanbag1.AddSecsToList(objects)
beanbag1.AddSecsToList(beanbags)

fixedObjects.append(False)
fixedObjects.append(False)
fixedObjects.append(False)
fixedObjects.append(False)

#more slingshot creation
objects.append(topCircle)
fixedObjects.append(True)
slingshot.append(topCircle)

# SETUP FORCES
gravity = Gravity(objects_list=objects, acc=(0, 980))
bonds = SpringForce(window, pairs_list=slingshot, strength=40)
drag = AirDrag(objects_list=objects)
#repulsion = SpringRepulsion(objects_list=bag)
windVector = Vector2(0,0)
pygame.key.set_repeat(1,1)

#game loop
running = True
while running:
    click = pygame.mouse.get_pressed()
    # update the display
    pygame.display.update()
    # delay for correct timing
    clock.tick(fps)
    # clear the screen
    window.fill([255,255,255])

    mousePosCur = Vector2(pygame.mouse.get_pos())
    mouseVel = Vector2(mousePosCur - mousePosPre)

    #get pressed key
    key = pygame.key.get_pressed()

    # EVENT loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False



    if click[0]:
        for obj in beanbags:
            if (((obj.pos - Vector2(pygame.mouse.get_pos())).magnitude() <= obj.radius)) and grabbedObj == null:
                grabbedObj = objects.index(obj)
                if not ballGrabbed:
                    ballGrabbed = True
                break
            

        if grabbedObj != null:
            objects[grabbedObj].pos = pygame.mouse.get_pos()
            objects[grabbedObj].vel = Vector2(0,0)


    if not click[0]:
        if ballGrabbed:
            ballGrabbed = False
            ballLaunched = True

        if grabbedObj == 0:
            objects[grabbedObj].vel = Vector2(0,0)
            grabbedObj = null

        if grabbedObj != null and grabbedObj > 0:
            objects[grabbedObj].vel = mouseVel
            grabbedObj = null
        

        mousePosPre = mousePosCur

    if beanbag1.centralSec != null:
        if (topCircle.pos - Vector2(beanbag1.centralSec.pos)).magnitude() <= topCircle.radius + beanbag1.centralSec.radius and len(slingshot) > 1:
            if ballLaunched:
                ballLaunched = False
                slingshot.pop(slingshot.index(beanbag1.centralSec))
                


    # PHYSICS
    for o in objects:
        o.clear_force()

    # collisions
    beanbag1.UpdateCollisions()
    overlap = False
    contacts: list[Contact] = []

    # check for contact with any other objects
    for a, b in itertools.combinations(objects, 2):
        resolve = True

        if (a.isBeanbag and b == topCircle) or (a == topCircle and b.isBeanbag):
            resolve = False
            c: Contact = generate(a, b, resolve=resolve, friction=coeff_of_friction)
        else:
            c: Contact = generate(a, b, resolve=resolve, friction=coeff_of_friction)

        if c.overlap > 0:
            overlap = True
            contacts.append(c)



    ## apply all forces
    gravity.apply(grabbedObj)


    if len(slingshot) > 1:
        bonds.apply(grabbedObj)
    #drag.apply(grabbedObj)


    ## update all objects
    for obj in objects:
        if fixedObjects[objects.index(obj)] == False:
            if objects.index(obj) > 0 and objects.index(obj) != grabbedObj:
                obj.vel += windVector
            obj.update(dt)
    
    beanbag1.Update(grabbedObj=grabbedObj, objectsList=objects, slingshot=slingshot, ballGrabbed=ballGrabbed)
        

    # GRAPHICS
    # draw objects
    offset = 1200
    for d in nonPhysicsObjects:
        d.draw()

    for o in objects:
        o.draw()