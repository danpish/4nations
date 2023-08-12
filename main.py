"""
4Nations
Developed by Daniel pishyar 2022-2023
Using ursina engine 5.x - python 3.10
"""
from ursina import *
import socket
import pickle
import threading
import time
from configparser import ConfigParser
import os.path

current_dock = [None, None, None, None, None]  # Dock data currently in the client
received_dock = [1, 2, 3, 0, 0]  # Dock data received from the server

current_step = 0

# Game values
is_mouse_down = False
was_mouse_down = True
send_card = False  # Global card sending permission
connected_ID = 255
testing = False
g_data = None
do_delete_card = 0  # Values = 0(invalid)/ 2(correct)/ 1(incorrect)
did_receive_4 = False
marker_counting_down = False
count_down_value = 0
timer_exist = None
o_marker = None
is_server_shut_down = False
config_name = "cconfig.txt"

settings = ConfigParser()

# Settings values
card_mode = "round"  # Options = round , card
music_enabled = False
card_rotation_speed = 1
debugging_enabled = False


def card_movement_diagram(value):
    return (value - 1.6) ** 3 * (1 / 8) + 0.5


def update():
    global g_data, send_card, did_receive_4, timer_exist, o_marker, current_step
    camera.position = (0, 0, 0)
    if g_data:
        u_data = g_data
        if len(u_data) > 1:  # be sure it's not confirmation message and waiting for players
            if debugging_enabled:
                print(u_data)
            if u_data[0] == 7 and not timer_exist:
                timer_exist = timer(o_marker)

            your_turn_text.enabled = u_data[1] == connected_ID
            send_card = u_data[1] == connected_ID

    else:
        send_card = False
    if did_receive_4:
        did_receive_4 = False
        waiting_for_players.visible = False
        for cards in range(4):
            current_dock[cards].visible = True


textures = ["ir", "fr", "am", "ar"]  # country BALL texture
card_textures = ["iran_card", "france_card", "armenia_card", "argentina_card"]  # country CARDS texture


class Socket_Client:
    def __init__(self, sock=None):
        if not sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        else:
            self.sock = sock

    def connect(self, address, port):
        self.sock.connect((address, port))

    def send_data(self, data):
        to_send_data = pickle.dumps(data)
        self.sock.send(to_send_data)

    def receive_data(self):
        data = self.sock.recv(8126)
        return data


client = Socket_Client()


class Cards(Entity):
    def __init__(self, position, ido, slot_position):
        global textures, card_mode, card_textures, is_mouse_down, was_mouse_down
        super().__init__(
            parent=scene,
            position=position,
            model="sphere",
            collider="sphere",
            idi=ido,
            texture=textures[ido],
            xpos=0,
            slot_position=slot_position,
            static_y_position=position[1]
        )
        if card_mode == "card":
            self.model = "quad"
            self.collider = "cube"
            self.texture = card_textures[self.idi]
            self.scale = (1, 2, 1)
        is_mouse_down, was_mouse_down = False, True

    def is_clicked(self):
        global is_mouse_down, was_mouse_down

        if not self.hovered:
            return False
        if not is_mouse_down and not was_mouse_down:
            was_mouse_down = True
            return True
        if mouse.left:
            is_mouse_down = True
            was_mouse_down = False
            return False
        else:
            is_mouse_down = False
            return False

    def update(self):
        global is_mouse_down, was_mouse_down, send_card, card_mode, g_data, do_delete_card, connected_ID, debugging_enabled, card_rotation_speed

        if held_keys["r"]:
            self.xpos = 0
        movement_speed = 4 * time.dt
        if card_mode == "round":
            self.rotation = Vec3(0, self.rotation.y + (movement_speed * 16) * card_rotation_speed, 0)
        if self.hovered:
            if self.xpos < 1.0:
                self.xpos += movement_speed
        else:
            if self.xpos > 0.0:
                self.xpos -= movement_speed

        if self.xpos < 0.0:  # Fail safe
            self.xpos = 0.0
        elif self.xpos > 5.0:
            self.xpos = 5.0

        self.position = (
            self.position.x,
            self.static_y_position + card_movement_diagram(self.xpos) + (int(card_mode == "card") * 0.5),
            self.position.z,
        )
        if self.is_clicked() and self.visible:
            do_delete = False

            if current_dock[self.slot_position] != "":
                do_delete = True

            if not testing:
                if do_delete and send_card:

                    if debugging_enabled:
                        print(f"i should send data and my ID is : {connected_ID}")

                    while do_delete_card == 0 :
                        time.sleep(0.1)
                        client.send_data([6, connected_ID, self.slot_position, current_step])

                        if debugging_enabled:
                            print(f"client side do_send_card = {do_delete_card}")

                    if do_delete_card:
                        if do_delete_card == 1:
                            send_card = False
                            print("done")
                            current_dock[self.slot_position] = ""
                            self.disable()
                        elif do_delete_card == 2:
                            print("not your turn")
                            send_card = False
            else:
                if do_delete:
                    if debugging_enabled:
                        # for debugging showing if there is a card in a slot
                        # not showing the entire information.
                        dock_status = [False, False, False, False]
                        for cards_in_deck in range(4):
                            if current_dock[cards_in_deck] != "":
                                dock_status[cards_in_deck] = True
                        print(dock_status)
                    self.disable()


