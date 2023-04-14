"""
Network test
"""
from ursina import *
import socket
import pickle
import threading
import time
current_dock = [1,2,3,0,0]
recived_dock = [1,2,3,0,0]
was_mouse_down = True
send_card = False
connected_ID = 255
testing = False
g_data = None
card_mode = "round" #Options = round , card
music_enabled = False

def card_movement_diagram(value):
	return (value - 1.6)**3 * (1/8) + 0.5

def update():
    global camera_position_z,g_data,send_card
    camera_position_z = 0
    camera.position = (0,0,camera_position_z)
    if g_data:
        #print(f"{g_data} {connected_ID}")
        your_turn_text.enabled = g_data[1] == connected_ID
        send_card = g_data[1] == connected_ID
    else:
        send_card = False

textures = ["ir", "fr", "am", "ar"]
card_textures = ["iran", "france", "armenia", "argentina"]

class scoket_client():
    def __init__(self, sock=None, addr = "127.0.0.1", port = 8008):
        if sock == None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        else:
            self.sock = sock
        #self.sock.setblocking(0) GOD HELP
        self.addr = "127.0.0.1"
        self.port = 8008

    def connect(self):
        self.sock.connect((self.addr, self.port))
        #Clean code! Am I doing this correctly?

    def send_data(self, data):
        to_send_data = pickle.dumps(data)
        self.sock.send(to_send_data)

    def recive_data(self):
        data = self.sock.recv(8126)
        return data

client = scoket_client()


class cards(Entity):
    def __init__(self, position, ido, xpos, slot_position):
        global textures,card_mode, card_textures
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
        if card_mode == "card":
            self.model = "quad"
            self.collider = "cube"
            self.texture = card_textures[self.idi]
    def update(self):
        global is_mouse_down, was_mouse_down, send_card, card_mode

        if held_keys['r']:
            self.xpos = 0
        movement_speed = 4 * time.dt
        if card_mode == "round":
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
                if not testing:
                    if do_delete and send_card:
                        client.send_data([self.idi, connected_ID])
                        print("i should send data")
                        msg = pickle.loads(client.recive_data())
                        if msg:
                            if msg[0] == 22:
                                send_card = False
                                self.disable()
                            elif msg[0] == 21:
                                print("not your turn")
                else:
                    self.disable()

game = Ursina()


def on_begin():
    global recived_dock
    time.sleep(0.1)
    Main_menu_back.enabled = False
    current_dock[0]=(cards((-1.5,0,10), int(recived_dock[0]),0,0))
    current_dock[1]=(cards((-0.5,0,10), int(recived_dock[1]),0,1))
    current_dock[2]=(cards((0.5,0,10), int(recived_dock[2]),0,2))
    current_dock[3]=(cards((1.5,0,10), int(recived_dock[3]),0,3))
    table = Entity(model="table", position=Vec3(0,-2.8,10), texture="tabletop.png")

def reset_menu_UI():
    Main_menu_host.enabled = False
    Main_menu_join.enabled = False
    Main_menu_text.enabled = False
    Main_menu_go_back.enabled = False
    Main_menu_start.enabled = False
    Main_menu_settings.enabled = False
    Main_menu_exit.enabled = False

    Settings_menu_title.enabled = False
    Settings_menu_back.enabled = False
    Settings_menu_card_button.enabled = False
    Settings_menu_card_title.enabled = False
    Settings_menu_card_stat.enabled = False
    Settings_menu_music.enabled = False
    Settings_menu_music_title.enabled = False
    Settings_menu_super.enabled = False
    Settings_menu_super_title.enabled = False
    Settings_menu_super_stat.enabled = False


def on_start():
    reset_menu_UI()
    Main_menu_text.enabled = True
    Main_menu_host.enabled = True
    Main_menu_join.enabled = True
    Main_menu_go_back.enabled = True

def show_main_menu():
    reset_menu_UI()
    Main_menu_start.enabled = True
    Main_menu_text.enabled = True
    Main_menu_settings.enabled = True
    Main_menu_exit.enabled = True

def open_settings_menu():
    reset_menu_UI()
    Settings_menu_title.enabled = True
    Settings_menu_back.enabled = True
    Settings_menu_card_button.enabled = True
    Settings_menu_card_title.enabled = True
    Settings_menu_card_stat.enabled = True
    Settings_menu_music.enabled = True
    Settings_menu_music_title.enabled = True
    Settings_menu_super.enabled = True
    Settings_menu_super_title.enabled = True
    Settings_menu_super_stat.enabled = True


def card_mode_change():
    global card_mode
    if card_mode == "round":
        card_mode = "card"
    else:
        card_mode = "round"
    Settings_menu_card_stat.text = card_mode

