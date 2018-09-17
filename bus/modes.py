from constants import KEY
from dataset import SERVICE

class MODE(object):
    ONE         = 1
    TWO         = 2
    THREE       = 3
    FOUR        = 4
    FIVE        = 5
    SIX         = 6
    SEVEN       = 7
    EIGHT       = 8
    NINE        = 9
    TEN         = 10
    ELEVEN      = 11
    TWELVE      = 12


class BUFFER_METHOD(object):
    NONE         = "none"
    CIRCLE_400   = "circle_400"
    SQUARE_709   = "square_709"
    DIAMOND_500  = "diamond_500"

# List of supported buffer methods
BUFFER_LIST = [
    BUFFER_METHOD.NONE,
    BUFFER_METHOD.CIRCLE_400,
    BUFFER_METHOD.SQUARE_709,
    BUFFER_METHOD.DIAMOND_500
]

class DECAY_METHOD(object):
    NONE        = None
    CROW_250    = "crow_250"    # Euclidian distance, butterworth dpass = 250
    CROW_100    = "crow_100"    # Euclidian distance, butterworth dpass = 100
    GRID_250    = "grid_250"    #

# List of supported decay methods
# TODO is this really needed?
DECAY_LIST = [
    DECAY_METHOD.NONE,
    DECAY_METHOD.CROW_250,
    DECAY_METHOD.CROW_100,
    DECAY_METHOD.GRID_250,
]

class SCORE_METHOD(object):
    STOP_COUNT              = "simple_stop_count"
    DEPARTURES_PER_HOUR     = "departures_per_hour"
    DEPARTURES_PER_DAY      = "departures_per_day"
    DEPARTURES_PER_WEEK     = "departures_per_week"
    DIST_TO_CLOSEST_STOP    = "dist_to_closest_stop"
    DECAYED_WAIT            = "decayed_wait"

#-----------------------------------------------------------------------
MODE_DICT = {
    MODE.ONE : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
        KEY.STOP_DEMAND         : None
    },
    MODE.TWO : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.SQUARE_709,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
        KEY.STOP_DEMAND         : None
    },
    MODE.THREE : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_500,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
        KEY.STOP_DEMAND         : None
    },
    MODE.FOUR : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : False,
        KEY.STOP_DEMAND         : None
    },
    MODE.FIVE : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : False,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_250,
        KEY.STOP_DEMAND         : None
    },
    MODE.SIX : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : False,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_250,
        KEY.STOP_DEMAND         : None
    },
    MODE.SEVEN : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_250,
        KEY.STOP_DEMAND         : None
    },
    MODE.EIGHT : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_100,
        KEY.STOP_DEMAND         : None,
        KEY.SERVICE_TYPE        : SERVICE.MWF
    },
    MODE.NINE : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DECAY_METHOD        : DECAY_METHOD.GRID_250,
        KEY.STOP_DEMAND         : None,
        KEY.SERVICE_TYPE        : SERVICE.MWF
    },
    MODE.TEN : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NONE,
        KEY.SCORE_METHOD        : SCORE_METHOD.DIST_TO_CLOSEST_STOP,
        KEY.DISTANCE_METHOD     : 'grid',
    },
    MODE.ELEVEN : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NONE,
        KEY.SCORE_METHOD        : SCORE_METHOD.DIST_TO_CLOSEST_STOP,
        KEY.DISTANCE_METHOD     : 'crow',
    },
    MODE.TWELVE : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_250,
        KEY.STOP_DEMAND         : None,
    },
    13 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_250,
        KEY.STOP_DEMAND         : None,
        KEY.NORMALIZE_VALUE     : 6.0,
    },
    14: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_250,
        KEY.STOP_DEMAND         : None,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 10.0,
    },
    15: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_250,
        KEY.STOP_DEMAND         : None,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    }
}
