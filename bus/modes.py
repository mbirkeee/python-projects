import pprint
import copy
import random

from constants import KEY
from dataset import SERVICE

class BUFFER_METHOD(object):
    NONE            = "none"
    CIRCLE_400      = "circle_400"
    CIRCLE_500      = 'circle_500'
    CIRCLE_800      = "circle_800"
    SQUARE_709      = "square_709"
    DIAMOND_500     = "diamond_500"
    DIAMOND_400     = "diamond_400"
    DIAMOND_1500    = "diamond_1500"
    NETWORK_400     = "network_400"
    NETWORK_532     = "network_532"
    NETWORK_2000    = "network_2000"

BUFFER_LIST = [
    BUFFER_METHOD.CIRCLE_400,
    BUFFER_METHOD.CIRCLE_500,
    BUFFER_METHOD.CIRCLE_800,
    BUFFER_METHOD.SQUARE_709,
    BUFFER_METHOD.DIAMOND_400,
    BUFFER_METHOD.DIAMOND_500,
    BUFFER_METHOD.DIAMOND_1500,
    BUFFER_METHOD.NETWORK_400,
    BUFFER_METHOD.NETWORK_2000,
]

class DECAY_METHOD(object):
    NONE        = None

    CROW_50         = "crow_50"
    CROW_100        = "crow_100"
    CROW_150        = "crow_150"
    CROW_200        = "crow_200"
    CROW_250        = "crow_250"
    CROW_400        = "crow_400"
    GRID_50         = "grid_50"
    GRID_100        = "grid_100"
    GRID_150        = "grid_150"
    GRID_200        = "grid_200"
    GRID_250        = "grid_250"
    GRID_400        = "grid_400"
    GRID_1000       = "grid_1000"
    GRID_WALKSCORE  = "grid_99999"
    EXPONENTIAL_1   = "exp_1"
    EXPONENTIAL_2   = "exp_2"
    EXPONENTIAL_3   = "exp_3"
    EXPONENTIAL_4   = "exp_4"
    POLY_1          = "poly_1"


class SCORE_METHOD(object):
    STOP_COUNT              = "simple_stop_count"
    DEPARTURES_PER_HOUR     = "departures_per_hour"
    DEPARTURES_PER_DAY      = "departures_per_day"
    DEPARTURES_PER_WEEK     = "departures_per_week"
    DIST_TO_CLOSEST_STOP    = "dist_to_closest_stop"
    DECAYED_WAIT            = "decayed_wait"
    COVERAGE                = "coverage"
    TRANSIT_SCORE           = "transit_score"

class DEMAND_METHOD(object):

    DIVIDE                  = "divide"

class SPECIAL_MODE(object):
    """
    Special modes
    """
    TRANSIT_SCORE = 10000
