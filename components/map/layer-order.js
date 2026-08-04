import { useEffect } from 'react';

import { useMap } from './map-provider';
import { useStore } from '../store/index';

const LayerOrder = () => {
  const { map } = useMap();

  const timePeriod = useStore((state) => state.timePeriod);
  const window = useStore((state) => state.window);
  const showStatesLayer = useStore((state) => state.showStatesLayer);
  const showCountriesLayer = useStore((state) => state.showCountriesLayer);
  const showCropLayer = useStore((state) => state.showCropLayer);
  const cropLayer = useStore((state) => state.cropLayer);
  const showRegionPicker = useStore((state) => state.showRegionPicker);

  useEffect(() => {
    if (!map) return;

    let layers = map.getStyle().layers;

    // find base layers - always shown
    let ocean = layers.find((layer) => layer.source == 'ocean');
    let land = layers.find((layer) => layer.source == 'land');
    let lakesFill = layers.find((layer) => layer.source == 'lakes-fill');
    let lakes = layers.find((layer) => layer.source == 'lakes');

    // find conditional layers
    let states = showStatesLayer ? layers.find((layer) => layer.source == 'states') : undefined;
    let countries = showCountriesLayer
      ? layers.find((layer) => layer.source == 'countries')
      : undefined;
    let cropExtentMask = cropLayer
      ? layers.find((layer) => layer.source == `${cropLayer}-extent-mask`)
      : undefined;
    let cropExtent = cropLayer
      ? layers.find((layer) => layer.source == `${cropLayer}-extent`)
      : undefined;
    let pointQuery = showRegionPicker
      ? layers.find((layer) => layer.source == `point-query`)
      : undefined;

    // https://docs.mapbox.com/mapbox-gl-js/api/map/#map#movelayer
    // build the complete target order list from bottom to top
    // map.moveLayer(a, b) will put a below b
    // map.moveLayer('forecast-raster', 'historical-raster')
    map.moveLayer('forecast-raster', lakesFill.id);
    map.moveLayer('historical-raster', lakesFill.id);
    if (cropExtentMask) map.moveLayer(cropExtentMask.id, lakesFill.id);
    if (cropExtent) map.moveLayer(cropExtent.id, lakesFill.id);
    if (cropExtentMask && cropExtent) map.moveLayer(cropExtentMask.id, cropExtent.id);
    map.moveLayer(lakesFill.id, lakes.id);
    map.moveLayer(lakes.id, ocean.id);
    map.moveLayer(ocean.id, land.id);
    if (states) map.moveLayer(states.id, land.id);
    if (countries) map.moveLayer(countries.id, states?.id || land.id);
    if (states && countries) map.moveLayer(states.id, countries.id);
    if (pointQuery) map.moveLayer(land.id, pointQuery.id);
  }, [map, showCountriesLayer, showStatesLayer, cropLayer, timePeriod, window, showRegionPicker]);

  return null;
};

export default LayerOrder;
