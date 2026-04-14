import { create } from 'zustand';

const MIN_HISTORICAL_DATE = '1991-01-01';
const MAX_HISTORICAL_DATE = '2026-03-01';

export const arrayRange = (start, end, step) => {
  let output = [];
  for (let idx = start; idx < end; idx += step) {
    output.push(idx);
  }
  return output;
};

const validMonths = arrayRange(1, 12, 1)
  .map(String)
  .map((val) => val.padStart(2, '0'));
const validYears = arrayRange(1991, 2027, 1).map(String);

const generateDates = (startDate, monthsRange) => {
  const dates = [];
  const [year, month, day] = startDate.split('-').map(Number);

  monthsRange.forEach((value) => {
    const date = new Date(year, month - 1 + value, day);
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    dates.push(`${y}-${m}-${d}`);
  });

  return dates;
};

// https://stackoverflow.com/a/15158873
const getDifferenceInMonths = (startDateString, endDateString) => {
  let startDate = new Date(startDateString);
  let endDate = new Date(endDateString);

  if (startDate > endDate) {
    throw new Error('End date must be later than start date.');
  }

  return (
    // the `+ 1` keeps the end date included, which we want
    endDate.getMonth() -
    startDate.getMonth() +
    1 +
    (endDate.getFullYear() - startDate.getFullYear()) * 12
  );
};

const createHistoricalDates = () => {
  let minDate = MIN_HISTORICAL_DATE;
  let maxDate = MAX_HISTORICAL_DATE;
  let monthsBetweenDates = getDifferenceInMonths(minDate, maxDate);
  let monthsRange = arrayRange(0, monthsBetweenDates, 1);

  return {
    maxHistoricalDate: maxDate,
    historicalDate: maxDate,
    historicalDates: generateDates(minDate, monthsRange),
    historicalSliderIndex: monthsRange.at(-1),
    time: maxDate,
    validMonths: validMonths,
    validYears: validYears,
  };
};

export const useStore = create((set, get) => ({
  // map container state
  zoom: 1.3,
  setZoom: (zoom) => set({ zoom }),

  maxZoom: 8,

  zoomToBox: null,
  setZoomToBox: (zoomToBox) => set({ zoomToBox }),

  zoomInitialized: false,
  setZoomInitialized: (zoomInitialized) => set({ zoomInitialized }),

  center: [-40, 40],
  setCenter: (center) => set({ center }),

  // https://github.com/mapbox/mapbox-gl-js/blob/2b6915c8004a5b759338f3a7d92fb2882db9dd5c/src/geo/lng_lat.js#L192-L201
  // https://docs.mapbox.com/mapbox-gl-js/example/restrict-bounds/
  bounds: [
    [-360, -60.5], // southwest
    [360, 85], // northeast
  ],

  // general / raster state variables
  variable: 'perc',
  setVariable: (variable) => set({ variable }),

  windowOptions: { 3: true, 12: false },
  setWindowOptions: (windowOptions) => set({ windowOptions }),

  window: '3',
  setWindow: (window) => set({ window }),

  opacity: 1,
  setOpacity: (opacity) => set({ opacity }),

  // handle dates
  ...createHistoricalDates(),
  setHistoricalDate: (historicalDate) => set({ historicalDate }),
  setHistoricalSliderIndex: (historicalSliderIndex) => set({ historicalSliderIndex }),
  setTime: (time) => set({ time }),

  showTimeError: false,
  setShowTimeError: (showTimeError) => set({ showTimeError }),

  colormapName: 'redteal',
  setColormapName: (colormapName) => set({ colormapName }),

  clim: [0.0, 1.0],
  setClim: (clim) => set({ clim }),

  regionData: { loading: true },
  setRegionData: (regionData) => set({ regionData }),

  regionLoadingData: true,
  setRegionDataLoading: (regionLoadingData) => set({ regionLoadingData }),

  showRegionPicker: false,
  setShowRegionPicker: (showRegionPicker) => set({ showRegionPicker }),

  // crop-specific state variables
  crops: ['barley', 'cocoa', 'coffee', 'cotton', 'maize', 'rice', 'soybean', 'sugarcane', 'wheat'],
  cropValues: {
    barley: false,
    cocoa: false,
    coffee: false,
    cotton: false,
    maize: false,
    rice: false,
    soybean: false,
    sugarcane: false,
    wheat: false,
  },
  setCropValues: (cropValues) => set({ cropValues }),

  cropLayer: false,
  setCropLayer: (cropLayer) => set({ cropLayer }),

  showCropLayer: {}, // or is it this: [{}]
  setShowCropLayer: (showCropLayer) => set({ showCropLayer }),

  // show / hide layers
  showDrought: true,
  setShowDrought: (showDrought) => set({ showDrought }),

  display: true,
  setDisplay: (display) => set({ display }),

  showCountriesOutline: false,
  setShowCountriesOutline: (showCountriesOutline) => set({ showCountriesOutline }),

  showStatesOutline: false,
  setShowStatesOutline: (showStatesOutline) => set({ showStatesOutline }),

  sliding: false,
  setSliding: (sliding) => set({ sliding }),

  showAbout: false,
  setShowAbout: (showAbout) => set({ showAbout }),

  showAboutMobile: false,
  setShowAboutMobile: (showAboutMobile) => set({ showAboutMobile }),

  showMenu: false,
  setShowMenu: (showMenu) => set({ showMenu }),

  showOverlays: false,
  setShowOverlays: (showOverlays) => set({ showOverlays }),
}));
