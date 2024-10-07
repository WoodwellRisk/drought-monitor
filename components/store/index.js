import { create } from 'zustand'

const useStore = create((set) => ({
    // map container state
    zoom: 1,
    setZoom: (zoom) => set({ zoom }),

    maxZoom: 8,

    center: [-40, 40],
    setCenter: (center) => set({ center }),

    // https://github.com/mapbox/mapbox-gl-js/blob/2b6915c8004a5b759338f3a7d92fb2882db9dd5c/src/geo/lng_lat.js#L192-L201
    // https://docs.mapbox.com/mapbox-gl-js/example/restrict-bounds/
    bounds: [
        [-360, -60.5], // southwest
        [360, 85] // northeast
    ],

    // general / raster state variables
    variable: 'drought',
    setVariable: (variable) => set({ variable }),

    opacity: 1,
    setOpacity: (opacity) => set({ opacity }),

    minDate: '2001-01-01',
    maxDate: '2024-06-18',

    year: '2001',
    setYear: (year) => set({ year }),

    monthDay: '01-01',
    setMonthDay: (monthDay) => set({ monthDay }),

    time: (year, monthDay) => set(`${year}-${monthDay}`),
    setTime: (time) => set({ time }),

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
    crops: ["cocoa", "coffee", "cotton", "maize", "sugar", "wheat"],
    cropValues: {
        "cocoa": false,
        "coffee": false,
        "cotton": false,
        "maize": false,
        "sugar": false,
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

    showAbout: false,
    setShowAbout: (showAbout) => set({ showAbout }),

    showMenu: false,
    setShowMenu: (showMenu) => set({ showMenu }),

    showOverlays: false,
    setShowOverlays: (showOverlays) => set({ showOverlays }),

}))

export default useStore