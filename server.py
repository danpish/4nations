import socket
import pickle
import threading
import time
from configparser import ConfigParser
import os.path
import random

debugging = True
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP connection(again hopefully)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
server_address = ""  # automatic? maybe?
server_port = 8008
server.bind((server_address, server_port))
server.listen()
conn = []
addr = []
ga_data = []  # an array of data
receiver_threads = [None, None, None, None]
received_data = False
max_player = 2
stop_sending = False
marker_received = False
is_running = True
config_name = "sconfig.txt"
step = 0

# settings values
country_themes = 1
settings = ConfigParser()

"""
    country codes
    IR = 0
    FR = 1
    AM = 2
    AR = 3
"""
players = [[0, 3, 1, 2, ""], [2, 1, 0, 3, ""], [3, 0, 2, 1, ""], [1, 3, 2, 0, ""]]
player_list = [False, False, False, False]
all_players_in = False

"""
Net functions / data[0]
1 = get data
2 = receive request
22 = DATA received
21 = Not accepted Data receive
3 = Send received card
4 = all players has joined
5 = receive marker obtained
6 = card obtained
7 = marker countdown value
8 = send server shutdown (going to be replaced with win message)
81 = ask player username
82 = receive player username
99 = emergency exit
... for further additions
"""


def main():
    global players, player_list, country_themes, settings
    set_settings()
    shuffle_cards()
    join_all_players()
    run_all_receiver_threads()
    ask_player_usernames()
    play()


def shuffle_cards():
    global players
    countries = [max_player, max_player, max_player, max_player]
    countries_condition = max_player * 4
    country_cards = []
    random.seed(time.time())
    while countries_condition:
        random_country = random.randint(0,3)
        if countries[random_country] >= 1:
            countries[random_country] -= 1
            countries_condition -= 1
            country_cards.append(random_country)
    if debugging:
        print("shuffled country results : {}".format(country_cards))
    for each_player in range(max_player):
        for each_card in range(4):
            players[each_player][each_card] = country_cards[each_player * 4 + each_card]


def emergency_exit(error):
    global conn
    for x in range(len(conn)):
        try:
            conn[x].send(pickle.dumps([99, error]))
        except:
            print(f"could not connect to player {x}")
    quit()


def send_to_all(message):
    global conn, max_player
    for each_player in range(max_player):
        try:
            conn[each_player].send(message)
        except socket.error as e:
            emergency_exit(f"could not connect to player {each_player}")


def receiver(receive_from):
    global ga_data, conn, marker_received, is_running

    retries = 0

    while is_running:
        if debugging:
            pass
            """
            uncomment for displaying player server request debug l
                                                                 l
                                                                 V
            """
            # print(f"receiver is receiving data from player {receive_from}")

        l_data = None

        while not l_data and not received_data and not marker_received:
            try:
                l_data = conn[receive_from].recv(1024)
            except socket.error as e:
                print(f"{retries} : receiver failed receiving with error : {e}")
                time.sleep(0.1)
                retries += 1
                if retries > 20:
                    emergency_exit(e)

        if l_data:
            try:
                ga_data.append(pickle.loads(l_data))
            except:
                pass


def set_settings():
    global settings, country_themes
    if os.path.isfile(config_name):
        try:
            settings.read(config_name)
            country_themes = int(settings["SERVER"]["COUNTRY_THEME"])
        except:
            settings["SERVER"] = {"COUNTRY_THEME": str(country_themes)}
            open_file = open(config_name, "w")
            settings.write(open_file)
    else:
        settings["SERVER"] = {"COUNTRY_THEME": str(country_themes)}
        open_file = open(config_name, "w")
        settings.write(open_file)


def insert_card(dock, card):
    removed_stock = 4  # default to last slot

    for cards in range(len(dock)):  # find the first empty slot
        if dock[cards] == "":
            removed_stock = cards
            break

    improved_dock = dock

    if debugging:
        print(improved_dock)  # you know ... make sure we got the right thing

    improved_dock[removed_stock] = card

    return improved_dock


