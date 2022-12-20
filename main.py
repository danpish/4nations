"""
Hello I'm Daniel and today im going to make this game with ursina engine
just because i hate my self and decided to suffer to make a game
with an engine that i dont really know and a mountain of exams on the horizon
with a terrible mental health tooo 
"""
from ursina import *



a = 0

def update():
	global a
	camera.position = (0,0,a)
	#a += 0.1

textures = ["Iran", "france", "armen", "argen"]

class cards(Entity):# I;m just praying that this works //LATER // OH GOODNESS IT WORKES
	def __init__(self, position, texture):
		super().__init__(
			parent = scene,
			position = position,
			model="quad",
			collider = "cube",
			texture = texture
		)

dock = []

game = Ursina()
window.isfullscreen = False
window.borderless = False
window.exit_button.visible = False
window.exit_button.enabled = False
window.fps_counter.visible = True
#Cube = Entity(model = "quad", position = (0,-1,10), texture='Iran')
#"""                     color = color.blue,"""
dock.append(cards((-2,0,10), 'Iran'))
dock.append(cards((-1,0,10), 'Iran'))
dock.append(cards((1,0,10), 'Iran'))
dock.append(cards((2,0,10), 'Iran'))
dock[0].rotation = (0,0,-60)
dock[1].rotation = (0,0,-30)
dock[2].rotation = (0,0,30)
dock[3].rotation = (0,0,60)
dock[1].texture = textures[1]
dock[2].texture = textures[2]
dock[3].texture = textures[3]
#Windos = Text(text="Windwos XP", position=(0,1,10))
#GOD DAMN WHAT THE FU

game.run()