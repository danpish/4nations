"""
Hello I'm Daniel and today im going to make this game with ursina engine
just because i hate my self and decided to suffer to make a game
with an engine that i dont really know and a mountain of exams on the horizon
with a terrible mental health tooo 
"""
from ursina import *
dock = []

g_mouseX = 0
g_mouseY = 0
pov_mouseX = 0
pov_mouseY = 0
hitting = 255
	


a = 0
def update():
	global a, g_mouseY, g_mouse, pov_mouseX, pov_mouseY, hitting
	camera.position = (0,0,a)
	#a += 0.1
	#print("mousex " + str(mouse.x) + ": mousey" + str(mouse.y))#for mouse positioning debug
	#lets cast a beam from the mosue
	mouse_origin = Vec3(0,0,0)
	cast_direction = (mouse.x + mouse.x / 8, mouse.y + mouse.y / 8,2) #It was not supposed to work with this but somehow it did
	mouse_raycast = raycast(mouse_origin, cast_direction, debug=True)
	if mouse_raycast.hit:
		hitting = mouse_raycast.entity.idi
	else:
		hitting = 255
	
	
	
textures = ["Iran", "france", "armen", "argen"]

class cards(Entity):# I;m just praying that this works //LATER// OH GOODNESS IT WORKES
	def __init__(self, position, ido):
		global textures
		super().__init__(
			parent = scene,
			position = position,
			model="quad",
			collider = "cube",
			idi = ido,
			goup = False,
			godown = False,
			texture = textures[ido]
		)
	def picked_up(self):
		self.goup = True
		self.godown = False
	def released(self):
		self.goup = False
		self.godown = True
	def update(self):
		global hitting
		if hitting == self.idi:
			if self.position.y < 0.5:
				self.position = (self.position.x,self.position.y + 0.01,self.position.z)
		#if self.godown:
		else:
			if self.position.y >= 0.0:
				self.position = (self.position.x,self.position.y - 0.01,self.position.z)
			#else:
			#	self.godown = False

game = Ursina()
window.isfullscreen = False
window.borderless = False
window.exit_button.visible = False
window.exit_button.enabled = False
window.fps_counter.visible = True
#Cube = Entity(model = "quad", position = (0,-1,10), texture='Iran')
#"""                     color = color.blue,"""
dock.append(cards((-2,0,10), 0))
dock.append(cards((-1,0,10), 1))
dock.append(cards((1,0,10), 2))
dock.append(cards((2,0,10), 3))
#add rotation here if needed
dock[1].picked_up()
#Windos = Text(text="Windwos XP", position=(0,1,10))
#GOD DAMN WHAT THE FU

game.run()
