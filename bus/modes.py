from constants import KEY

class MODE(object):
    ONE         = 1
    TWO         = 2
    THREE       = 3

class BUFFER_METHOD(object):
    CIRCLE_400 = "circle_400"
    SQUARE_709 = "square_709"
    DIAMOND_500 = "diamond_500"

class SCORE_METHOD(object):
    STOP_COUNT = "simple_stop_count"


MODE_DICT = {
    MODE.ONE : {
        KEY.BUFFER_METHOD   : BUFFER_METHOD.CIRCLE_400,
        KEY.SCORE_METHOD    : SCORE_METHOD.STOP_COUNT,
        KEY.DISTANCE_DECAY  : False,
        KEY.STOP_DEMAND     : None
    },
    MODE.TWO : {
        KEY.BUFFER_METHOD   : BUFFER_METHOD.SQUARE_709,
        KEY.SCORE_METHOD    : SCORE_METHOD.STOP_COUNT,
        KEY.DISTANCE_DECAY  : False,
        KEY.STOP_DEMAND     : None
    },
    MODE.THREE : {
        KEY.BUFFER_METHOD   : BUFFER_METHOD.DIAMOND_500,
        KEY.SCORE_METHOD    : SCORE_METHOD.STOP_COUNT,
        KEY.DISTANCE_DECAY  : False,
        KEY.STOP_DEMAND     : None
    }

}