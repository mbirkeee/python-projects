import ogr

class ShapeFileWriter(object):

    def __init__(self):

        self._raster_list = []

    def add_raster(self, raster, score):

        self._raster_list.append((raster, score))

    def write(self, file_name):

        driver = ogr.GetDriverByName('Esri Shapefile')
        ds = driver.CreateDataSource(file_name)
        layer = ds.CreateLayer('', None, ogr.wkbPolygon)

        # Add one attribute
        layer.CreateField(ogr.FieldDefn('fid', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('da_id', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('raster_id', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('score', ogr.OFTReal))

        defn = layer.GetLayerDefn()

        ## If there are multiple geometries, put the "for" loop here

        for i, item in enumerate(self._raster_list):

            fid = i + 1
            raster = item[0]
            score = item[1]

            da_id = raster.get_parent_id()
            raster_id= raster.get_id()

            # Create a new feature (attribute and geometry)
            feature = ogr.Feature(defn)
            feature.SetField('fid', fid)
            feature.SetField('da_id', da_id)
            feature.SetField('raster_id', raster_id)
            feature.SetField('score', score)

            # Make a geometry, from Shapely object
            # geom = ogr.CreateGeometryFromWkb(poly.wkb)

            p = raster.get_polygon()
            geom = p.get_ogr_poly()
            feature.SetGeometry(geom)

            layer.CreateFeature(feature)
            feature = geom = None  # destroy these

        # Save and close everything
        ds = layer = feature = geom = None

        print "Wrote %s" % file_name