game = Ursina(title="4Nations - dev")


class marker(Entity):
    def __init__(self, position):
        global is_mouse_down, was_mouse_down
        super().__init__(
            position=position,
            model="marker",
            collider="marker",
            scale=.2
        )
        is_mouse_down, was_mouse_down = False, True

    def marker_clicked(self):
        n_timer = timer(self)

    def is_clicked(self):
        global is_mouse_down, was_mouse_down

        if not self.hovered:
            return False
        if not is_mouse_down and not was_mouse_down:
            was_mouse_down = True
            return True
        if mouse.left:
            is_mouse_down = True
            was_mouse_down = False
            return False
        else:
            is_mouse_down = False
            return False

    def update(self):
        global is_mouse_down, was_mouse_down, testing
        if self.is_clicked():
            if testing:
                self.marker_clicked()
            else:
                client.send_data([5, connected_ID])


class timer(Entity):
    def __init__(self, marker):
        super().__init__(
            parent=marker,
            position=(0, 0, -2),
            model="circle",
            color=color.dark_gray,
            scale=3,
        )
        self.child_scale = 0
        self.child = Entity(parent=self, position=(0, 0, -0.01), scale=self.child_scale, color=color.green,
                            model="circle")

    def update(self):
        global count_down_value, marker_counting_down, testing
        if self.child_scale >= 1:
            self.disable()
        self.child.scale = self.child_scale
        if testing:
            self.child_scale += 2 * time.dt
        else:
            self.child_scale = count_down_value


def on_begin(testing):
    global received_dock, is_mouse_down, was_mouse_down, o_marker, table
    reset_menu_ui()
    Main_menu_back.enabled = False

    current_dock[0] = Cards((-2, 0, 10), int(received_dock[0]), 0)
    current_dock[1] = Cards((-0.9, 0, 10), int(received_dock[1]), 1)
    current_dock[2] = Cards((0.9, 0, 10), int(received_dock[2]), 2)
    current_dock[3] = Cards((2, 0, 10), int(received_dock[3]), 3)

    Ingame_back.enabled = True
    if not testing:
        Ingame_back.text = "Exit"
        for cards in range(4):
            current_dock[cards].visible = False
        waiting_for_players.visible = True

    o_marker = marker((0, 0.2, 10))
    table = Entity(model="table", position=Vec3(0, -2.8, 10), texture="tabletop.png")


