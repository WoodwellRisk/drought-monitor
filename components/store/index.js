import { create } from 'zustand'

const useStore = create((set, get) => ({
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
        [360, 85] // northeast
    ],

    updatingData: false,

    // general / raster state variables
    variable: 'perc',
    setVariable: (variable) => set({ variable }),

    windowOptions: { '3': true, '12': false, },
    setWindowOptions: (windowOptions) => set({ windowOptions }),

    window: '3',
    setWindow: (window) => set({ window }),

    opacity: 1,
    setOpacity: (opacity) => set({ opacity }),

    minDate: '1991-01-01',
    maxDate: '2026-01-01',

    year: 2026,
    setYear: (year) => set({ year }),

    monthValues: ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'],
    month: '01',
    setMonth: (month) => set({ month }),
    
    monthIdx: 0,
    setMonthIdx: (monthIdx) => set({ monthIdx }),

    time: (year, month) => set(`${year}-${month}-01`),
    setTime: (time) => set({ time }),

    minYear: () => {
        const { minDate } = get()
        return `${ new Date(minDate + 'T00:00:00').getFullYear() }`
    },
    maxYear: () => {
        const { maxDate } = get()
        return `${ new Date(maxDate + 'T00:00:00').getFullYear() }`
    },

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
    crops: ["barley", "cocoa", "coffee", "cotton", "maize", "rice", "soybean", "sugarcane", "wheat"],
    cropValues: {
        "barley": false,
        "cocoa": false,
        "coffee": false,
        "cotton": false,
        "maize": false,
        "rice": false,
        "soybean": false,
        "sugarcane": false,
        "wheat": false
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

    showWarning: false,
    setShowWarning: (showWarning) => set({ showWarning }),

    showOverlays: false,
    setShowOverlays: (showOverlays) => set({ showOverlays }),

}))

export default useStore