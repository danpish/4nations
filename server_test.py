import socket
import pickle
import threading
import time

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
"""
    country codes
    IR = 0
    AR = 1
    FR = 2
    AM = 3
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
... for further additions
"""


def join_all_players():
    global players, player_list, conn, addr, all_players_in
    while not all_players_in:
        c_conn, c_addr = server.accept()
        print("got connection from " + str(c_addr))
        for x in range(len(player_list)):
            if not player_list[x]:
                player_list[x] = True
                c_conn.send(pickle.dumps([1, players[x], x]))
                conn.append(c_conn)
                addr.append(c_addr)
                break
        print(len(conn))
        if len(conn) >= max_player:
            print("we are all in")
            all_players_in = True


def receiver(receive_from):  # kind of pathetic. but you got to do what you got to do
    global g_data, conn
    print(type(receive_from))
    conn[receive_from].settimeout(1.0)
    l_data = None
    while not l_data and not received_data:
        try:
            l_data = conn[receive_from].recv(1024)
        except socket.error as e:
            print(f"{e}")
    if l_data:
        g_data = pickle.loads(l_data)


def send_to_all(message):
    global conn
    for x in range(len(conn)):
        conn[x].send(message)


def insert_card(dock, card):
    removed_stock = 4
    for cards in range(len(dock)):
        if dock[cards] == "":
            removed_stock = cards
            break
    improved_dock = dock
    print(improved_dock)
    improved_dock[removed_stock] = card
    return improved_dock


def send_terminator_timer():
    global stop_sending
    time.sleep(0.1)
    stop_sending = True


def play():
    global players, player_list, conn, addr, g_data, stop_sending
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
        print("now asking player " + f"{current_player}")
        while not did_player_answer:
            send_to_all(pickle.dumps([2, current_player]))
            if g_data:
                c_data = g_data
                for threads in range(len(receiver_threads)):
                    receiver_threads[threads] = None
                if c_data[1] == current_player:
                    print(players)
                    print("got some data from ", end="")
                    print(f"player {g_data[1]}")
                    print(type(players[c_data[1]][c_data[0]]))
                    card_to_send = players[c_data[1]][c_data[0]]
                    players[c_data[1]][c_data[0]] = ""
                    send_termination_counter = threading.Thread(target=send_terminator_timer, args=())
                    send_termination_counter.start()
                    while not stop_sending:
                        conn[c_data[1]].send(pickle.dumps([22]))
                    stop_sending = False
                    print(f"sent confirmation to player {c_data[1]}")
                    did_player_answer = True
                    print("send the received card to the next player")
                    if c_data[1] == max_player - 1:
                        conn[0].send(pickle.dumps([3, card_to_send]))
                        players[0] = insert_card(players[0], card_to_send)
                    else:
                        conn[c_data[1] + 1].send(pickle.dumps([3, card_to_send]))
                        players[c_data[1] + 1] = insert_card(players[c_data[1] + 1], card_to_send)
                elif c_data[1] != current_player:
                    # print(f"wrong player player {c_data[1]}")
                    conn[c_data[1]].send(pickle.dumps([21]))
                else:
                    print("unknown")
        current_player += 1
        if current_player == max_player:
            current_player = 0


def main():
    global players, player_list
    join_all_players()
    play()


main()
