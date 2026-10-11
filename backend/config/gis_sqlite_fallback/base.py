"""Minimal GeoDjango database backend for SQLite *without* SpatiaLite.

Purpose: run the test suite in CI sandboxes or on dev laptops that have no
system SpatiaLite/GDAL install. Geometry columns are stored as WKT text and
round-tripped through GEOS (loaded via the TBS_BUNDLED_GIS=1 shapely wheel
trick in settings/base.py).

LIMITATIONS - do not use outside tests:
  * No spatial SQL (contains/intersects/dwithin lookups will fail)
  * SRID is not persisted in the stored WKT
Production and normal development use PostGIS via docker-compose.
"""
from django.contrib.gis.db.backends.spatialite.operations import SpatiaLiteOperations
from django.db.backends.sqlite3.base import DatabaseWrapper as SQLiteDatabaseWrapper


class DatabaseOperations(SpatiaLiteOperations):
    # Inherit spatial ops (Adapter, placeholders) from SpatiaLite, then
    # neutralize everything that would require the libspatialite extension.

    # SpatiaLite wraps geometry selections in CAST(AsEWKB(%s) AS BLOB); plain
    # text columns need no wrapper.
    select = "%s"

    def geo_db_type(self, f):
        return "text"

    def get_geometry_converter(self, expression):
        # SpatiaLite decodes EWKB blobs; our columns hold WKT text instead.
        from django.contrib.gis.geos import GEOSGeometry

        srid = expression.output_field.srid

        def converter(value, expression, connection):
            if value is None:
                return None
            if isinstance(value, memoryview):
                value = bytes(value)
            geom = GEOSGeometry(value)
            geom.srid = srid
            return geom

        return converter

    def get_geom_placeholder(self, f, value, compiler):
        # The adapter serializes the geometry to a quoted WKT string, so a
        # plain parameter placeholder is all that is needed.
        return "%s"


class DatabaseWrapper(SQLiteDatabaseWrapper):
    ops_class = DatabaseOperations
