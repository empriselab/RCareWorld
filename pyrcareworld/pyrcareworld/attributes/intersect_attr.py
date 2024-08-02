import pyrcareworld.attributes as attr

class IntersectAttr(attr.BaseAttr):
    def create_game_objects(self, position_a, scale_a, position_b, scale_b):
        """
        Create two GameObjects in the Unity environment.

        :param position_a: Position of object A as a list [x, y, z].
        :param scale_a: Scale of object A as a list [x, y, z].
        :param position_b: Position of object B as a list [x, y, z].
        :param scale_b: Scale of object B as a list [x, y, z].
        """
        self._send_data("CreateGameObjects", position_a, scale_a, position_b, scale_b)

    def check_intersection(self):
        """
        Check if object A intersects with object B and get the volume ratio of intersection to object A.

        :return: A tuple (is_intersected, ratio).
        """
        self._send_data("CheckIntersection")
        self.env._step()
        data = self.data.get("CheckIntersection")
        if data:
            return data[0], data[1]
        else:
            return False, 0