def card_adder(new_card_id):
    global current_dock
    empty_slot = 4  # default empty slot as 5th card
    position_placement_x = 0
    position_placement_y = 0
    for cards_in_deck in range(len(current_dock) - 1):  # search in 4 main cards
        if current_dock[cards_in_deck] == "":
            empty_slot = cards_in_deck
    if empty_slot == 0:
        position_placement_x = -2
    elif empty_slot == 1:
        position_placement_x = -0.9
    elif empty_slot == 2:
        position_placement_x = 0.9
    elif empty_slot == 3:
        position_placement_x = 2
    else:
        position_placement_x = 2.9
        position_placement_y = 0

    current_dock[empty_slot] = Cards((position_placement_x, position_placement_y, 10), new_card_id, empty_slot)


def reset_menu_ui():
    Main_menu_test.enabled = False
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
    Settings_menu_card_rotation_speed.enabled = False

    Joingame_input_port.enabled = False
    Joingame_input_address.enabled = False
    Joingame_join_address_port.enabled = False
    Joingame_back_address_port.enabled = False

    Server_shutdown_message.enabled = False
    Server_shutdown_exit.enabled = False
    Server_shutdown_back.enabled = False

    Countryselect_test_button.enabled = False
    Countryselect_select_1.enabled = False
    Countryselect_select_2.enabled = False
    Countryselect_back_button.enabled = False


def exit_game(dont_exit=False):
    global testing
    for cards in range(4):
        if current_dock[cards]:
            current_dock[cards].disable()
    if o_marker and table:
        o_marker.disable()
        table.disable()
    Main_menu_back.enabled = True
    reset_menu_ui()
    show_main_menu()
    Ingame_back.enabled = False
    if not testing and not dont_exit:
        application.quit()


def server_shut_down(message):
    global is_server_shut_down
    is_server_shut_down = True
    exit_game(True)
    Main_menu_back.enabled = True
    reset_menu_ui()
    Server_shutdown_exit.enabled = True
    Server_shutdown_message.enabled = True
    Server_shutdown_message.text = f"server shut down with \n error message: {message}"
    Server_shutdown_back.enabled = True


def on_start():
    reset_menu_ui()
    Main_menu_text.enabled = True
    Main_menu_test.enabled = True
    Main_menu_join.enabled = True
    Main_menu_go_back.enabled = True
    # Countryselect_test_button.enabled = True


def show_main_menu():
    reset_menu_ui()
    Main_menu_start.enabled = True
    Main_menu_text.enabled = True
    Main_menu_settings.enabled = True
    Main_menu_exit.enabled = True


def change_countries(value):
    global textures
    if value == 1:
        textures = ["ir", "fr", "am", "ar"]
        Countryselect_select_1.color = color.black90
        Countryselect_select_2.color = color.black66
    elif value == 2:
        textures = ["ph", "bt", "kz", "rs"]
        Countryselect_select_2.color = color.black90
        Countryselect_select_1.color = color.black66


def open_settings_menu():
    reset_menu_ui()
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
    Settings_menu_card_rotation_speed.enabled = True


def change_ball_country_rotate():
    global card_rotation_speed, settings, config_name
    card_rotation_speed = Settings_menu_card_rotation_speed.value
    settings["CLIENT"]["CARD_SPEED"] = f"{Settings_menu_card_rotation_speed.value}"
    config_file = open(config_name, "w")
    settings.write(config_file)


def open_join_menu():
    reset_menu_ui()
    Joingame_input_address.enabled = True
    Joingame_input_port.enabled = True
    Joingame_join_address_port.enabled = True
    Joingame_back_address_port.enabled = True


def card_mode_change():
    global card_mode, settings, config_name
    if card_mode == "round":
        card_mode = "card"
    else:
        card_mode = "round"
    Settings_menu_card_stat.text = card_mode
    settings["CLIENT"]["CARD_MODE"] = card_mode
    config_file = open(config_name, "w")
    settings.write(config_file)


