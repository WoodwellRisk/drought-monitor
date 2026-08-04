import { useEffect, useRef, useState } from 'react';
import { useThemeUI, Box } from 'theme-ui';
import { useMap } from './map-provider';
import { v4 as uuidv4 } from 'uuid';

import { useStore } from '../store/index';

export default function PointQuery({ key, id }) {
  const { theme } = useThemeUI();
  const { map } = useMap();

  const removed = useRef(false);
  const sourceIdRef = useRef();
  const layerIdRef = useRef();

  const historicalRaster = useStore((state) => state.historicalRaster);
  const forecastRaster = useStore((state) => state.forecastRaster);

  const historicalDates = useStore((state) => state.historicalDates);
  const forecastDates = useStore((state) => state.forecastDates);
  const window = useStore((state) => state.window);
  const timePeriod = useStore((state) => state.timePeriod);

  const queryPoint = map.getCenter();
  const [coords, setCoords] = useState([queryPoint['lng'], queryPoint['lat']]);

  function toFourDecimalPlaces(num) {
    return parseFloat(num.toFixed(4));
  }

  const [coordinates, setCoordinates] = useState([
    `Longitude: ${toFourDecimalPlaces(coords[0])}`,
    `Latitude: ${toFourDecimalPlaces(coords[1])}`,
  ]);

  // https://docs.mapbox.com/mapbox-gl-js/example/drag-a-point/
  const draggablePoint = {
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: coords,
        },
      },
    ],
  };

  useEffect(() => {
    map.on('remove', () => {
      removed.current = true;
    });
  }, []);

  useEffect(() => {
    sourceIdRef.current = id || uuidv4();
    const { current: sourceId } = sourceIdRef;

    if (!map.getSource(sourceId)) {
      draggablePoint.features[0].geometry.coordinates = coords;

      map.addSource(sourceId, {
        type: 'geojson',
        data: draggablePoint,
      });
    }
  }, [key]);

  useEffect(() => {
    const { current: sourceId } = sourceIdRef;
    layerIdRef.current = uuidv4();
    const { current: layerId } = layerIdRef;

    if (!map.getLayer(layerId)) {
      map.addLayer({
        id: layerId,
        type: 'circle',
        source: sourceId,
        paint: {
          'circle-radius': ['interpolate', ['linear'], ['zoom'], 5, 10, 7, 20],
          'circle-color': theme.rawColors.primary,
          'circle-stroke-width': 2,
          'circle-stroke-color': theme.rawColors.primary,
          'circle-opacity': 0.5,
        },
      });
    }

    function onMove(e) {
      const coords = e.lngLat;

      map.getCanvas().style.cursor = 'grabbing';

      draggablePoint.features[0].geometry.coordinates = [coords.lng, coords.lat];
      map.getSource(sourceIdRef.current).setData(draggablePoint);
    }

    function onUp(e) {
      const coords = e.lngLat;
      setCoords([coords.lng, coords.lat]);

      setCoordinates([
        `Longitude: ${toFourDecimalPlaces(coords.lng)}`,
        `Latitude:   ${toFourDecimalPlaces(coords.lat)}`,
      ]);

      map.getCanvas().style.cursor = '';
      map.off('mousemove', onMove);
      map.off('touchmove', onMove);
    }

    map.on('mouseenter', layerId, () => {
      map.getCanvas().style.cursor = 'move';
    });

    map.on('mouseleave', layerId, () => {
      map.setPaintProperty(layerId, 'circle-color', theme.rawColors.primary);
      map.getCanvas().style.cursor = '';
    });

    map.on('mouseup', layerId, (e) => {
      e.preventDefault();
      map.getCanvas().style.cursor = 'grab';
      map.on('mousemove', onMove);
      map.once('mouseup', onUp);
      map.setPaintProperty(layerId, 'circle-opacity', 0.5);
    });

    map.on('mousedown', layerId, (e) => {
      map.setPaintProperty(layerId, 'circle-opacity', 1.0);

      e.preventDefault();

      map.getCanvas().style.cursor = 'grab';
      map.on('mousemove', onMove);
      map.once('mouseup', onUp);
    });

    map.on('touchstart', layerId, (e) => {
      if (e.points.length !== 1) return;
      e.preventDefault();
      map.on('touchmove', onMove);
      map.once('touchend', onUp);
    });

    return () => {
      if (!removed.current) {
        if (map.getLayer(layerId)) {
          map.removeLayer(layerId);
        }
      }
    };
  }, []);

  useEffect(() => {
    (async () => {
      if (!historicalRaster && !forecastRaster) return;

      // give the rasters time to load
      await new Promise((resolve) => setTimeout(resolve, 500));

      try {
        const historicalResult = await historicalRaster.queryData(
          { type: 'Point', coordinates: coords },
          { time: historicalDates }
        );
        console.log(historicalResult);
      } catch (error) {
        console.error('Error querying historical raster:', error);
      }

      try {
        const forecastResult = await forecastRaster.queryData(
          { type: 'Point', coordinates: coords },
          { time: forecastDates }
        );
        console.log(forecastResult);
        console.log();
      } catch (error) {
        console.error('Error querying forecast raster:', error);
      }
    })();
  }, [historicalRaster, window, coords]);

  return (
    <Box
      as="div"
      id={'coordinates-container'}
      sx={{
        borderColor: 'primary',
        borderStyle: 'solid',
        borderWidth: '1px',
        borderRadius: '0.2rem',
        color: '#fff',
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        zIndex: 10,
        position: 'absolute',
        right: [2],
        bottom: [20, 20, 20, 20],
        padding: '0.3rem 0.7rem',
        margin: 0,
        display: coordinates ? 'block' : 'none',
        fontWeight: 'bold',
        fontSize: '0.9rem',
        lineHeight: '1.2rem',

        right: [2],
        bottom: [20, 20, 20, 20],
      }}
    >
      {coordinates &&
        coordinates.map((coord, idx) => (
          <p key={idx} style={{ margin: 0 }}>
            {coord}
          </p>
        ))}
    </Box>
  );
}
