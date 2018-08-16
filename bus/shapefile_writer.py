import ogr

class ShapeFileWriter(object):

    def __init__(self):

        self._raster_list = []

    def add_raster(self, raster):

        self._raster_list.append(raster)

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
            raster_id= raster.get_id()

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