import { useEffect } from 'react';

import { useMap } from './map-provider';
import { useStore } from '../store/index';

const LayerOrder = () => {
  const { map } = useMap();

  const showStatesLayer = useStore((state) => state.showStatesLayer);
  const showCountriesLayer = useStore((state) => state.showCountriesLayer);
  const showCropLayer = useStore((state) => state.showCropLayer);
  const cropLayer = useStore((state) => state.cropLayer);

  useEffect(() => {
    if (!map) return;

    let layers = map.getStyle().layers;
    let ocean = layers.find((layer) => layer.source == 'ocean');
    let land = layers.find((layer) => layer.source == 'land');
    let lakesFill = layers.find((layer) => layer.source == 'lakes-fill');
    let lakes = layers.find((layer) => layer.source == 'lakes');
    let states = showStatesLayer ? layers.find((layer) => layer.source == 'states') : undefined;
    let countries = showCountriesLayer
      ? layers.find((layer) => layer.source == 'countries')
      : undefined;
    let cropExtentMask = showCropLayer
      ? layers.find((layer) => layer.source == `${cropLayer}-extent-mask`)
      : undefined;
    let cropExtent = showCropLayer
      ? layers.find((layer) => layer.source == `${cropLayer}-extent`)
      : undefined;

    map.moveLayer(ocean.id, land.id);
    map.moveLayer(lakes.id, ocean.id);
    map.moveLayer(lakesFill.id, lakes.id);
    map.moveLayer('raster', lakesFill.id);
    if (states) map.moveLayer(states.id, land.id);
    if (countries) map.moveLayer(countries.id, states?.id || land.id);
    if (states && countries) map.moveLayer(states.id, countries.id);
    if (cropExtentMask) map.moveLayer(cropExtentMask.id, ocean.id);
    if (cropExtent) map.moveLayer(cropExtent.id, ocean.id);
    if (cropExtentMask && cropExtent) map.moveLayer(cropExtentMask.id, cropExtent.id);
  }, [map, showCountriesLayer, showStatesLayer, showCropLayer]);

  return null;
};

export default LayerOrder;
