class BASE(object):
    JULY = "../data/sts/csv/2018_08_05/"
    JUNE = "../data/sts/csv/2018_05_04/"
    BRT  = "../data/shapefiles/brt_lines/brt"

class SERVICE(object):
    UNKNOWN     = 0
    MWF         = 1
    SAT         = 2
    SUN         = 3

class DATASET(object):
    JUNE        = 'june'
    JULY        = 'july'
    BRT_ORIG    = 'brt'

class MODE(object):
    ONE         = "1"
    TWO         = "2"

class BUFFER(object):
    CIRCLE_400 = "circle_400"

class KEY(object):
    SERVICE_TYPE        = 'serv_type'
    DEPART_TIME         = 'depart_time'
    ROUTE_ID            = 'route_id'
    TRIP_ID             = 'trip_id'
    HEADSIGN            = 'headsign'
    DIRECTION           = 'direction'
    STOP_ID             = 'stop_id'
    EST_WAIT_SEC        = 'est_wait_sec'
    DISTANCE            = 'dist'
    POPULATION          = 'pop'
    WEIGHT              = 'weight'
    DAILY_DEPARTURES    = 'daily_departures'

    BAD_ID              = 'bad_id'
    POINT               = 'point'
    NAME                = 'name'

    STOP_SET            = 'stop_set'
    BUFFER              = 'buffer'