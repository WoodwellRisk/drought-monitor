import { create } from 'zustand'

const MIN_DATE = '1991-01-01'
const MAX_DATE = '2026-02-01'
const MONTH_VALUES = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];

const getYear = (date) => {
    return `${ new Date(date + 'T00:00:00').getFullYear() }`
}

const getMonth = (date) => {
    const [year, month, day] = date.split('-')
    return month
}

const getMonthIdx = (month, months) => {
    return months.indexOf(month)
}

const getTime = (year, month) => {
    return `${year}-${month}-01`
}

const createDates = () => {
    const startYear = getYear(MIN_DATE)
    const endYear = getYear(MAX_DATE)
    const month = getMonth(MAX_DATE)
    const months = MONTH_VALUES

    return {
        minDate: MIN_DATE,
        maxDate: MAX_DATE,
        minYear: startYear,
        year: endYear,
        maxYear: endYear,
        month: month,
        monthValues: months,
        monthIdx: getMonthIdx(month, months),
        time: getTime(endYear, month),
    }
};

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

    // handle dates
    ...createDates(),
    setYear: (year) => set({ year }),
    setMonth: (month) => set({ month }),
    setMonthIdx: (monthIdx) => set({ monthIdx }),
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

    showAbout: false,
    setShowAbout: (showAbout) => set({ showAbout }),

    showAboutMobile: false,
    setShowAboutMobile: (showAboutMobile) => set({ showAboutMobile }),

    showMenu: false,
    setShowMenu: (showMenu) => set({ showMenu }),

    showOverlays: false,
    setShowOverlays: (showOverlays) => set({ showOverlays }),

}))

export default useStore