def marker_function():
    global max_player, is_running
    do_marker_countdown = 0
    to_seconds = 0.3
    multiplier = 4
    delta_time = 0
    while do_marker_countdown < to_seconds:
        t0 = time.time()
        do_marker_countdown += delta_time * 0.1 * multiplier
        new_time = do_marker_countdown * 10 / 3
        print(new_time)
        send_to_all(pickle.dumps([7, new_time]))
        delta_time = time.time() - t0
    for all_p in range(max_player):
        for times in range(3):
            conn[all_p].send(pickle.dumps([8]))
            time.sleep(0.01)
    is_running = False


def join_all_players():
    global players, player_list, conn, all_players_in, max_player, country_themes

    while not all_players_in:
        c_conn, c_addr = server.accept()

        if debugging:
            print("got connection from " + str(c_addr))
        if c_conn:
            for x in range(len(player_list)):
                if not player_list[x]:
                    player_list[x] = True
                    c_conn.send(pickle.dumps([1, players[x], x, country_themes]))
                    conn.append(c_conn)
                    break

        if debugging:
            print(len(conn))

        if len(conn) >= max_player:
            if debugging:
                print("we are all in")
            all_players_in = True
            time.sleep(0.2)
            send_to_all(pickle.dumps([4]))


def run_all_receiver_threads():
    global max_player
    for player in range(max_player):
        c_thread = threading.Thread(target=receiver, args=([player]), daemon=True)
        receiver_threads[player] = c_thread
        receiver_threads[player].start()


def ask_player_usernames():
    global conn, ga_data, players, max_player
    asking_players = 0
    while asking_players < max_player:
        time.sleep(0.1)
        conn[asking_players].send(pickle.dumps([81]))
        while ga_data:
            c_data = ga_data[0]
            if c_data[0] == 82:
                if c_data[1] == asking_players:
                    players[asking_players].append(c_data[2])
                    asking_players += 1
            ga_data.pop(0)
    print(f"asking usernames finished with final data : {players}")


server_play_loop = 0


def play():
    global players, player_list, conn, addr, stop_sending, max_player, marker_received, is_running, ga_data, step, server_play_loop

    current_player = 0

    while is_running:

        did_player_answer = False

        if debugging:
            print("now asking player " + f"{current_player}")

        # print(f"current player is {current_player}")

        while not did_player_answer:
            send_to_all(pickle.dumps([2, current_player, step]))

            time.sleep(0.1)  # GOD FORGIVE ME IF THIS IS A MISTAKE

            print(f"server Play loop {server_play_loop}")  # Performance debugging. later this should be removed
            server_play_loop += 1

            if ga_data:
                if debugging:
                    print(f"global array data = {ga_data}")

                c_data = ga_data[0]
                ga_data.pop(0)
                answered_player = c_data[1]

                if c_data[0] == 6:
                    if answered_player == current_player:

                        if debugging:
                            print(f"got some data from player {answered_player}")

                        card_to_send = players[answered_player][c_data[2]]
                        players[answered_player][c_data[2]] = ""

                        conn[answered_player].send(pickle.dumps([22]))

                        if debugging:
                            print(f"sent confirmation to player {answered_player}")

                        did_player_answer = True

                        if answered_player == max_player - 1:
                            conn[0].sendall(pickle.dumps([3, card_to_send]))
                            players[0] = insert_card(players[0], card_to_send)
                        else:
                            conn[answered_player + 1].sendall(pickle.dumps([3, card_to_send]))
                            players[answered_player + 1] = insert_card(players[answered_player + 1], card_to_send)

                        if debugging:
                            print("sent confirmation to the next player")

                    else:
                        if c_data[3] == step - 1 or c_data[3] == step:
                            conn[answered_player].send(pickle.dumps([22]))

                if c_data[0] == 5:
                    marker_received = True
                    if debugging:
                        print("I GOT THE MARKER")
                    marker_function()

        current_player += 1
        if current_player == max_player:
            current_player = 0
        step += 1
        if debugging:
            print(f"step: {step}")


main()
