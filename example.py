from math import sqrt
import json
from abc import *


class DictSerializable:
    def to_dict(self):
        result = self.__dict__
        result['cls'] = self.__class__.__name__
        return result

    @classmethod
    def from_dict(cls, dict_object):
        return cls(**dict_object)


class Resource(DictSerializable):
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.cost = kwargs['cost']


class Heating(DictSerializable):
    def __init__(self, **kwargs):
        self.resource = kwargs['resource']
        self.heating_space = kwargs['heating_space']
        self.consumption = kwargs['consumption']


class Fireplace(Heating):
    def __init__(self, time, **kwargs):
        self.time = time
        super().__init__(**kwargs)

    @classmethod
    def from_dict(cls, dict_object):
        return cls(dict_object.pop('time'), **dict_object)


class ElectricHeater(Heating):
    def __init__(self, turned_on=False, **kwargs):
        self.turned_on = turned_on
        super().__init__(**kwargs)

    def turn_on(self):
        self.turned_on = True

    def turn_off(self):
        self.turned_on = False

    @classmethod
    def from_dict(cls, dict_object):
        return cls(dict_object.pop('turned_on', False), **dict_object)


class Furniture(DictSerializable):
    def __init__(self, **kwargs):
        self.x = kwargs['x']
        self.y = kwargs['y']
        self.width = kwargs['width']
        self.length = kwargs['length']
        self.height = kwargs['height']
        self.density = kwargs['density']

    def distance_to(self, furniture):
        return sqrt(((self.x - furniture.x)**2) + ((self.y - furniture.y)**2))

    def calc_weight(self):
        return self.calc_volume() * self.density

    def calc_volume(self):
        return self.width * self.height * self.length


class Table(Furniture):
    def __init__(self, tabletop_height, leg_width, **kwargs):
        super().__init__(**kwargs)
        self.tabletop_height = tabletop_height
        self.leg_width = leg_width

    def calc_volume(self):
        tabletop_vol = self.width * self.length * self.tabletop_height
        leg_vol = self.leg_width * self.leg_width * (self.height - self.tabletop_height)
        return tabletop_vol + 4*leg_vol

    @classmethod
    def from_dict(cls, dict_object):
        return cls(dict_object.pop('tabletop_height'), dict_object.pop('leg_width'), **dict_object)


class Chair(Furniture):
    # let's assume that leg`s height equals half of chair` height
    def __init__(self, seat_height, leg_width, **kwargs):
        super().__init__(**kwargs)
        self.seat_height = seat_height
        self.leg_width = leg_width

    def calc_volume(self):
        seat_vol = self.width * self.length * self.seat_height
        back_vol = self.width * self.leg_width * (self.height / 2)
        leg_vol = self.leg_width * self.leg_width * (self.height / 2)
        return seat_vol + back_vol + 4*leg_vol

    @classmethod
    def from_dict(cls, dict_object):
        return cls(dict_object.pop('seat_height'), dict_object.pop('leg_width'), **dict_object)


class Bed(Furniture):
    def __init__(self, made=False, **kwargs):
        super().__init__(**kwargs)
        self.made = made

    def make(self):
        self.made = True

    def use(self):
        self.made = False

    @classmethod
    def from_dict(cls, dict_object):
        return cls(dict_object.pop('made', False), **dict_object)


class Wardrobe(Furniture):
    def __init__(self, clothes_weight, **kwargs):
        super().__init__(**kwargs)
        self.clothes_weight = clothes_weight

    def calc_weight(self):
        return super().calc_weight() + self.clothes_weight

    @classmethod
    def from_dict(cls, dict_object):
        return cls(dict_object.pop('clothes_weight'), **dict_object)


class Device(Furniture):
    def __init__(self, kw_per_hour, **kwargs):
        super().__init__(**kwargs)
        self.kw_per_hour = kw_per_hour
        self.turned_on = False

    def turn_on(self):
        self.turned_on = True

    def turn_off(self):
        self.turned_on = False

    @classmethod
    def from_dict(cls, dict_object):
        return cls(dict_object.pop('kw_per_hour'), **dict_object)


class WashingMachine(Device):
    clothes_weight = 0
    modes = ['wool', 'cotton', 'daily quick', 'synthetics']
    cur_mode = 'daily_quick'

    def load(self, clothes_weight):
        self.clothes_weight = clothes_weight

    def turn_on(self, mode):
        if mode in self.modes:
            self.cur_mode = mode
        else:
            print("EXTERMINATE")

    def calc_weight(self):
        return super().calc_weight() + self.clothes_weight


class Refrigerator(Device):
    def __init__(self, cur_temperature, **kwargs):
        super().__init__(**kwargs)
        self.cur_temperature = cur_temperature

    def set_temperature(self, temperature):
        self.cur_temperature = temperature

    @classmethod
    def from_dict(cls, dict_object):
        return cls(dict_object.pop('cur_temperature'), **dict_object)


class Entrance(DictSerializable):
    def __init__(self, is_open=False, **kwargs):
        self.x = kwargs['x']
        self.y = kwargs['y']
        self.is_window = kwargs['is_window']
        self.is_open = is_open
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.length = kwargs['length']

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    @classmethod
    def from_dict(cls, dict_object):
        #return cls(dict_object['x'], dict_object['y'], dict_object['width'], dict_object['height'],
         #          dict_object['is_window'], dict_object.get('is_open', False))
        return cls(**dict_object)


