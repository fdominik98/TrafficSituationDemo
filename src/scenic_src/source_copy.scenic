
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

param map = localPath('Town06.xodr')
#param carla_map = 'Town06'
#model scenic.simulators.carla.model
model scenic.simulators.newtonian.driving_model
#weather = 'ClearSunset'
from follow_lane_edge import FollowLaneRightEdgeBehavior, FollowLaneLeftEdgeBehavior

FAST_SPEED = 10
SLOW_SPEED = 3
BRAKE_INTENSITY = 1.0


road = network.elements['road40']
lane1 = road.lanes[0]
lane2 = road.lanes[1]
lane3 = road.lanes[2]
lane4 = road.lanes[3]
lane5 = road.lanes[4]


# lane1.show(plt)
# plt.show()
# lane2.show(plt)
# plt.show()
# lane3.show(plt)
# plt.show()
# lane4.show(plt)
# plt.show()
# lane5.show(plt)
# plt.show()

spot1 = new OrientedPoint at 170 @ -251.5
spot2 = new OrientedPoint at 170 @ -248.5
spot3 = new OrientedPoint at 170 @ -244.5
spot4 = new OrientedPoint at 250 @ -241.5
spot5 = new OrientedPoint at 250 @ -237.5

behavior MyFollowLaneBehavior(targetSpeed=FAST_SPEED, laneToFollow=None, is_oppositeTraffic=False):
        take SetThrottleAction(1)
        do FollowLaneRightEdgeBehavior(target_speed=targetSpeed, laneToFollow=laneToFollow, is_oppositeTraffic=is_oppositeTraffic)


behavior ComplexBehavior(is_oppositeTraffic=False):
    do MyFollowLaneBehavior(laneToFollow=lane5) until (distance from self to 190 @ -251.5) < 5
    nextSection = lane2.sectionAt(210 @ -248.5)
    take SetBrakeAction(1.0)
    do LaneChangeBehavior(laneSectionToSwitch=nextSection, target_speed=SLOW_SPEED, is_oppositeTraffic=False)
    do MyFollowLaneBehavior() until (distance from self to 230 @ -248.5) < 5
    nextSection = lane1.sectionAt(260 @ -251.5)
    take SetBrakeAction(1.0)
    do LaneChangeBehavior(laneSectionToSwitch=nextSection, target_speed=SLOW_SPEED, is_oppositeTraffic=False)
    do MyFollowLaneBehavior()


# ego = new Car at spot1,
#         with behavior ComplexBehavior()

# car2 = new Car at spot3,
#         with behavior MyFollowLaneBehavior()

# car3 = new Car at spot4,
#         facing toward 220 @ -241.5,
#         with behavior MyFollowLaneBehavior(True)

# car4 = new Car at spot5,
#         facing toward 220 @ -237.5,
#         with behavior MyFollowLaneBehavior(True)

car0 = new Car at 348.5 @ -244.6375, facing toward 338.5 @ -244.6375, with behavior FollowLaneLeftEdgeBehavior(is_oppositeTraffic=True)
print(road.laneAt(348.5 @ -244.6375).id)
ego = new Car at 158.5 @ -241.14249999999998, with behavior ComplexBehavior()
print(road.laneAt(158.5 @ -241.14249999999998).id)
car2 = new Car at 178.5 @ -241.14249999999998, with behavior MyFollowLaneBehavior()
print(road.laneAt(178.5 @ -241.14249999999998).id)
car3 = new Car at 188.5 @ -248.15, with behavior MyFollowLaneBehavior()
print(road.laneAt(188.5 @ -248.15).id)

terminate when (distance from ego to spot1) > 200
