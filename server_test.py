import socket
import pickle
import threading
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#TCP connection(again hopefully)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
server_address = ""#automatic? maybe?
server_port = 8008
server.bind((server_address, server_port))
server.listen()
conn = []
addr = []
g_data = None
"""
	country codes
	IR = 0
	AR = 1
	FR = 2
	AM = 3
"""
players = [[0,3,1,2],[2,1,0,3],[3,0,2,1],[1,3,2,0]]
player_list = [False,False,False,False]
all_players_in = False

"""
Net functions / data[0]
1 = get_data
2 = recive_request
22 = DATA recived
... for further additions
"""

def join_all_players():
    global players,player_list,conn,addr,all_players_in
    while not all_players_in:
        c_conn, c_addr = server.accept()
        print("got connection from " + str(c_addr))
        for x in range(len(player_list)):
            if not player_list[x]:
                player_list[x] = True
                c_conn.send(pickle.dumps([1,players[x], x]))
                conn.append(c_conn)
                addr.append(c_addr)
                break
        print(len(conn))
        if len(conn) >= 4:
            print("we are all in")
            all_players_in = True

def reciver():#kind of pathetic. but you got to do what you got to do
    global g_data,conn
    for x in range(len(conn)):
        l_data = conn[x].recv(1024)
    if l_data:
        g_data = pickle.loads(l_data)

def send_to_all(message):
    global conn
    for x in range(len(conn)):
        conn[x].send(message)  

def play():
    global players, player_list, conn, addr, g_data
    current_player = 0
    x = threading.Thread(target=reciver, args=())
    x.start()
    did_player_answer = False
    while True:
        did_player_answer = False
        print("now asking pkayer " + f"{current_player}")
        while not did_player_answer:
            send_to_all(pickle.dumps([2,current_player]))
            #conn.send(pickle.dumps([2,current_player]))
            if g_data:
                if g_data[1] == current_player:
                    players[current_player].remove(g_data[0])
                    conn[current_player].send(pickle.dumps([22]))
        current_player += 1
        if current_player > 4:
            current_player -= 4

def main():
	global players, player_list
	join_all_players()
	play()


main()