#-----------------------------------------------------------------------
MODE_DICT = {
    1 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
    },
    2 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.SQUARE_709,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
    },
    3 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_500,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
    },
    4 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : False,
        KEY.DISTANCE_DECAY      : None
    },
    5 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : False,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_250,
    },
    6 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : False,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_250,
    },
    7 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_250,
    },
    8 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_100,
        KEY.SERVICE_TYPE        : SERVICE.MWF
    },
    9 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.SERVICE_TYPE        : SERVICE.MWF
    },
    10 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NONE,
        KEY.SCORE_METHOD        : SCORE_METHOD.DIST_TO_CLOSEST_STOP,
        KEY.DISTANCE_METHOD     : 'grid',
    },
    11 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NONE,
        KEY.SCORE_METHOD        : SCORE_METHOD.DIST_TO_CLOSEST_STOP,
        KEY.DISTANCE_METHOD     : 'crow',
    },
    12 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_250,
    },
    13 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_250,
        KEY.NORMALIZE_VALUE     : 6.0,
    },
    14: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_250,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 10.0,
    },
    15: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_250,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    },
    16: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_200,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    },
    17: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_100,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    },
    18: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_400,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    },
    19: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    },
    20: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    },
    21: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    },
    22: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_250,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    },
    23: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_250,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    },
    24: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 1.0,
    },
    25: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 5.0,
    },
    26: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 10.0,
    },
    27: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
    },
    28: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.SCORE_NEAREST_ONLY  : False
    },
    29: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_WEEK,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.SCORE_NEAREST_ONLY  : False
    },
    30: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 5.0,
    },
    31: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_100,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 5.0,
    },
    32: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 10.0,
    },
    33: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.STOP_DEMAND         : DECAY_METHOD.GRID_250,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 10.0,
    },
    34: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
    },
    35: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
    },

    # COVERAGE MODEL
    36: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.COVERAGE,
        KEY.SCORE_NEAREST_ONLY  : False

    },

    # COVERAGE WITH DECAY
    37: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.COVERAGE,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.SCORE_NEAREST_ONLY  : False
    },

    # This is the "FREQUENCY" model
    38 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : False,
    },

    # This is the "FREQUENCY" model with distance decay
    39 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : False,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250
    },

    # This is the "FREQUENCY" model with distance decay & filtering
    40 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250
    },
    # This is the "FREQUENCY" model & filtering
    41 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
    },

    # FILTERED COVERAGE
    42: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.COVERAGE,
        KEY.SCORE_NEAREST_ONLY  : True
    },

     # FILTERED COVERAGE
    43: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.COVERAGE,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250
    },

    # This is the "FREQUENCY" model with distance decay & filtering
    44 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_800,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_250,
    },
    45 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_800,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_100,
    },
    46 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_800,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_50,
    },
    47 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_800,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_150,
    },
    48 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_800,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_200,
    },
    # This is the "FREQUENCY" model with distance decay & filtering
    49 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.CROW_150
    },
    # Langfords E2SFCA
    50 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.STOP_DEMAND         : DECAY_METHOD.GRID_250,
        KEY.DEMAND_METHOD       : DEMAND_METHOD.DIVIDE
    },
    # Modified E2SFCA
    51 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.STOP_DEMAND         : DECAY_METHOD.GRID_250,
        KEY.DEMAND_METHOD       : "pow_0.5"
    },
    # Modified E2SFCA
    52 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.STOP_DEMAND         : DECAY_METHOD.GRID_250,
        KEY.DEMAND_METHOD       : "pow_0.5",
        KEY.RASTER_CLIP         : 0.1
    },
    # Modified E2SFCA
    53 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.STOP_DEMAND         : DECAY_METHOD.GRID_250,
        KEY.DEMAND_METHOD       : "pow_0.5",
        KEY.RASTER_CLIP         : "log"
    },
    # Walkscore - 400 - self computed
    54 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_WEEK,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_WALKSCORE,
        KEY.STOP_DEMAND         : DECAY_METHOD.GRID_250,
        KEY.DEMAND_METHOD       : "pow_0.5",
        KEY.RASTER_CLIP         : "log"
    },
    # Transit Score - self computed
    55 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_2000,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_WEEK,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_WALKSCORE,
        KEY.STOP_DEMAND         : None,
        KEY.DEMAND_METHOD       : None,
        KEY.RASTER_CLIP         : "log"
    },
    #
    56 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_WEEK,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_150,
        KEY.STOP_DEMAND         : DECAY_METHOD.GRID_400,
        KEY.DEMAND_METHOD       : "pow_0.8",
        KEY.RASTER_CLIP         : "fraction_0.1",
    },
    57 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : "grid_131",
        KEY.STOP_DEMAND         : "grid_370",
        KEY.DEMAND_METHOD       : "pow_0.96",
        KEY.RASTER_CLIP         : "percent_6.5",
    },
    58 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : "grid_150",
        KEY.STOP_DEMAND         : "grid_500",
        KEY.DEMAND_METHOD       : "pow_0.85",
        KEY.RASTER_CLIP         : "percent_5",
    },
    59 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_WEEK,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : "grid_150",
        KEY.STOP_DEMAND         : "grid_500",
        KEY.DEMAND_METHOD       : "pow_0.85",
        KEY.RASTER_CLIP         : "percent_5",
    },
    # This is the "FREQUENCY" model like 40 but with shorter dist decay
    60 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : 'grid_150'
    },
    # This is the "FREQUENCY" model like 40 but with shorter dist decay
    61 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : 'grid_150'
    },

    # Like 51 but with GRID buffers and departs per hour
    62 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_500,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250,
        KEY.STOP_DEMAND         : DECAY_METHOD.GRID_250,
        KEY.DEMAND_METHOD       : "pow_0.5"
    },

    # Like 51 but with GRID buffers and departs per hour
    63 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_150,
        KEY.STOP_DEMAND         : DECAY_METHOD.GRID_250,
        KEY.DEMAND_METHOD       : "pow_0.85",
        KEY.RASTER_CLIP         : "percent_5",
    },

    # This is the "FREQUENCY" model with distance decay & filtering
    64 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_150
    },
    # This is the "FREQUENCY" model with distance decay & filtering
    65 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_500,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_150
    },

    # This is the "FREQUENCY" model with distance decay & filtering
    66 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_100
    },

    # This is the "FREQUENCY" model with distance decay & filtering
    67 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_100
    },

    # This is the "FREQUENCY" model with distance decay & filtering
    68 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.EXPONENTIAL_1
    },

    # This is the "FREQUENCY" model with distance decay & filtering
    69 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_1500,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.EXPONENTIAL_1
    },
    # This is the "FREQUENCY" model with distance decay & filtering
    70 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250
    },

    # This is the "FREQUENCY" model with distance decay & filtering
    71 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250
    },

    72 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_WEEK,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250
    },
    73 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_500,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_200
    },

    74 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_150
    },

    75 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : "grid_300"
    },

    76 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.EXPONENTIAL_3
    },

    77: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_532,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.POLY_1
    },

    78: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.POLY_1
    },
    79: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_532,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250
    },

    80: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_532,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_150
    },

    81: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_150
    },

    82 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.POLY_1
    },

    83 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_532,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250
    },

    84 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_532,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.POLY_1
    },

    85 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_532,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_150
    },

    86 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.EXPONENTIAL_4
    },

    87 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
        # KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.EXPONENTIAL_4
    },

    # This is the "FREQUENCY" model with distance decay
    88 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : False,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_150
    },

    89 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : False,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.EXPONENTIAL_4
    },

    90 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_532,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : False,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.GRID_250
    },

    91 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_532,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.EXPONENTIAL_4
    },

    92: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.COVERAGE,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.EXPONENTIAL_4
    },

    93: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.COVERAGE,
        KEY.SCORE_NEAREST_ONLY  : False,
        KEY.DISTANCE_DECAY      : DECAY_METHOD.EXPONENTIAL_4
    },

    SPECIAL_MODE.TRANSIT_SCORE : {
        KEY.SCORE_METHOD        : SCORE_METHOD.TRANSIT_SCORE
    },


}