def music_mode_change():
    global music_enabled
    music_enabled = not music_enabled
    Settings_menu_music.color = color.red
    if music_enabled:
        Settings_menu_music.color = color.green

def join_function():
    client.connect()
    x = threading.Thread(target=multiplayer_thread, args=())
    time.sleep(0.1)
    x.start()
    on_begin()

def test_function():
    x = threading.Thread(target=single_player_test, args=())
    x.start()
    on_begin()

def single_player_test():
    global testing, send_card
    testing = True
    send_card = True
    time.sleep(0.5)

def multiplayer_thread():
    global send_card, recived_dock, testing, connected_ID, g_data
    testing = False
    while True:
        #time.sleep(0.1)
        try:
            data = client.recive_data()
            #print(pickle.loads(data))
        except socket.error as e:
            print(e)
            data = None
        if data:
            try:
                #print(f"{pickle.loads(data)} {connected_ID}")
                data = pickle.loads(data)
                g_data = data
                if data[0] == 1:
                    connected_ID = data[2]
                    recived_dock = data[1]
                    print(type(recived_dock[1]))
                """
                if data[0] == 2 and data[1] == connected_ID:
                    send_card = True
                """
            except:
                print("for some stupid reason, pickle failed")




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
Main_menu_go_back = Button(parent=Main_menu_back, scale=.2,position=(0,-0.3,-0.1))
join_text = Text(parent=Main_menu_join, text = "join", position=(-0.15, 0.1, 0), scale=5)
host_text = Text(parent=Main_menu_host, text = "host", position=(-0.15, 0.1, 0), scale=5)
back_text = Text(parent=Main_menu_go_back, text = "back", position=(-0.15, 0.1, 0), scale=5)
Main_menu_host.enabled = False
Main_menu_join.enabled = False
Main_menu_go_back.enabled = False
Settings_menu_title = Text(parent=Main_menu_back, text="Settings", position=(0,0.4,-.1))
Settings_menu_back = Button(parent=Main_menu_back, scale=(.2,.05),position=(0,-.3,-.1))
Settings_menu_back_title = Text(parent=Settings_menu_back, text="BACK", scale = (5,20),position = (-.2,.2,0))

Settings_menu_card_button = Button(parent=Main_menu_back, scale=.2,position=(0.3,0.1,-0.1))
Settings_menu_card_title = Text(parent=Main_menu_back,position=(-.3,0.1,-.1),text="Card mode")
Settings_menu_card_stat = Text(parent=Settings_menu_card_button,scale = 5,position=(-.3,0,-.1),text=card_mode)
Settings_menu_music = Button(parent=Main_menu_back, scale=.2,position=(0.3,-0.1,-0.1),color=color.red)
Settings_menu_music_title = Text(parent=Main_menu_back,position=(-.3,-0.1,-.1),text="music")
Settings_menu_super = Button(parent=Main_menu_back, scale=.2,position=(0.3,-0.3,-0.1))
Settings_menu_super_title = Text(parent=Main_menu_back,position=(-.3,-0.3,-.1),text="Super mode")
Settings_menu_super_stat = Text(parent=Settings_menu_super,scale = 5,position=(-.3,0,-.1),text="Never")

Settings_menu_title.enabled = False
Settings_menu_back.enabled = False
Settings_menu_card_button.enabled = False
Settings_menu_card_title.enabled = False
Settings_menu_card_stat.enabled = False
Settings_menu_music.enabled = False
Settings_menu_music_title.enabled = False
Settings_menu_super.enabled = False
Settings_menu_super_title.enabled = False
Settings_menu_super_stat.enabled = False

Settings_menu_music.on_click = music_mode_change
Settings_menu_card_button.on_click = card_mode_change

your_turn_text = Text(text = "your turn", position=(-.5,0.5,0), color=color.green)
your_turn_text.enabled = False

#For god sake button text is glitched. So we define our own
start_text = Text(parent=Main_menu_start, text = "StARt", position=(-0.15, 0.1, 0), scale=5)
settings_text = Text(parent=Main_menu_settings, text = "SEttINGS", position=(-0.15, 0.1, 0), scale=5)
exit_text  = Text(parent=Main_menu_exit, text = "EXIt", position=(-0.15, 0.1, 0), scale=5)

Main_menu_exit.on_click = application.quit
Main_menu_start.on_click = on_start
#Main_menu_join.on_click = lambda:on_begin([0,1,2,3])
Main_menu_join.on_click = test_function
Main_menu_host.on_click = join_function
Main_menu_go_back.on_click = show_main_menu
Main_menu_settings.on_click = open_settings_menu
Settings_menu_back.on_click = show_main_menu





Sky()
game.run()