def music_mode_change():
    global music_enabled
    music_enabled = not music_enabled
    Settings_menu_music.color = color.red
    if music_enabled:
        Settings_menu_music.color = color.green
    settings["CLIENT"]["MUSIC_ENABLED"] = f"{music_enabled}"
    config_file = open(config_name, "w")
    settings.write(config_file)


def join_function():
    global is_server_shut_down
    is_server_shut_down = False
    address = Joingame_input_address.text
    port = Joingame_input_port.text
    client.connect(address, int(port))
    x = threading.Thread(target=multiplayer_thread, args=(), daemon=True)
    x.start()
    time.sleep(0.1)
    on_begin(False)


def test_function():
    x = threading.Thread(target=single_player_test, args=(), daemon=True)
    x.start()
    on_begin(True)


def single_player_test():
    global testing, send_card
    testing = True
    send_card = True


def test_country_select():
    reset_menu_ui()
    Countryselect_select_1.enabled = True
    Countryselect_select_2.enabled = True
    Countryselect_back_button.enabled = True
    Countryselect_test_button.enabled = True
    Countryselect_test_button.enabled = False


def multiplayer_thread():
    global did_receive_4, send_card, received_dock, testing, connected_ID, g_data, do_delete_card, debugging_enabled, count_down_value, marker_counting_down, is_server_shut_down, current_step
    testing = False
    while not is_server_shut_down:
        try:
            data = client.receive_data()
        except socket.error as e:
            server_shut_down("cannot connect to server")
            data = None
        if data:
            try:
                data = pickle.loads(data)
                g_data = data
                if data[0] == 1:  # connected to server for first time and receiving player info
                    connected_ID = data[2]
                    received_dock = data[1]
                    change_countries(data[3])
                elif data[0] == 2:
                    current_step = data[2]
                elif data[0] == 3:  # received a card. adding it to list and sending confirmation
                    if debugging_enabled:
                        print(f"received {data}")
                    card_adder(data[1])
                elif data[0] == 4:
                    did_receive_4 = True
                elif data[0] == 7:  # server received marker request and is sending countdown result
                    marker_counting_down = True
                    count_down_value = data[1]
                elif data[0] == 8:
                    application.quit()
                elif data[0] == 99:
                    server_shut_down(data[1])
                if send_card:
                    # print(data[0])
                    if data[0] == 22: # received confirmation, card sending request has been successfully transferred
                        do_delete_card = 1
                        time.sleep(
                            0.2)  # wait for cards to work with the information without rewriting with future messages
                else:
                    do_delete_card = 0
            except:
                pass


window.isfullscreen = False
window.borderless = False
window.exit_button.visible = False
window.exit_button.enabled = False
window.fps_counter.visible = True

# settings load and create file when missing
if os.path.isfile(config_name):
    settings.read(config_name)
    try:
        card_mode = settings["CLIENT"]["CARD_MODE"]
        music_enabled = bool(settings["CLIENT"]["MUSIC_ENABLED"] == "True")
        card_rotation_speed = float(settings["CLIENT"]["CARD_SPEED"])
        debugging_enabled = bool(settings["CLIENT"]["DEBUGGING"] == "True")
    except:
        settings["CLIENT"] = {"CARD_MODE": "round", "MUSIC_ENABLED": "False", "CARD_SPEED": 4.0, "DEBUGGING": "False"}
        config_file = open(config_name, "w")
        settings.write(config_file)
else:
    settings["CLIENT"] = {"CARD_MODE": "round", "MUSIC_ENABLED": "False", "CARD_SPEED": 4.0, "DEBUGGING": "False"}
    config_file = open(config_name, "w")
    settings.write(config_file)

