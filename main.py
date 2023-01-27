"""
Hello I'm Daniel and today im going to make this game with ursina engine
just because i hate my self and decided to suffer to make a game
with an engine that i dont really know and a mountain of exams on the horizon
with a terrible mental health tooo 
"""
from ursina import *
dock = []
hitting = 255
a = 0
def ofset(value):
	return (value - 1.6)**3 * (1/8) + 0.5
def update():
	global a, g_mouseY, g_mouse, pov_mouseX, pov_mouseY, hitting
	camera.position = (0,0,a)
	#a += 0.1
	#print("mousex " + str(mouse.x) + ": mousey" + str(mouse.y))#for mouse positioning debug
	#lets cast a beam from the mosue
	mouse_origin = Vec3(0,0,0,)
	mouseRad  = Vec3(math.radians(mouse.x), math.radians(mouse.y),0)
	#cast_direction = (mouse.x + mouse.x / 8, mouse.y + mouse.y / 8,2) #It was not supposed to work with this but somehow it did
	cast_direction = (mouseRad.x, mouseRad.y,0.0285)#done?
	mouse_raycast = raycast(mouse_origin, cast_direction, debug=True)
	if mouse_raycast.hit:
		hitting = mouse_raycast.entity.idi
	else:
		hitting = 255

textures = ["Iran", "france", "armen", "argen"]

class cards(Entity):# I;m just praying that this works //LATER// OH GOODNESS IT WORKES
	def __init__(self, position, ido, xpos):
		global textures
		super().__init__(
			parent = scene,
			position = position,
			model="quad",
			collider = "cube",
			idi = ido,
			goup = False,
			godown = False,
			texture = textures[ido],
			xpos = xpos
		)
	"""
	def picked_up(self):
		self.goup = True
		self.godown = False
	def released(self):
		self.goup = False
		self.godown = True
	"""
	def update(self):
		global hitting
		movement_speed = 2 * time.dt
		if hitting == self.idi:
			if self.xpos < 1.0:
				self.position = (self.position.x,ofset(self.xpos),self.position.z)
				self.xpos += movement_speed
		#if self.godown:
		else:
			if self.xpos > 0.0:
				self.position = (self.position.x,ofset(self.xpos),self.position.z)
				self.xpos -= movement_speed
			#else:
			#	self.godown = False
		if self.xpos < 0.0:#Fail safe
			self.xpos = 0.0

game = Ursina()
window.isfullscreen = False
window.borderless = False
window.exit_button.visible = False
window.exit_button.enabled = False
window.fps_counter.visible = True
#Cube = Entity(model = "quad", position = (0,-1,10), texture='Iran')
#                     color = color.blue
dock.append(cards((-2,0,10), 0,0))
dock.append(cards((-1,0,10), 1,0))
dock.append(cards((1,0,10), 2,0))
dock.append(cards((2,0,10), 3,0))
#add rotation here if needed
#Windos = Text(text="Windwos XP", position=(0,1,10))
table = Entity(model="cube", position=Vec3(0,-4.5,10), scale=8, color = color.brown)
Sky()
game.run()
