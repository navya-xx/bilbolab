import dataclasses

from core.utils.logging_utils import Logger


@dataclasses.dataclass
class Waypoint:
    x: float = 0.0
    y: float = 0.0


class BILBO_PositionControl:
    waypoints: list[Waypoint]
    current_waypoint: Waypoint

    def __init__(self):
        self.waypoints = []
        self.current_waypoint = None  # type: ignore

        self.logger = Logger('PositionControl')
        self.logger.setLevel('DEBUG')

        pass

    def update(self):
        ...



    def setWaypoints(self, waypoints):
        if not isinstance(waypoints, list):
            raise ValueError('waypoints must be a list')

        for entry in waypoints:
            new_waypoint = Waypoint(entry['x'], entry['y'])
            self.waypoints.append(new_waypoint)

        self.logger.info(f"Received {len(self.waypoints)} waypoints")
        self.current_waypoint = self.waypoints[0]


