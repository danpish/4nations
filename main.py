"""
Hello I'm Daniel and today im going to make this game with ursina engine
just because i hate my self and decided to suffer to make a game
with an engine that i dont really know and a mountain of exams on the horizon
with a terrible mental health tooo 
"""
from ursina import *
dock = ["","","","",""]
#hitting = 255
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
	""" Never mind. Ursina worked from the first place
	mouse_origin = Vec3(0,0,0,)
	mouseRad  = Vec3(math.radians(mouse.x), math.radians(mouse.y),0)
	cast_direction = (mouseRad.x, mouseRad.y,0.0285)#yes its done
	mouse_raycast = raycast(mouse_origin, cast_direction, debug=True)
	if mouse_raycast.hit:
		hitting = mouse_raycast.entity.idi
	else:
		hitting = 255
	"""

textures = ["ir", "fr", "am", "ar"]

class cards(Entity):# I;m just praying that this works //LATER// OH GOODNESS IT WORKES
	def __init__(self, position, ido, xpos, slot_position):
		global textures
		super().__init__(
			parent = scene,
			position = position,
			model="sphere",
			collider = "sphere",
			idi = ido,
			texture = textures[ido],
			xpos = xpos,
			slot_position = slot_position
		)
	def update(self):
		global mouse_down, was_mouse_down
		movement_speed = 4 * time.dt
		self.rotation = Vec3(0,self.rotation.y + (movement_speed * 16),0)
		if self.hovered:
			if self.xpos < 1.0:
				self.xpos += movement_speed
		else:
			if self.xpos > 0.0:
				self.xpos -= movement_speed
		if self.xpos < 0.0:#Fail safe
			self.xpos = 0.0
		elif self.xpos > 5.0:
			self.xpos = 5.0
		self.position = (self.position.x,ofset(self.xpos),self.position.z)
		if self.hovered:
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

def on_start():
	Main_menu_back.disable()
	dock[0]=(cards((-1.5,0,10), 0,0,0))
	dock[1]=(cards((-0.5,0,10), 1,0,1))
	dock[2]=(cards((0.5,0,10), 2,0,2))
	dock[3]=(cards((1.5,0,10), 3,0,3))
	table = Entity(model="table", position=Vec3(0,-2.8,10), texture="tabletop.png")
window.isfullscreen = False
window.borderless = False
window.exit_button.visible = False
window.exit_button.enabled = False
window.fps_counter.visible = True
#Main menu
Main_menu_back = Entity(model="quad", color=color.gray,position=(0,0,3))
Main_menu_text = Text(parent=Main_menu_back,position=(0,0.4,-0.1), text="4NATIONS DEV")
Main_menu_start = Button(parent=Main_menu_back, scale=.2,position=(0,0.1,-0.1))
Main_menu_settings = Button(parent=Main_menu_back,scale=.2,position=(0,-0.1,-0.1))
Main_menu_exit = Button(parent=Main_menu_back, scale=.2,position=(0,-0.3,-0.1))
#For god sake button text is glitched
start_text = Text(parent=Main_menu_start, text = "StARt", position=(-0.15, 0.1, 0), scale=5)
settings_text = Text(parent=Main_menu_settings, text = "SEttINGS", position=(-0.15, 0.1, 0), scale=5)
exit_text  = Text(parent=Main_menu_exit, text = "EXIt", position=(-0.15, 0.1, 0), scale=5)
#Button actions(Missing settings)
Main_menu_exit.on_click = application.quit
Main_menu_start.on_click = on_start
Sky()
game.run()
