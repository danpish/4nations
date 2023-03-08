"""
Network test
"""
from ursina import *
import socket
import pickle
import threading
current_dock = [0,0,0,0,0]
recived_dock = [0,0,0,0,0]
was_mouse_down = True
send_card = False
connected_ID = 255


def card_movement_diagram(value):
	return (value - 1.6)**3 * (1/8) + 0.5

def update():
	global camera_position_z
	camera_position_z = 0
	camera.position = (0,0,camera_position_z)

textures = ["ir", "fr", "am", "ar"]

def setup_server_client():
	global client, server_port , server_address
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#TCP connection(hopefully)
	server_port = 8008
	server_address = "127.0.0.1"#Later to be replaced with user given address

def server_connect():
	client.connect((server_address, server_port))
	#Clean code! Am I doing this correctly?

def send_data(data):
	send_data = data.encode()
	client.send(send_data)

def recive_data():
	data = b""
	while True:
		part = client.recv(1024)
		data += part
		if len(part) < 1024:
			#Copied from stackoverflow, I don't undrestand this
			break
	return data



class cards(Entity):
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
		global is_mouse_down, was_mouse_down, send_card

		if held_keys['r']:
			self.xpos = 0

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
		self.position = (self.position.x,card_movement_diagram(self.xpos),self.position.z)
		if self.hovered:
			if mouse.left:
				#I don't know if Ursina has it predefined but here it goes, self made click function
				is_mouse_down = True
				was_mouse_down = False
			else:
				is_mouse_down = False
			if not is_mouse_down and not was_mouse_down:
				was_mouse_down = True
				do_delete = False
				if self.position.x == -1.5 and current_dock[0] != "":
					current_dock[0] = ""
					do_delete = True
				elif self.position.x == -0.5 and current_dock[1] != "":
					current_dock[1] = ""
					do_delete = True
				elif self.position.x == 0.5 and current_dock[2] != "":
					current_dock[2] = ""
					do_delete = True
				elif self.position.x == 1.5 and current_dock[3] != "":
					current_dock[3] = ""
					do_delete = True
				if do_delete and send_card:
					client.send(self.idi)
					msg = pickle.loads(recive_data())
					if msg:
						if msg[0] == 22:
							send_card = False
							self.disable()
game = Ursina()

def on_begin():
	global recived_dock
	Main_menu_back.disable()
	current_dock[0]=(cards((-1.5,0,10), int(recived_dock[0]),0,0))
	current_dock[1]=(cards((-0.5,0,10), int(recived_dock[1]),0,1))
	current_dock[2]=(cards((0.5,0,10), int(recived_dock[2]),0,2))
	current_dock[3]=(cards((1.5,0,10), int(recived_dock[3]),0,3))
	table = Entity(model="table", position=Vec3(0,-2.8,10), texture="tabletop.png")

def on_start():
	Main_menu_host.enabled = True
	Main_menu_join.enabled = True
	Main_menu_back_dere.enabled = True
	Main_menu_start.enabled = False
	Main_menu_settings.enabled = False
	Main_menu_exit.enabled = False

def join_function():
	setup_server_client()
	server_connect()
	x = threading.Thread(target=multiplayer_thread, args=())
	x.start()
	on_begin()


def multiplayer_thread():
    global send_card, recived_dock
    while True:
        print("im still here")
        try:
            print("before data recive")
            client.setblocking(0)
            data = b""
            while True:
                part = client.recv(1024)
                print("cmon do something")
                data += part
                if len(part) < 1024:
                    #Copied from stackoverflow, I don't undrestand this
                    break
            print("after data revcive")
        except socket.error as e:
            print(e)
            data = None
        if data:
            print(pickle.loads(data))
            data = pickle.loads(data)
            if data[0] == 1:
                connected_ID = data[2]
                recived_dock = data[1]
                print(type(recived_dock[1]))
            if data[0] == 2:
                send_card = True



window.isfullscreen = False
window.borderless = False
window.exit_button.visible = False
window.exit_button.enabled = False
window.fps_counter.visible = True
#Main menu
#Oh ...erm ... Apparently, according to clean code, comments are for losers
Main_menu_back = Entity(model="quad", color=color.gray,position=(0,0,3))
Main_menu_text = Text(parent=Main_menu_back,position=(0,0.4,-0.1), text="4NATIONS DEV")
Main_menu_start = Button(parent=Main_menu_back, scale=.2,position=(0,0.1,-0.1))
Main_menu_settings = Button(parent=Main_menu_back,scale=.2,position=(0,-0.1,-0.1))
Main_menu_exit = Button(parent=Main_menu_back, scale=.2,position=(0,-0.3,-0.1))
#join and host options
Main_menu_host = Button(parent=Main_menu_back, scale=.2,position=(0,0.1,-0.1))
Main_menu_join = Button(parent=Main_menu_back, scale=.2,position=(0,-0.1,-0.1))
Main_menu_back_dere = Button(parent=Main_menu_back, scale=.2,position=(0,-0.3,-0.1))
join_text = Text(parent=Main_menu_join, text = "join", position=(-0.15, 0.1, 0), scale=5)
host_text = Text(parent=Main_menu_host, text = "host", position=(-0.15, 0.1, 0), scale=5)
back_text = Text(parent=Main_menu_back_dere, text = "back", position=(-0.15, 0.1, 0), scale=5)
Main_menu_host.enabled = False
Main_menu_join.enabled = False
Main_menu_back_dere.enabled = False
#For god sake button text is glitched. So we define our own
start_text = Text(parent=Main_menu_start, text = "StARt", position=(-0.15, 0.1, 0), scale=5)
settings_text = Text(parent=Main_menu_settings, text = "SEttINGS", position=(-0.15, 0.1, 0), scale=5)
exit_text  = Text(parent=Main_menu_exit, text = "EXIt", position=(-0.15, 0.1, 0), scale=5)
#Button actions(Missing settings)
Main_menu_exit.on_click = application.quit
Main_menu_start.on_click = on_start
Main_menu_join.on_click = lambda:on_begin([0,1,2,3])
Main_menu_host.on_click = join_function
Sky()
game.run()
