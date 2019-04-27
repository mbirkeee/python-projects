import ogr

class ShapeFileWriter(object):

    def __init__(self):

        self._raster_list = []
        self._stop_list = []
        self._da_list = []

    def add_da(self, da):
        self._da_list.append(da)

    def add_raster(self, raster):
        self._raster_list.append(raster)

    def add_stop(self, stop):
        print "add stop", repr(stop)
        self._stop_list.append(stop)

    def write_stop_file(self, file_name):

        f = open("stop_file.csv", "w")

        driver = ogr.GetDriverByName('Esri Shapefile')
        ds = driver.CreateDataSource(file_name)
        # layer = ds.CreateLayer('', None, ogr.wkbPolygon)
        layer = ds.CreateLayer('', None, ogr.wkbPoint)

        # Add attributes
        layer.CreateField(ogr.FieldDefn('fid', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('lat', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('lon', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('name', ogr.OFTString))

        defn = layer.GetLayerDefn()

        ## If there are multiple geometries, put the "for" loop here

        f.write("fid,stop_id,stop_name,lat,lng\n")

        for i, stop in enumerate(self._stop_list):

            stop_id = stop.get_id()
            name = stop.get_name()
            point = stop.get_point()
            lat, lon = point.get_lat_lng()
            ogr_point = point.get_ogr_point()

            # Create a new feature (attribute and geometry)
            feature = ogr.Feature(defn)
            feature.SetField('fid', stop_id)
            feature.SetField('lat', lat)
            feature.SetField('lon', lon)
            feature.SetField('name', name)

            geom = ogr_point
            feature.SetGeometry(geom)
            layer.CreateFeature(feature)

            f.write("%d,%d,%s,%f,%f\n" % (i+1, stop_id, name, lat, lon))
            feature = geom = None  # destroy these

        # Save and close everything
        ds = layer = feature = geom = None

        print "Wrote %s" % file_name
        f.close()

    def write_stop_da_intersections(self, intersection_list, file_name):

        driver = ogr.GetDriverByName('Esri Shapefile')
        ds = driver.CreateDataSource(file_name)
        layer = ds.CreateLayer('', None, ogr.wkbPolygon)

        # Add attributes
        layer.CreateField(ogr.FieldDefn('fid', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('group1_id', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('group2_id', ogr.OFTInteger))

        defn = layer.GetLayerDefn()

        ## If there are multiple geometries, put the "for" loop here

        for i, item in enumerate(intersection_list):

            fid = i + 1
            group1_id = item[0]
            group2_id = item[1]
            p = item[2]

            # Create a new feature (attribute and geometry)
            feature = ogr.Feature(defn)
            feature.SetField('fid', fid)
            feature.SetField('group1_id', group1_id)
            feature.SetField('group2_id', group2_id)

            geom = p.get_ogr_poly()
            feature.SetGeometry(geom)

            layer.CreateFeature(feature)
            feature = geom = None  # destroy these

        # Save and close everything
        ds = layer = feature = geom = None

        print "Wrote %s" % file_name

    def write_heatmap_da(self, file_name):

        driver = ogr.GetDriverByName('Esri Shapefile')
        ds = driver.CreateDataSource(file_name)
        layer = ds.CreateLayer('', None, ogr.wkbPolygon)

        layer.CreateField(ogr.FieldDefn('fid', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('da_id', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('score', ogr.OFTReal))

        defn = layer.GetLayerDefn()

        for i, da in enumerate(self._da_list):
            fid = i + 1

            score = da.get_score()
            da_id = da.get_id()

            # Create a new feature (attribute and geometry)
            feature = ogr.Feature(defn)
            feature.SetField('fid', fid)
            feature.SetField('da_id', da_id)
            feature.SetField('score', score)

            p = da.get_polygon()
            geom = p.get_ogr_poly()
            feature.SetGeometry(geom)

            layer.CreateFeature(feature)
            feature = geom = None  # destroy these

        # Save and close everything
        ds = layer = feature = geom = None
        print "Wrote %s" % file_name

    def write(self, file_name):

        driver = ogr.GetDriverByName('Esri Shapefile')
        ds = driver.CreateDataSource(file_name)
        layer = ds.CreateLayer('', None, ogr.wkbPolygon)

        # Add attributes
        layer.CreateField(ogr.FieldDefn('fid', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('da_id', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('raster_id', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('score', ogr.OFTReal))

        defn = layer.GetLayerDefn()

        ## If there are multiple geometries, put the "for" loop here

        for i, raster in enumerate(self._raster_list):

            fid = i + 1

            score = raster.get_score()
            da_id = raster.get_parent_id()
            raster_id = raster.get_id()

            # Create a new feature (attribute and geometry)
            feature = ogr.Feature(defn)
            feature.SetField('fid', fid)
            feature.SetField('da_id', da_id)
            feature.SetField('raster_id', raster_id)
            feature.SetField('score', score)

            p = raster.get_polygon()
            geom = p.get_ogr_poly()
            feature.SetGeometry(geom)

            layer.CreateFeature(feature)
            feature = geom = None  # destroy these

        # Save and close everything
        ds = layer = feature = geom = None

        print "Wrote %s" % file_name
