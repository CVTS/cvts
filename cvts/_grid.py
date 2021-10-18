from math import floor, ceil
import numpy as np
import logging
from scipy.ndimage import convolve



#: Minimum latitude of the raster 'covering' Vietnam.
MINLAT   =   7.8584

#: Approximate maximum latitude of the raster 'covering' Vietnam.
MAXLAT   =  23.8882

#: Minimum latitude of the raster 'covering' Vietnam.
MINLON   = 101.9988

#: Approximate maximum longitude of the raster 'covering' Vietnam.
MAXLON   = 109.3325

#: Cellsize of the raster 'covering' Vietnam.
CELLSIZE =   0.1

#: NA value to use for the raster 'covering' Vietnam.
NA_VALUE = -9999

logger = logging.getLogger(__name__)


class Grid:
    """Raster used for accumulating stop points."""

    def __init__(
            self,
            minlat   = MINLAT,
            minlon   = MINLON,
            maxlat   = MAXLAT,
            maxlon   = MAXLON,
            cellsize = CELLSIZE,
            na_value = NA_VALUE):
        self.minlat = minlat
        self.minlon = minlon
        self.cellsize = cellsize
        self.na_value = na_value
        self.ncol = int(ceil((maxlon - minlon) / self.cellsize))
        self.nrow = int(ceil((maxlat - minlat) / self.cellsize))
        self.minlat = minlat
        self.minlon = minlon
        self.maxlat = minlat + self.nrow * cellsize
        self.maxlon = minlon + self.ncol * cellsize
        self.cells = np.zeros((self.nrow, self.ncol), int)

    def increment(self, lon, lat):
        """Increment the count in cell containing the point (*lon*, *lat*)."""
        try:
            row = self.nrow - int(floor((lat - self.minlat) / self.cellsize)) - 1
            col =             int(floor((lon - self.minlon) / self.cellsize))
            if 0 <= col < self.ncol and 0 <= row < self.nrow:
                self.cells[row, col] += 1
            return row, col
        except ValueError as e:
            logger.error('value error: {} at ({:.2f}, {:.2f})'.format(e, lat, lon))

    def increment_many(self, lons, lats):
        """Increment the count in cells containing the points (*lons*, *lats*).

        Should be much more efficient than using :py:meth:`Grid.increment`
        repeatedly.
        """
        valid_lls = np.all(np.vstack((
            lats > self.minlat, lats < self.maxlat,
            lons > self.minlon, lons < self.maxlon)), axis=0)

        lons = lons[valid_lls]
        lats = lats[valid_lls]

        row_cols = np.array([
            self.nrow - (np.floor((lats - self.minlat) / self.cellsize)) - 1,
                        (np.floor((lons - self.minlon) / self.cellsize))],
            dtype='int32')

        indexes, counts = np.unique(row_cols, return_counts=True, axis=1)
        self.cells[indexes[0,:],indexes[1,:]] += counts

        return row_cols.T, lons, lats

    def convolve(self, kernel):
        return convolve(self.cells, kernel)

    def save(self, fn):
        """Save as ASCII grid."""
        with open(fn, 'w') as f:
            f.write('ncols        {}\n'.format(self.ncol))
            f.write('nrows        {}\n'.format(self.nrow))
            f.write('xllcorner    {}\n'.format(self.minlon))
            f.write('yllcorner    {}\n'.format(self.minlat))
            f.write('cellsize     {}\n'.format(self.cellsize))
            f.write('NODATA_value {}\n'.format(self.na_value))
            f.write(' '.join([str(i) for i in self.cells.flatten()]))