# Main menu
# Oh ...erm ... Apparently, according to clean code, comments are for losers
Main_menu_back = Entity(model="quad", color=color.gray, position=(0, 0, 3))
Main_menu_text = Text(parent=Main_menu_back, position=(0, 0.4, -0.1), text="4NATIONS DEV")
Main_menu_start = Button(parent=Main_menu_back, scale=0.2, position=(0, 0.1, -0.1))
Main_menu_settings = Button(parent=Main_menu_back, scale=0.2, position=(0, -0.1, -0.1))
Main_menu_exit = Button(parent=Main_menu_back, scale=0.2, position=(0, -0.3, -0.1))
# join and host options
Main_menu_join = Button(parent=Main_menu_back, scale=0.2, position=(0, 0.1, -0.1))
Main_menu_test = Button(parent=Main_menu_back, scale=0.2, position=(0, -0.1, -0.1))
Main_menu_go_back = Button(parent=Main_menu_back, scale=0.2, position=(0, -0.3, -0.1))
join_text = Text(parent=Main_menu_join, text="join", position=(-0.15, 0.1, 0), scale=5)
test_text = Text(parent=Main_menu_test, text="test", position=(-0.15, 0.1, 0), scale=5)
back_text = Text(parent=Main_menu_go_back, text="back", position=(-0.15, 0.1, 0), scale=5)
Main_menu_test.enabled = False
Main_menu_join.enabled = False
Main_menu_go_back.enabled = False
# settings buttons and functions
Settings_menu_title = Text(parent=Main_menu_back, text="Settings", position=(0, 0.4, -0.1))
Settings_menu_back = Button(parent=Main_menu_back, scale=(0.2, 0.05), position=(0, -0.3, -0.1))
Settings_menu_back_title = Text(parent=Settings_menu_back, text="BACK", scale=(5, 20), position=(-0.2, 0.2, 0))
Settings_menu_card_button = Button(parent=Main_menu_back, scale=0.2, position=(0.3, 0.1, -0.1))
Settings_menu_card_title = Text(parent=Main_menu_back, position=(-0.3, 0.1, -0.1), text="Card mode")
Settings_menu_card_stat = Text(parent=Settings_menu_card_button, scale=5, position=(-0.3, 0, -0.1), text=card_mode)
Settings_menu_music = Button(parent=Main_menu_back, scale=0.2, position=(0.3, -0.1, -0.1), color=color.red)
Settings_menu_music_title = Text(parent=Main_menu_back, position=(-0.3, -0.1, -0.1), text="music")
Settings_menu_super = Button(parent=Main_menu_back, scale=0.2, position=(0.3, -0.3, -0.1))
Settings_menu_super_title = Text(parent=Main_menu_back, position=(-0.3, -0.3, -0.1), text="Super mode")
Settings_menu_super_stat = Text(parent=Settings_menu_super, scale=5, position=(-0.3, 0, -0.1), text="Never")
Settings_menu_card_rotation_speed = Slider(min=0, max=20, default=card_rotation_speed, height=0.025, x=-0.25, y=0.14)
Settings_menu_card_rotation_speed.enabled = False
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
Settings_menu_music.color = color.red
if music_enabled:
    Settings_menu_music.color = color.green

your_turn_text = Text(text="your turn", position=(-0.5, 0.5, 0), color=color.green)
your_turn_text.enabled = False
# For god's sake! button text is glitched. So we define our own
start_text = Text(parent=Main_menu_start, text="Start", position=(-0.15, 0.1, 0), scale=5)
settings_text = Text(parent=Main_menu_settings, text="Settings", position=(-0.15, 0.1, 0), scale=5)
exit_text = Text(parent=Main_menu_exit, text="Exit", position=(-0.15, 0.1, 0), scale=5)
# address bar and port function
Joingame_input_address = InputField(label="address", max_lines=1, character_limit=15, y=.1, default_value="127.0.0.1")
Joingame_input_port = InputField(label="port", max_lines=1, character_limit=6, y=.0, default_value="8008")
Joingame_join_address_port = Button(parent=Main_menu_back, scale=(0.2, 0.1), position=(-0.1, -0.3, -0.1))
Joingame_back_address_port = Button(parent=Main_menu_back, scale=(0.2, 0.1), position=(0.1, -0.3, -0.1))
Joingame_join_button_label = Text(parent=Joingame_join_address_port, text="Join", scale=(5, 20),
                                  position=(-0.2, 0.2, 0))