class ModeMan(object):

    def __init__(self, mode=None):

        self._mode_dict = copy.copy(MODE_DICT)

        self._random_model_service_day = None
        self._random_model_service_time = None

        self.validate()
        self._mode = mode
        if mode is not None:
            self.set_mode(mode)

    def mode_list_summary(self, mode_list):

        mode_list = sorted(mode_list)

        getters = [
            ("BUFFER",          self.get_buffer_method),
            ("SCORE",           self.get_score_method),
            ("DISTANCE",        self.get_distance_method),
            ("DECAY",           self.get_distance_decay),
            ("NEAREST",         self.get_nearest_only),
            ("DAY",             self.get_service_type),
            ("TIME",            self.get_service_time),
            ("WAIT_BPASS",      self.get_wait_bandpass),
            ("WAIT_NORM",       self.get_normalize_value),
            ("STOP DEMAND",     self.get_stop_demand),
            ("DEMAND METHOD",   self.get_demand_method),
            ("RASTER CLIP",     self.get_raster_clip)

        ]

        for item in getters:
            desc = item[0]
            getter = item[1]

            method_dict = {}

            for mode in mode_list:
                try:
                    method = getter(mode=mode)
                except:
                    method = "None"

                modes = method_dict.get(method, [])
                modes.append(mode)
                method_dict[method] = modes

            for k, v in method_dict.iteritems():
                modes = "%s" % repr(v)
                param = "%-15s %-20s %s" % (desc, k, modes)
                print param

    def get_model(self):
        model_data = self._mode_dict.get(self._mode)
        return model_data

    def print_model(self):
        model_data = self._mode_dict.get(self._mode)
        for k, v in model_data.iteritems():
            print "KEY: %s: VALUE: %s" % (repr(k), repr(v))

    def make_random_model(self):
        self._mode = "random"
        mode_data = {}

        if self._random_model_service_time is None:
            raise ValueError("Service time not set for random model")

        if self._random_model_service_day is None:
            raise ValueError("Service day not set for random model")

        dpass = random.randint(50, 400)
        distance_decay = "grid_%d" % dpass

        spass = random.randint(50, 400)
        stop_decay = "grid_%d" % spass

        demand_pow = float(random.randint(0, 1000)) / 1000.0
        demand_method = "pow_%f" % demand_pow

        # 0 to 10 mins
        wpass = float(random.randint(0, 1000)) / 100.0

        # 1% to 15%
        raster_clip = float(random.randint(100, 1500)) / 10000.0
        raster_clip = "percent_%f" % (raster_clip * 100.0)

        mode_data = {
            KEY.SERVICE_TIME        : self._random_model_service_time,
            KEY.SERVICE_TYPE        : self._random_model_service_day,
            KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
            KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
            KEY.SCORE_NEAREST_ONLY  : True,
            KEY.STOP_DEMAND         : stop_decay,
            KEY.DISTANCE_DECAY      : distance_decay,
            KEY.DEMAND_METHOD       : demand_method,
            KEY.WAIT_BANDPASS       : wpass,
            KEY.RASTER_CLIP         : raster_clip
        }

        self._mode_dict[self._mode] = mode_data

    def set_mode(self, mode):
        mode = int(mode)
        if not self.valid(mode):
            print "Invalid mode. Supported modes are:"
            self.print_modes()
            raise ValueError("Invalid mode")
        self._mode = mode

    def get_mode(self):
        return self._mode

    def set_service_time(self, service_time):
        mode_data = self._mode_dict.get(self._mode)
        if mode_data is not None:
            mode_data[KEY.SERVICE_TIME] = service_time
            self._mode_dict[self._mode] = mode_data

        self._random_model_service_time = service_time

    def set_service_day(self, service_day):
        mode_data = self._mode_dict.get(self._mode)
        if mode_data is not None:
            mode_data[KEY.SERVICE_TYPE] = service_day
            self._mode_dict[self._mode] = mode_data
        self._random_model_service_day = service_day

    def get_service_day_str(self):
        day = self.get_service_type()

        if day == SERVICE.MWF:
            return "mwf"
        elif day == SERVICE.SAT:
            return "sat"
        elif day == SERVICE.SUN:
            return "sun"
        return "unknown_day"

    def get_service_time_str(self):
        t = self.get_service_time()
        #return t
        return t.replace(":", "_")

    def compare_modes(self, mode1, mode2, key1, key2):

        if mode1.get(KEY.BUFFER_METHOD, BUFFER_METHOD.NONE) != mode2.get(KEY.BUFFER_METHOD, BUFFER_METHOD.NONE):
            return False

        if mode1.get(KEY.SCORE_METHOD) != mode2.get(KEY.SCORE_METHOD):
            return False

        if mode1.get(KEY.DISTANCE_METHOD) != mode2.get(KEY.DISTANCE_METHOD):
            return False

        if mode1.get(KEY.SCORE_NEAREST_ONLY, True) != mode2.get(KEY.SCORE_NEAREST_ONLY, True):
            return False

        if mode1.get(KEY.DISTANCE_DECAY, None) != mode2.get(KEY.DISTANCE_DECAY, None):
            return False

        if mode1.get(KEY.STOP_DEMAND, None) != mode2.get(KEY.STOP_DEMAND, None):
            return False

        if mode1.get(KEY.NORMALIZE_VALUE, None) != mode2.get(KEY.NORMALIZE_VALUE, None):
            return False

        if mode1.get(KEY.WAIT_BANDPASS, None) != mode2.get(KEY.WAIT_BANDPASS, None):
            return False

        if mode1.get(KEY.SERVICE_TYPE, SERVICE.MWF) != mode2.get(KEY.SERVICE_TYPE, SERVICE.MWF):
            return False

        if mode1.get(KEY.SERVICE_TIME, "8:00") != mode2.get(KEY.SERVICE_TIME, "8:00"):
            return False

        if mode1.get(KEY.DEMAND_METHOD) != mode2.get(KEY.DEMAND_METHOD):
            return False

        if mode1.get(KEY.RASTER_CLIP) != mode2.get(KEY.RASTER_CLIP):
            return False

        # If we made it to here a duplicate mode was detected
        pp = pprint.PrettyPrinter(indent=4)
        print "*"*80
        print "DUPLICATE MODE KEY", key1
        pp.pprint(mode1)
        print "*"*80
        print "DUPLICATE MODE KEY", key2
        pp.pprint(mode2)
        print "*"*80
        raise ValueError("Duplicate modes")

    def validate(self):

        for key1, mode1 in self._mode_dict.iteritems():
            for key2, mode2 in self._mode_dict.iteritems():
                if key1 == key2: continue
                self.compare_modes(mode1, mode2, key1, key2)

    def valid(self, mode):
        if self._mode_dict.has_key(mode):
            return True
        return False

    def print_modes(self):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self._mode_dict)

    def get_buffer_method(self, mode=None):
        if not mode: mode = self._mode
        # Buffer method defaults to BUFFER_METHOD.NONE
        mode_data = self._mode_dict.get(mode)
        return mode_data.get(KEY.BUFFER_METHOD, BUFFER_METHOD.NONE)

    def get_score_method(self, mode=None):
        # Score method must be defined (if requested)
        if not mode: mode = self._mode
        mode_data = self._mode_dict.get(mode)
        method = mode_data.get(KEY.SCORE_METHOD)
        if method is None:
            raise ValueError("Score method not defined for mode: %s" % repr(mode))
        return method

    def get_distance_method(self, mode=None):
        # Distance method must be defined (if requested)
        if not mode: mode = self._mode
        mode_data = self._mode_dict.get(mode)
        method = mode_data.get(KEY.DISTANCE_METHOD)
        if method is None:
            raise ValueError("Score method not defined for mode: %s" % repr(mode))
        return method

    def get_distance_decay(self, mode=None):
        # Distance method must be defined (if requested)
        if not mode: mode = self._mode
        mode_data = self._mode_dict.get(mode)
        method = mode_data.get(KEY.DISTANCE_DECAY)
        # if method is None:
        #     raise ValueError("Decay method not defined for mode: %s" % repr(mode))
        return method

    def get_service_type(self, mode=None):
        # Service defaults to MWF
        if not mode: mode = self._mode
        mode_data = self._mode_dict.get(mode)
        method = mode_data.get(KEY.SERVICE_TYPE, SERVICE.MWF)
        return method

    def get_normalize_value(self, mode=None):
        # Normalize value can be None
        if not mode: mode = self._mode
        mode_data = self._mode_dict.get(mode)
        method = mode_data.get(KEY.NORMALIZE_VALUE)
        return method

    def get_wait_bandpass(self, mode=None):
        # Wait bandpass must be defined (if requested)
        if not mode: mode = self._mode
        mode_data = self._mode_dict.get(mode)
        value = mode_data.get(KEY.WAIT_BANDPASS)
        if value is None:
            raise ValueError("Decay method not defined for mode: %s" % repr(mode))
        return value

    def get_nearest_only(self, mode=None):
        # Nearest only defaults to TRUE!!!
        if not mode: mode = self._mode
        mode_data = self._mode_dict.get(mode)
        method = mode_data.get(KEY.SCORE_NEAREST_ONLY, True)
        return method

    def get_service_time(self, mode=None):
        # Service time defaults to "8:00"  (8 AM)
        if not mode: mode = self._mode
        mode_data = self._mode_dict.get(mode)
        method = mode_data.get(KEY.SERVICE_TIME, "8:00")
        return method

    def get_stop_demand(self, mode=None, check=True):
        if not mode: mode = self._mode
        mode_data = self._mode_dict.get(mode)
        method = mode_data.get(KEY.STOP_DEMAND, None)
        if check and method is not None:
            if self.get_demand_method(mode=mode, check=False) is None:
                raise ValueError("DEMAND_METHOD must be defined")
        return method

    def get_demand_method(self, mode=None, check=True):
        if not mode: mode = self._mode
        mode_data = self._mode_dict.get(mode)
        method = mode_data.get(KEY.DEMAND_METHOD)
        if check and method is not None:
            if self.get_stop_demand(mode=mode, check=False) is None:
                raise ValueError("STOP_DEMAND must be defined")
        return method

    def get_raster_clip(self, mode=None):
        if not mode: mode = self._mode
        mode_data = self._mode_dict.get(mode)
        value = mode_data.get(KEY.RASTER_CLIP, "percent_5.0")
        return value