class Room(DictSerializable):
    #def __init__(self, height, width, length, furnitures, entrances):
    def __init__(self, **kwargs):
        self.height = kwargs['height']
        self.width = kwargs['width']
        self.length = kwargs['length']
        self.furnitures = kwargs['furnitures']
        self.entrances = kwargs['entrances']
        self.heating = kwargs['heating']

    def is_crossing(self, furniture, new_x, new_y):
        crossing_x = False
        crossing_y = False
        for furn in self.furnitures:
            if (new_x > furn.x and new_x < furn.x + furn.length) or \
                    (new_x + furniture.length > furn.x and new_x + furniture.length < furn.x+furn.length):
                crossing_x = True
            if (new_y > furn.y and new_y < furn.y + furn.width) or \
                    (new_y + furniture.width > furn.y and new_y + furniture.width < furn.y + furn.width):
                crossing_y = True
            if crossing_x and crossing_y and (furn.x != furniture.x and furn.y != furniture.y):
                print("it's crossing", furn.__class__.__name__)
                return True
        else:
            return False

    def move(self, furniture, new_x, new_y):
        if not self.is_crossing(furniture, new_x, new_y):
            furniture.x = new_x
            furniture.y = new_y
            print("%s moved" % furniture.__class__.__name__)

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

    def is_heated(self):
        total_space = 0
        for heater in self.heating:
            total_space += heater.heating_space
        if self.height * self.width * self.length <= total_space:
            return True
        else:
            return False

    def heating_cost(self):
        sum = 0
        for heater in self.heating:
            sum += heater.resource.cost * heater.consumption
        return sum


class LivingRoom(Room):
    def __init__(self, people_count, **kwargs):
        super().__init__(**kwargs)
        self.people_count = people_count

    def add_tenants(self, num):
        self.people_count += num

    def remove_tenants(self, num):
        try:
            if num <= self.people_count:
                self.people_count -= num
        except Exception:
            print("Sorry, there are only %s people." % self.people_count)

    @classmethod
    def from_dict(cls, dict_object):
        return cls(dict_object.pop('people_count'), **dict_object)


class House(DictSerializable):
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

    def is_heated(self):
        for room in self.rooms:
            if not room.is_heated():
                return False
        return True

    def heating_cost(self):
        sum = 0
        for room in self.rooms:
            sum += room.heating_cost()
        return sum

    @classmethod
    def from_dict(cls, dict_object):
        return cls(dict_object['rooms'])


class Encoder(metaclass=ABCMeta):
    @abstractmethod
    def save(self,file_path, obj):
        file = open(file_path, 'w')
        file.write(obj)
        file.close()

    @abstractmethod
    def load(self, file_path):
        file = open(file_path, 'r')
        text = file.read()
        file.close()
        return text


class JsonEncoder(Encoder):
    def save(self, file_path, obj):
        file = open(file_path, 'w')
        file.write(json.dumps(obj.to_dict(), default=lambda x: x.to_dict(), sort_keys=True, indent=4))
        file.close()

    def load(self, file_path):
        file = open(file_path, 'r')
        text = file.read()
        file.close()
        obj = self.load_object_from_dict(json.loads(text))
        return obj

    def load_object_from_dict(self, dict_object):
        classes = globals()
        cls = classes[dict_object['cls']]
        del dict_object['cls']
        properties = dict()
        for key, value in dict_object.items():
            if isinstance(value, list):
                dict_object[key] = [self.load_object_from_dict(i) for i in value]
            elif isinstance(value, dict):
                dict_object[key] = self.load_object_from_dict(value)
            properties[key] = dict_object[key]
        return cls.from_dict(properties)


def create_house():
    house = House([
        LivingRoom(width=100, height=50, length=50,
                   furnitures=[Table(x=0, y=0, width=20, length=10, height=10, density=0.5, tabletop_height=3, leg_width=3),
                               Chair(x=10, y=15, width=5, length=5, height=7, density=0.5, seat_height=1, leg_width=1),
                               Bed(x=65, y=0, width=45, length=20, height=15, density=0.5),
                               Wardrobe(x=75, y=35, width=25, length=15, height=35, density=0.5, clothes_weight=50)],
                   entrances=[Entrance(x=10, y=50, length=20, width=3, height=40, is_window=True),
                              Entrance(x=70, y=50, length=20, width=3, height=40, is_window=True),
                              Entrance(x=100, y=23, length=3, width=6, height=40, is_window=False)],
                   heating=[Fireplace(resource=Resource(name="wood", cost=100), heating_space=250000, consumption=10, time=5),
                            ElectricHeater(resource=Resource(name="electricity", cost=100), heating_space=250000, consumption=220, turned_on=True)],
                   people_count=1),
        Room(width=30, height=50, length=50,
             furnitures=[WashingMachine(x=10, y=0, width=20, length=20, height=20, density=0.5, kw_per_hour=100)],
             entrances=[Entrance(x=0, y=13, length=3, width=6, height=40, is_window=False),
                        Entrance(x=50, y=13, length=3, width=6, height=40, is_window=False)],
             heating=[ElectricHeater(resource=Resource(name="electricity", cost=100), heating_space=250000, consumption=220, turned_on=True)]),
        Room(height=50, width=50, length=50,
             furnitures=[Refrigerator(x=30, y=0, width=20, length=20, height=35, density=0.5, kw_per_hour=100, cur_temperature=-30),
                         Table(x=0, y=0, width=20, length=10, height=10, density=0.5, tabletop_height=3, leg_width=3),
                         Chair(x=10, y=15,  width=5, length=5, height=7, density=0.5, seat_height=1, leg_width=1)],
             entrances=[Entrance(x=0, y=23, length=3, width=6, height=40, is_window=False),
                        Entrance(x=10, y=50, length=30, width=3, height=40, is_window=True)],
             heating=[ElectricHeater(resource=Resource(name="electricity", cost=100), heating_space=250000, consumption=220, turned_on=True)])
    ])
    return house


if __name__ == "__main__":
    my_house = create_house()
    enc = JsonEncoder()
    enc.save('test_house', my_house)