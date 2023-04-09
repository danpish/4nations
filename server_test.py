import socket
import pickle
import threading
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#TCP connection(again hopefully)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
server_address = ""#automatic? maybe?
server_port = 8008
server.bind((server_address, server_port))
server.listen()
conn = None
addr = None
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
		conn, addr = server.accept()
		print("got connection from " + str(addr))
		for x in range(len(player_list)):
			if not player_list[x]:
				player_list[x] = True
				conn.send(pickle.dumps([1,players[x], x]))
				break
		if player_list[0] and player_list[1] and player_list[2] and player_list[3]:
			print("we are all in")
			all_players_in = True

def reciver():#kind of pathetic. but you got to do what you got to do
	global g_data
	l_data = conn.recv(1024)
	g_data = pickle.loads(l_data)

"""
global players, player_list, conn, addr, g_data
		current_player = 0
	x = threading.Thread(target=reciver, args=())
	x.start()
	did_player_answer = False
	while True:
		did_player_answer = False
		print("now asking player " + str(current_player))
		while not did_player_answer:
			conn.send(pickle.dumps([2,current_player])
					  if g_data:
						  if g_data[1] == current_player:
					players[x].remove(g_data[1])
					conn.send(pickle.dumps([22]))
					did_player_answer = True
					current_player += 1
					if current_player > 4:
						current_player = 0
"""
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
			conn.send(pickle.dumps([2,current_player]))
			if g_data:
				if g_data[1] == current_player:
					players[current_player].remove(g_data[0])
					conn.send(pickle.dumps([22]))
		current_player += 1
		if current_player > 4:
			current_player -= 4

def main():
	global players, player_list
	join_all_players()
	play()


main()