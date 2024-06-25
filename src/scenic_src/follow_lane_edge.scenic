import math
from scenic.domains.driving.actions import *
import scenic.domains.driving.model as _model
from scenic.domains.driving.roads import ManeuverType

def concatenateCenterlines(centerlines=[]):
    return PolylineRegion.unionAll(centerlines)

behavior PartialLaneChangeBehavior(target_point, is_oppositeTraffic=False, target_speed=10):
    current_lane = self.lane
    
    if not is_oppositeTraffic:
        if self.position[1] < target_point[1]:
            traj_centerline = [current_lane.leftEdge]
            traj_endpoint = current_lane.leftEdge[-1]
        else:
            traj_centerline = [current_lane.rightEdge]
            traj_endpoint = current_lane.rightEdge[-1]
    else:
        if self.position[1] < target_point[1]:
            traj_centerline = [current_lane.leftEdge]
            traj_endpoint = current_lane.leftEdge[0]
        else:
            traj_centerline = [current_lane.rightEdge]
            traj_endpoint = current_lane.rightEdge[0]


    brakeIntensity = 1.0
    distanceToEndpoint = 3 # meters

    trajectory_centerline = concatenateCenterlines(traj_centerline)

    if current_lane.maneuvers != ():
        nearby_intersection = current_lane.maneuvers[0].intersection
        if nearby_intersection == None:
            nearby_intersection = current_lane.centerline[-1]
    else:
        nearby_intersection = current_lane.centerline[-1]

    # instantiate longitudinal and lateral controllers
    _lon_controller, _lat_controller = simulation().getLaneChangingControllers(self)

    past_steer_angle = 0

    while True:
        if abs(trajectory_centerline.signedDistanceTo(self.position)) < 0.1:
            break        
        if (distance from self to nearby_intersection) < distanceToEndpoint:
            straight_manuevers = filter(lambda i: i.type == ManeuverType.STRAIGHT, current_lane.maneuvers)

            if len(straight_manuevers) > 0:
                select_maneuver = Uniform(*straight_manuevers)
            else:
                if len(current_lane.maneuvers) > 0:
                    select_maneuver = Uniform(*current_lane.maneuvers)
                else:
                    take SetBrakeAction(1.0)
                    break

            # assumption: there always will be a maneuver
            if select_maneuver.connectingLane != None:
                trajectory_centerline = concatenateCenterlines([trajectory_centerline, select_maneuver.connectingLane.centerline, \
                    select_maneuver.endLane.centerline])
            else:
                trajectory_centerline = concatenateCenterlines([trajectory_centerline, select_maneuver.endLane.centerline])

            current_lane = select_maneuver.endLane

        if self.speed is not None:
            current_speed = self.speed
        else:
            current_speed = 0

        cte = trajectory_centerline.signedDistanceTo(self.position)
        if is_oppositeTraffic: # [bypass] when crossing over the yellowline to opposite traffic lane 
            cte = -cte

        speed_error = target_speed - current_speed

        # compute throttle : Longitudinal Control
        throttle = _lon_controller.run_step(speed_error)

        # compute steering : Latitudinal Control
        current_steer_angle = _lat_controller.run_step(cte)

        take RegulatedControlAction(throttle, current_steer_angle, past_steer_angle)
        past_steer_angle = current_steer_angle

