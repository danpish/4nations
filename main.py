"""
Hello I'm Daniel and today im going to make this game with ursina engine
just because i hate my self and decided to suffer to make a game
with an engine that i dont really know and a mountain of exams on the horizon
with a terrible mental health tooo 
"""
from ursina import *
dock = ["","","","",""]
hitting = 255
a = 0
was_mouse_down = True
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
	cast_direction = (mouseRad.x, mouseRad.y,0.0285)#yes its done
	mouse_raycast = raycast(mouse_origin, cast_direction, debug=True)
	if mouse_raycast.hit:
		hitting = mouse_raycast.entity.idi
	else:
		hitting = 255

textures = ["Iran", "france", "armen", "argen"]

class cards(Entity):# I;m just praying that this works //LATER// OH GOODNESS IT WORKES
	def __init__(self, position, ido, xpos, slot_position):
		global textures
		super().__init__(
			parent = scene,
			position = position,
			model="quad",
			collider = "cube",
			idi = ido,
			texture = textures[ido],
			xpos = xpos,
			slot_position = slot_position
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
		global hitting, mouse_down, was_mouse_down
		movement_speed = 4 * time.dt
		if hitting == self.idi:
			if self.xpos < 1.0:
				self.position = (self.position.x,ofset(self.xpos),self.position.z)
				self.xpos += movement_speed
		else:
			if self.xpos > 0.0:
				self.position = (self.position.x,ofset(self.xpos),self.position.z)
				self.xpos -= movement_speed
		if self.xpos < 0.0:#Fail safe
			self.xpos = 0.0

		if hitting == self.idi:
			if mouse.left:
				mouse_down = True
				was_mouse_down = False
			else:
				mouse_down = False
			if not mouse_down and not was_mouse_down:
				was_mouse_down = True
				do_delete = False
				if self.position.x == -1.5 and dock[0] != "":
					dock[0] = ""
					do_delete = True
				elif self.position.x == -0.5 and dock[1] != "":
					dock[1] = ""
					do_delete = True
				elif self.position.x == 0.5 and dock[2] != "":
					dock[2] = ""
					do_delete = True
				elif self.position.x == 1.5 and dock[3] != "":
					dock[3] = ""
					do_delete = True
				print(dock)
				if do_delete:
					self.disable()
game = Ursina()
window.isfullscreen = False
window.borderless = False
window.exit_button.visible = False
window.exit_button.enabled = False
window.fps_counter.visible = True
#Cube = Entity(model = "quad", position = (0,-1,10), texture='Iran')
#                     color = color.blue
dock[0]=(cards((-1.5,0,10), 0,0,0))
dock[1]=(cards((-0.5,0,10), 1,0,1))
dock[2]=(cards((0.5,0,10), 2,0,2))
dock[3]=(cards((1.5,0,10), 3,0,3))
#add rotation here if needed
table = Entity(model="cube", position=Vec3(0,-4.5,10), scale=8, color = color.brown)
Sky()
game.run()
