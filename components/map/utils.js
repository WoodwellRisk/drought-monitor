export const updatePaintProperty = (map, ref, key, value) => {
  if (!map) return;

  const { current: id } = ref;
  if (map.getLayer(id)) {
    map.setPaintProperty(id, key, value);
  }
};

// https://www.delftstack.com/howto/javascript/rgb-to-hex-javascript/
export const rgbArrayToHex = (rgbArray) => {
  return rgbArray.map((rgb) => {
    const [r, g, b] = rgb;
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
  });
};