Joingame_join_regret_label = Text(parent=Joingame_back_address_port, text="Back", scale=(5, 20),
                                  position=(-0.2, 0.2, 0))
Joingame_input_address.enabled = False
Joingame_input_port.enabled = False
Joingame_join_address_port.enabled = False
Joingame_back_address_port.enabled = False
Ingame_back = Button(scale=.1, text="back", position=Vec2(0, 0.45))
Ingame_back.enabled = False
Server_shutdown_message = Text(parent=Main_menu_back, text="server has shut down", scale=2,
                               position=Vec3(-.3, 0, -0.1))
Server_shutdown_back = Button(parent=Main_menu_back, scale=.2, position=Vec3(-0.1, -0.3, -0.1))
Server_shutdown_exit = Button(parent=Main_menu_back, scale=.2, position=Vec3(0.1, -0.3, -0.1))
Server_shutdown_back_text = Text(parent=Server_shutdown_back, text="back", position=(-0.15, 0.1, 0), scale=5)
Server_shutdown_exit_text = Text(parent=Server_shutdown_exit, text="exit", position=(-0.15, 0.1, 0), scale=5)
Server_shutdown_back.enabled = False
Server_shutdown_exit.enabled = False
Server_shutdown_message.enabled = False
Countryselect_test_button = Button(scale=0.1, position=Vec2(0.45, 0.45), text="country \nselect\n test")
Countryselect_back_button = Button(parent=Main_menu_back, position=Vec3(0.0, -0.3, -0.1), scale=.2)
Countryselect_select_1 = Button(parent=Main_menu_back, position=Vec3(0.0, 0.1, -0.1), scale=(0.8, 0.2))
Countryselect_select_2 = Button(parent=Main_menu_back, position=Vec3(0.0, -0.1, -0.1), scale=(0.8, 0.2))
Countryselect_back_text = Text(parent=Countryselect_back_button, text="Back", position=(-0.15, 0.1, 0), scale=5)
Countryselect_1_text = Text(parent=Countryselect_select_1, text="IRAN, ARMENIA, FRANCE, ARGENTINA",
                            position=(-0.45, 0.1, 0), scale=(5 / 4 * 7.3 / 5, 7.3))
Countryselect_2_text = Text(parent=Countryselect_select_2, text="Bhutan, Kazakhstan, Serbia ,Philippines".upper(),
                            position=(-0.45, 0.1, 0), scale=(5 / 4 * 7.3 / 5, 7.3))
Countryselect_select_1.enabled = False
Countryselect_select_2.enabled = False
Countryselect_back_button.enabled = False
Countryselect_test_button.enabled = False

waiting_for_players = Text(text="waiting for players", position=Vec3(-0.2, 0, 10), scale=(2))
waiting_for_players.visible = False

Main_menu_exit.on_click = application.quit
Main_menu_start.on_click = on_start
Main_menu_join.on_click = open_join_menu
Main_menu_test.on_click = test_function
Main_menu_go_back.on_click = show_main_menu
Main_menu_settings.on_click = open_settings_menu
Settings_menu_back.on_click = show_main_menu
Joingame_back_address_port.on_click = on_start
Joingame_join_address_port.on_click = join_function
Ingame_back.on_click = exit_game
Server_shutdown_back.on_click = show_main_menu
Server_shutdown_exit.on_click = application.quit
Countryselect_test_button.on_click = test_country_select
Countryselect_back_button.on_click = on_start
Countryselect_select_1.on_click = lambda: change_countries(1)
Countryselect_select_2.on_click = lambda: change_countries(2)

Settings_menu_card_rotation_speed.on_value_changed = change_ball_country_rotate

Sky()
game.run()
