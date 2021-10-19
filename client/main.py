import numpy as np
import threading
import socket
import pygame
from pygame.locals import *

import sys

integer_map = np.ones((100, 100))
width, height = 640, 480
tile_columns, tile_rows = 16, 12
tile_size = int(width / tile_columns)
screen = pygame.display.set_mode((width, height))
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 15)

class Local_Player:
    def __init__(self, _name):
        self.pos = (50, 50)
        self.name = _name

        self.string_map = ""
        self.has_map = False
        self.integer_map = []

        self.other_players = []

    def draw(self, _screen):
        player_image = pygame.image.load("assets/player.png")
        player_sprite = pygame.transform.scale(player_image, (tile_size, tile_size))
        _screen.blit(player_sprite, ((tile_columns / 2) * tile_size, int((tile_rows / 2) * tile_size)))

    def map_received(self):
        self.has_map = True
        row_arr = self.string_map.split(":")
        for i in range(len(row_arr)):
            self.integer_map.append([int(cell) for cell in row_arr[i].split(".")])


class Player:
    def __init__(self, _id, _name, _position):
        self.id = _id
        self.name = _name
        self.pos = _position

    def draw(self, _screen, _local_player):
        # if _local_player.pos[0] - tile_columns < self.pos[0] < _local_player.pos[0] + tile_columns and _local_player.pos[1] - tile_rows < self.pos[1] < _local_player.pos[1] + tile_rows:
        x_diff = self.pos[0] - _local_player.pos[0]
        y_diff = self.pos[1] - _local_player.pos[1]
        player_image = pygame.image.load("assets/player.png")
        player_sprite = pygame.transform.scale(player_image, (tile_size, tile_size))
        _screen.blit(player_sprite, (int(tile_columns/2 + x_diff) * tile_size, int((tile_rows/2 + y_diff) * tile_size)))
        text_surface = font.render(self.name, False, (100, 255, 100))
        _screen.blit(text_surface, (int(tile_columns/2 + x_diff) * tile_size, int((tile_rows/2 + y_diff) * tile_size - (tile_size/2))))


name = input("Enter your name: ")

player = Local_Player(name)

class Client(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.connect((self.host, self.port))

    def run(self):
        while True:
            data = self.socket.recv(4096)
            if not data:
                self.disconnect()

            data = data.decode().split("|")
            if data[0] == "map_start" or player.receiving_map:
                player.receiving_map = True
                for section in data:
                    if section != "map_start" and section != "map_end":
                        player.string_map += section
                if data[len(data)-1] == "map_end":
                    player.receiving_map = False
                    player.map_received()

            if data[0] == "new_player":
                print("a new player joined lol")

                position = [int(i) for i in data[2].split(":")]
                op = Player(int(data[3]), data[1], (position[0], position[1]))
                player.other_players.append(op)

            if data[0] == "update_position":
                for p in player.other_players:
                    if p.id == int(data[1]):
                        position = [int(i) for i in data[2].split(":")]
                        p.pos = position

    def send(self, header, msg):
        packet = header + "|" + msg
        self.socket.send(bytes(header + "|" + msg, 'utf-8'))

    def disconnect(self):
        print("disconnected")
        self.socket.close()
        exit()


network = Client('127.0.0.1', 65432)
network.send("character_setup", str(name))
network.start()

pygame.init()

fps = 60
fpsClock = pygame.time.Clock()

while True:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            # network.disconnect()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                player.pos = (player.pos[0] + 1, player.pos[1])
                network.send("update_my_position", ":".join(str(s) for s in player.pos))
            if event.key == pygame.K_a:
                player.pos = (player.pos[0] - 1, player.pos[1])
                network.send("update_my_position", ":".join(str(s) for s in player.pos))
            if event.key == pygame.K_w:
                player.pos = (player.pos[0], player.pos[1] - 1)
                network.send("update_my_position", ":".join(str(s) for s in player.pos))
            if event.key == pygame.K_s:
                player.pos = (player.pos[0], player.pos[1] + 1)
                network.send("update_my_position", ":".join(str(s) for s in player.pos))

    if player.has_map:
        for y_rel in range(tile_rows):
            for x_rel in range(tile_columns):
                x = int((x_rel - tile_columns/2) + player.pos[0])
                y = int((y_rel - tile_rows / 2) + player.pos[1])
                sprite_num = player.integer_map[y][x]
                image = pygame.image.load("assets/tile" + str(sprite_num)[0] + ".png")
                sprite = pygame.transform.scale(image, (tile_size, tile_size))
                screen.blit(sprite, (int(x_rel * tile_size), int(y_rel * tile_size)))

    player.draw(screen)
    for pla in player.other_players:
        pla.draw(screen, player)

    pygame.display.flip()
    fpsClock.tick(fps)
