from example import *


def init():
    enc = JsonEncoder()
    house = enc.load('test_house')
    print("free volume = ", house.count_free_vol())
    print("volume = ", house.count_volume())
    print("house is heated:", house.is_heated())
    print("heating cost = ", house.heating_cost())
    house.rooms[0].move(house.rooms[0].furnitures[0], 0, 10)
    house.rooms[0].add_tenants(1)
    print("people in living room: ", house.rooms[0].people_count)

if __name__ == "__main__":
    init()
