import socket
import pickle
import threading
import time
from configparser import ConfigParser
import os.path

debugging = False
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP connection(again hopefully)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
server_address = ""  # automatic? maybe?
server_port = 8008
server.bind((server_address, server_port))
server.listen()
conn = []
addr = []
g_data = None
receiver_threads = [None, None, None, None]
received_data = False
max_player = 2
stop_sending = False
marker_received = False
config_name = "sconfig.txt"

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
99 = emergency exit
... for further additions
"""


def join_all_players():
    global players, player_list, conn, addr, all_players_in, max_player, country_themes

    while not all_players_in:

        c_conn, c_addr = server.accept()

        if debugging:
            print("got connection from " + str(c_addr))

        for x in range(len(player_list)):
            if not player_list[x]:
                player_list[x] = True
                c_conn.send(pickle.dumps([1, players[x], x, country_themes]))
                conn.append(c_conn)
                addr.append(c_addr)
                break

        if debugging:
            print(len(conn))

        if len(conn) >= max_player:
            if debugging:
                print("we are all in")
            all_players_in = True
            time.sleep(0.2)
            send_to_all(pickle.dumps([4]))


def receiver(receive_from):  # kind of pathetic. but you got to do what you got to do
    global g_data, conn, marker_received

    if debugging:
        print(type(receive_from))

    l_data = None

    while not l_data and not received_data and not marker_received:
        try:
            l_data = conn[receive_from].recv(1024)
        except socket.error as e:
            print(f"{e}")

    if l_data:
        g_data = pickle.loads(l_data)


def emergency_exit():
    global conn
    for x in range(len(conn)):
        try:
            conn[x].send(pickle.dumps([99]))
        except:
            print(f"could not connect to player {x}")
    quit()


def send_to_all(message):
    global conn
    for x in range(len(conn)):
        try:
            conn[x].send(message)
        except socket.error as e:
            emergency_exit()


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


def send_to_seconds(message, seconds, person):
    global conn
    person = int(person)
    passed_milli_sec = 0
    while passed_milli_sec < seconds:
        time.sleep(0.01)
        passed_milli_sec += 0.01
        conn[person].send(message)


def marker_function():
    global max_player
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
        send_to_seconds(pickle.dumps([8]), 0.1, all_p)
    quit()


def play():
    global players, player_list, conn, addr, g_data, stop_sending, max_player, marker_received

    current_player = 0
    answered_player = 0
    did_player_answer = False
    card_to_send = ""

    while True:
        card_to_send = ""

        if not receiver_threads[current_player]:
            c_thread = threading.Thread(target=receiver, args=([current_player]), daemon=True)
            receiver_threads[current_player] = c_thread
            c_thread = None
            receiver_threads[current_player].start()

        did_player_answer = False

        if debugging:
            print("now asking player " + f"{current_player}")

        while not did_player_answer:
            send_to_all(pickle.dumps([2, current_player]))
            if g_data:
                c_data = g_data
                if c_data[1] == current_player:
                    if c_data[0] == 6:
                        if debugging:
                            print(players)
                            print("got some data from ", end="")
                            print(f"player {g_data[1]}")
                            print(players[c_data[1]][c_data[2]])
                        card_to_send = players[c_data[1]][c_data[2]]
                        players[c_data[1]][c_data[2]] = ""

                        send_to_seconds(pickle.dumps([22]), 0.01, c_data[1])

                        if debugging:
                            print(f"sent confirmation to player {c_data[1]}")

                        did_player_answer = True
                        receiver_threads[current_player] = None

                        if debugging:
                            print("send the received card to the next player")

                        if c_data[1] == max_player - 1:  # if the player is the last one
                            # conn[0].send(pickle.dumps([3, card_to_send]))  # send the card to first one instead
                            send_to_seconds(pickle.dumps([3, card_to_send]), 0.1, 0)
                            players[0] = insert_card(players[0], card_to_send)
                        else:
                            # conn[c_data[1] + 1].send(pickle.dumps([3, card_to_send]))
                            send_to_seconds(pickle.dumps([3, card_to_send]), 0.1, c_data[1] + 1)
                            players[c_data[1] + 1] = insert_card(players[c_data[1] + 1], card_to_send)
                    elif c_data[0] == 5:
                        marker_received = True
                        if debugging:
                            print("I GOT THE MARKER")
                        marker_function()
                elif c_data[1] != current_player:
                    send_to_seconds(pickle.dumps([21]), 0.1, c_data[1])
                else:
                    print("unknown")

        current_player += 1
        if current_player == max_player:
            current_player = 0


def set_settings():
    global settings, country_themes
    if os.path.isfile(config_name):
        try:
            settings.read(config_name)
            country_themes = int(settings["SERVER"]["COUNTRY_THEME"])
        except:
            settings["SERVER"] = { "COUNTRY_THEME" : country_themes }
            open_file = open(config_name, "w")
            settings.write(open_file)
    else:
        settings["SERVER"] = {"COUNTRY_THEME": country_themes}
        open_file = open(config_name, "w")
        settings.write(open_file)


def main():
    global players, player_list, country_themes, settings
    set_settings()
    join_all_players()
    play()


main()
