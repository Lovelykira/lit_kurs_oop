from math import sqrt
from json import JSONEncoder
import json


class Furniture:
    def __init__(self, x, y, width, length, height, density):
        self.x = x
        self.y = y
        self.width = width
        self.length = length
        self.height = height
        self.density = density

    def distance_to(self, furniture):
        return sqrt(((self.x - furniture.x)**2) + ((self.y - furniture.y)**2))

    def calc_weight(self):
        return self.calc_volume() * self.density

    def calc_volume(self):
        return self.width * self.height * self.length


class Table(Furniture):
    def __init__(self, x, y, width, length, height, density, tabletop_height, leg_width):
        super().__init__(x, y, width, length, height, density)
        self.tabletop_height = tabletop_height
        self.leg_width = leg_width

    def calc_volume(self):
        tabletop_vol = self.width * self.length * self.tabletop_height
        leg_vol = self.leg_width * self.leg_width * (self.height - self.tabletop_height)
        return tabletop_vol + 4*leg_vol


class Chair(Furniture):
    #let's assume that leg`s height equals half of chair` height
    def __init__(self, x, y, width, length, height, density, seat_height, leg_width ):
        super().__init__(x, y, width, length, height, density)
        self.seat_height = seat_height
        self.leg_width = leg_width

    def calc_volume(self):
        seat_vol = self.width * self.length * self.seat_height
        back_vol = self.width * self.leg_width * (self.height / 2)
        leg_vol = self.leg_width * self.leg_width * (self.height / 2)
        return seat_vol + back_vol + 4*leg_vol


class Bed(Furniture):
    def __init__(self, x, y, width, length, height, density, made = False):
        super().__init__(x, y, width, length, height, density)
        self.made = made

    def make(self):
        made = True

    def use(self):
        made = False


class Wardrobe(Furniture):
    def __init__(self, x, y, width, length, height, density, clothes_weight):
        super().__init__(x, y, width, length, height, density)
        self.clothes_weight = clothes_weight

    def calc_weight(self):
        return super().calc_weight() + self.clothes_weight


class Device(Furniture):
    def __init__(self, x, y, width, length, height, density, kw_per_hour):
        super().__init__(x, y, width, length, height, density)
        self.kw_per_hour = kw_per_hour
        self.turned_on = False

    def turn_on(self):
        self.turned_on = True

    def turn_off(self):
        self.turned_on = False


class WashingMachine(Device):
    clothes_weight = 0
    modes = ['wool', 'cotton', 'daily quick', 'synthetics']
    cur_mode = 'daily_quick'
    def load(self, clothes_weight):
        self.clothes_weight = clothes_weight

    def turn_on(self, mode):
        if mode in self.modes:
            cur_mode = mode
        else:
            print("EXTERMINATE")

    def calc_weight(self):
        return super().calc_weight() + self.clothes_weight


class Refrigerator(Device):
    def __init__(self, x, y, width, length, height, density, kw_per_hour, cur_temperature):
        super().__init__(x, y, width, length, height, density, kw_per_hour)
        self.cur_temperature = cur_temperature

    def set_temperature(self, temperature):
        self.cur_temperature = temperature


class Entrance:
    def __init__(self, x, y, width, height, is_window, is_open=False):
        self.x = x
        self.y = y
        self.is_window = is_window
        self.is_open = is_open

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False


class Room:
    def __init__(self, height, width, length, furnitures, entrances):
        self.height = height
        self.width = width
        self.length = length
        self.furnitures = furnitures
        self.entrances = entrances

    def is_crossing(self,furniture, new_x, new_y):
        crossing_x = False
        crossing_y = False
        for furn in self.furnitures:
            if (new_x >= furn.x and new_x <= furn.x + furn.length) or \
                    (new_x + furniture.lenght >= furn.x and new_x + furniture.lenght <= furn.x+furn.length):
                crossing_x = True
            if (new_y >= furn.y and new_y <= furn.y + furn.width) or \
                    (new_y + furniture.width >= furn.y and new_y + furniture.width <= furn.y + furn.width):
                crossing_y = True
            if crossing_x and crossing_y and (furn.x != furniture.x and furn.y != furniture.y):
                print("it's crossing")
                return True
        else:
            return False

    def move(self, furniture, new_x, new_y):
        if not self.is_crossing(furniture, new_x, new_y):
            furniture.x = new_x
            furniture.y = new_y

    def add_furn(self, furn):
        if not self.is_crossing(furn, furn.x, furn.y):
            self.furnitures.append(furn)

    def count_volume(self):
        return self.height * self.width * self.length

    def count_free_volume(self):
        furn_vol = 0
        for furn in self.furnitures:
            furn_vol += furn.calc_volume()
        return self.count_volume() - furn_vol


class LivingRoom(Room):
    def __init__(self, width, length,height, furnitures, entrances, people_count):
        super().__init__(height, width, length, furnitures, entrances)
        self.people_count = people_count

    def add_tenants(self, num):
        self.people_count += num

    def remove_tenants(self, num):
        if num <= self.people_count:
            self.people_count -= num
        else:
            print("Sorry, there are only %s people." % self.people_count)


class House:
    def __init__(self, rooms):
        self.rooms = rooms

    def count_volume(self):
        vol = 0
        for room in self.rooms:
            vol += room.count_volume()
        return vol

    def count_free_vol(self):
        free_vol = 0
        for room in self.rooms:
            free_vol += room.count_free_volume()
        return free_vol


house = House([
    LivingRoom(100, 50, 50,
               [Table(0, 0, 20, 10, 10, 0.5, 3, 3),
                Chair(10, 15, 5, 5, 7, 0.5, 1, 1),
                Bed(65, 0, 45, 20, 15, 0.5),
                Wardrobe(75, 35, 25, 15, 35, 0.5, 50)],
               [Entrance(10, 50, 20, 3, 40, True),
                Entrance(70, 50, 20, 3, 40, True),
                Entrance(100, 23, 3, 6, 40, False)],
               1),
    Room(30, 50, 50,
         [WashingMachine(10, 0, 20, 20, 20, 0.5, 100)],
         [Entrance(0, 13, 3, 6, 40, False),
          Entrance(50, 13, 3, 6, 40, False)]),
    Room(50, 50, 50,
         [Refrigerator(30, 0, 20, 20, 35, 0.5, 100, -30),
          Table(0, 0, 20, 10, 10, 0.5, 3, 3),
          Chair(10, 15, 5, 5, 7, 0.5, 1, 1)],
         [Entrance(0, 23, 3, 6, 40, False),
          Entrance(10, 50, 30, 3, 40, True)])
])


def SaveToJson(data, file_path):
    file = open(file_path, 'w')
    file.write(json.dumps(data))
    file.close()


def LoadFrom(file_path):
    file = open(file_path, 'r')
    text = file.read()
    file.close()
    jsn = json.loads(text)
    print(jsn)

#print(house.count_free_vol())
#class MyEncoder(JSONEncoder):
#    def default(self, o):
#        return o.__dict__

#SaveToJson(house, 'a')
#LoadFrom('a')



