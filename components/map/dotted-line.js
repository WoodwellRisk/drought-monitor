import { useEffect, useState, useRef } from 'react'
import { useMapbox } from '@carbonplan/maps'
import { v4 as uuidv4 } from 'uuid'

export const updatePaintProperty = (map, ref, key, value) => {
  const { current: id } = ref
  if (map.getLayer(id)) {
    map.setPaintProperty(id, key, value)
  }
}

const DottedLine = ({
  source,
  variable,
  color,
  id,
  maxZoom = 5,
  opacity = 1,
  blur = 0.4,
  width = 0.5,
}) => {
  const { map } = useMapbox()
  const removed = useRef(false)

  const sourceIdRef = useRef()
  const layerIdRef = useRef()

  const [mapZoom, setMapZoom] = useState(map.getZoom())

  useEffect(() => {
    console.log(mapZoom)
  }, [mapZoom])

  map.on('zoom', () => {
    setMapZoom(map.getZoom());
  });

  useEffect(() => {
    sourceIdRef.current = id || uuidv4()
    const { current: sourceId } = sourceIdRef
    if (!map.getSource(sourceId)) {
      map.addSource(sourceId, {
        type: 'vector',
        tiles: [`${source}/{z}/{x}/{y}.pbf`],
      })
      if (maxZoom) {
        map.getSource(sourceId).maxzoom = maxZoom
      }
    }
  }, [id])

  useEffect(() => {
    const layerId = layerIdRef.current || uuidv4()
    layerIdRef.current = layerId
    const { current: sourceId } = sourceIdRef
    if (!map.getLayer(layerId)) {
      // https://github.com/mapbox/mapbox-gl-js/issues/3045
      // https://docs.mapbox.com/style-spec/reference/layers/#layout-line-line-cap
      map.addLayer({
        id: layerId,
        type: 'line',
        source: sourceId,
        'source-layer': variable,
        layout: { 
          visibility: 'visible',
          'line-cap': 'butt',
          'line-join': 'round',
        },
        paint: {
          'line-blur': blur,
          'line-color': color,
          'line-opacity': opacity,
          'line-width': width,
          "line-dasharray": [1, 1]
        },
      });
    }

    return () => {
      if (!removed.current) {
        if (map.getLayer(layerId)) {
          map.removeLayer(layerId)
        }
      }
    }
  }, [])

  useEffect(() => {
    updatePaintProperty(map, layerIdRef, 'line-color', color)
  }, [color])

  useEffect(() => {
    updatePaintProperty(map, layerIdRef, 'line-opacity', opacity)
  }, [opacity])

  useEffect(() => {
    updatePaintProperty(map, layerIdRef, 'line-blur', blur)
  }, [blur])

  useEffect(() => {
    if(mapZoom < 3) {
      updatePaintProperty(map, layerIdRef, 'line-width', width / 2)
      updatePaintProperty(map, layerIdRef, 'line-dasharray',  [1, 1])
    } else if(mapZoom < 4) {
      updatePaintProperty(map, layerIdRef, 'line-width', width)
      updatePaintProperty(map, layerIdRef, 'line-dasharray',  [1, 1])
    } else if(mapZoom < 5) {
      updatePaintProperty(map, layerIdRef, 'line-width', width * 1.5)
      updatePaintProperty(map, layerIdRef, 'line-dasharray',  [1, 1])
    } else if(mapZoom < 6) {
      updatePaintProperty(map, layerIdRef, 'line-width', width * 2.0)
      updatePaintProperty(map, layerIdRef, 'line-dasharray',  [1, 1])
    } else if(mapZoom < 8) {
      updatePaintProperty(map, layerIdRef, 'line-width', width * 3)
      updatePaintProperty(map, layerIdRef, 'line-dasharray',  [1, 1])
    } else {
      updatePaintProperty(map, layerIdRef, 'line-width', width * 4)
      updatePaintProperty(map, layerIdRef, 'line-dasharray',  [1, 1])
    }
  }, [mapZoom])

  return null
}

export default DottedLine