import pprint

from constants import KEY
from dataset import SERVICE

class BUFFER_METHOD(object):
    NONE            = "none"
    CIRCLE_400      = "circle_400"
    SQUARE_709      = "square_709"
    DIAMOND_500     = "diamond_500"
    DIAMOND_400     = "diamond_400"
    NETWORK_400     = "network_400"

# List of supported buffer methods
BUFFER_LIST = [
    BUFFER_METHOD.NONE,
    BUFFER_METHOD.CIRCLE_400,
    BUFFER_METHOD.SQUARE_709,
    BUFFER_METHOD.DIAMOND_500,
    BUFFER_METHOD.DIAMOND_400,
    BUFFER_METHOD.NETWORK_400
]

class DECAY_METHOD(object):
    NONE        = None
    CROW_250    = "crow_250"    # Euclidian distance, butterworth dpass = 250
    CROW_100    = "crow_100"    # Euclidian distance, butterworth dpass = 100
    CROW_200    = "crow_200"    # Euclidian distance, butterworth dpass = 200
    CROW_400    = "crow_400"    # Euclidian distance, butterworth dpass = 200
    GRID_250    = "grid_250"    #

class SCORE_METHOD(object):
    STOP_COUNT              = "simple_stop_count"
    DEPARTURES_PER_HOUR     = "departures_per_hour"
    DEPARTURES_PER_DAY      = "departures_per_day"
    DEPARTURES_PER_WEEK     = "departures_per_week"
    DIST_TO_CLOSEST_STOP    = "dist_to_closest_stop"
    DECAYED_WAIT            = "decayed_wait"

#-----------------------------------------------------------------------
MODE_DICT = {
    1 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
        KEY.STOP_DEMAND         : None
    },
    2 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.SQUARE_709,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
        KEY.STOP_DEMAND         : None
    },
    3 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_500,
        KEY.SCORE_METHOD        : SCORE_METHOD.STOP_COUNT,
        KEY.STOP_DEMAND         : None
    },
    4 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : False,
        KEY.STOP_DEMAND         : None
    },
    5 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.SCORE_NEAREST_ONLY  : False,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_250,
        KEY.STOP_DEMAND         : None
    },
    6 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : False,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_250,
        KEY.STOP_DEMAND         : None
    },
    7 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_250,
        KEY.STOP_DEMAND         : None
    },
    8 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_100,
        KEY.STOP_DEMAND         : None,
        KEY.SERVICE_TYPE        : SERVICE.MWF
    },
    9 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_DAY,
        KEY.SCORE_NEAREST_ONLY  : True,
        KEY.DECAY_METHOD        : DECAY_METHOD.GRID_250,
        KEY.STOP_DEMAND         : None,
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
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_250,
        KEY.STOP_DEMAND         : None,
    },
    13 : {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DEPARTURES_PER_HOUR,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_250,
        KEY.STOP_DEMAND         : None,
        KEY.NORMALIZE_VALUE     : 6.0,
    },
    14: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_250,
        KEY.STOP_DEMAND         : None,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 10.0,
    },
    15: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_250,
        KEY.STOP_DEMAND         : None,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    },
    16: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_200,
        KEY.STOP_DEMAND         : None,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    },
    17: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_100,
        KEY.STOP_DEMAND         : None,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    },
    18: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DECAY_METHOD        : DECAY_METHOD.CROW_400,
        KEY.STOP_DEMAND         : None,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    },
    19: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.NETWORK_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DECAY_METHOD        : DECAY_METHOD.GRID_250,
        KEY.STOP_DEMAND         : None,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    },
    20: {
        KEY.BUFFER_METHOD       : BUFFER_METHOD.DIAMOND_400,
        KEY.SCORE_METHOD        : SCORE_METHOD.DECAYED_WAIT,
        KEY.DECAY_METHOD        : DECAY_METHOD.GRID_250,
        KEY.STOP_DEMAND         : None,
        KEY.NORMALIZE_VALUE     : 6.0,
        KEY.WAIT_BANDPASS       : 3.0,
    }
}

class ModeMan(object):

    def __init__(self, mode=None):

        self._mode_dict = MODE_DICT
        self.validate()

        self._mode = mode
        if mode is not None:
            self.set_mode(mode)

    def set_mode(self, mode):
        if not self.valid(mode):
            print "Invalid mode. Supported modes are:"
            self.print_modes()
            raise ValueError("Invalid mode")
        self._mode = mode

    def compare_modes(self, mode1, mode2, key1, key2):

        if mode1.get(KEY.BUFFER_METHOD, BUFFER_METHOD.NONE) != mode2.get(KEY.BUFFER_METHOD, BUFFER_METHOD.NONE):
            return False

        if mode1.get(KEY.SCORE_METHOD) != mode2.get(KEY.SCORE_METHOD):
            return False

        if mode1.get(KEY.DISTANCE_METHOD) != mode2.get(KEY.DISTANCE_METHOD):
            return False

        if mode1.get(KEY.SCORE_NEAREST_ONLY, True) != mode2.get(KEY.SCORE_NEAREST_ONLY, True):
            return False

        if mode1.get(KEY.DECAY_METHOD, None) != mode2.get(KEY.DECAY_METHOD, None):
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

    def get_buffer_method(self):
        # Buffer method defaults to BUFFER_METHOD.NONE
        mode_data = self._mode_dict.get(self._mode)
        return mode_data.get(KEY.BUFFER_METHOD, BUFFER_METHOD.NONE)

    def get_score_method(self):
        # Score method must be defined (if requested)
        mode_data = self._mode_dict.get(self._mode)
        method = mode_data.get(KEY.SCORE_METHOD)
        if method is None:
            raise ValueError("Score method not defined for mode: %s" % repr(self._mode))
        return method

    def get_distance_method(self):
        # Distance method must be defined (if requested)
        mode_data = self._mode_dict.get(self._mode)
        method = mode_data.get(KEY.DISTANCE_METHOD)
        if method is None:
            raise ValueError("Score method not defined for mode: %s" % repr(self._mode))
        return method

    def get_decay_method(self):
        # Distance method must be defined (if requested)
        mode_data = self._mode_dict.get(self._mode)
        method = mode_data.get(KEY.DECAY_METHOD)
        if method is None:
            raise ValueError("Decay method not defined for mode: %s" % repr(self._mode))
        return method

    def get_service_type(self):
        # Service defaults to MWF
        mode_data = self._mode_dict.get(self._mode)
        method = mode_data.get(KEY.SERVICE_TYPE, SERVICE.MWF)
        return method

    def get_normalize_value(self):
        # Normalize value can be None
        mode_data = self._mode_dict.get(self._mode)
        method = mode_data.get(KEY.NORMALIZE_VALUE)
        return method

    def get_wait_bandpass(self):
        # Wait bandpass must be defined (if requested)
        mode_data = self._mode_dict.get(self._mode)
        value = mode_data.get(KEY.WAIT_BANDPASS)
        if value is None:
            raise ValueError("Decay method not defined for mode: %s" % repr(self._mode))
        return value

    def get_nearest_only(self):
        # Nearest only defaults to TRUE!!!
        mode_data = self._mode_dict.get(self._mode)
        method = mode_data.get(KEY.SCORE_NEAREST_ONLY, True)
        return method

    def get_service_time(self):
        # Service time defaults to "8:00"  (8 AM)
        mode_data = self._mode_dict.get(self._mode)
        method = mode_data.get(KEY.SERVICE_TIME, "8:00")
        return method
