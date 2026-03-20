import { useCallback, useEffect } from 'react'
import { useRouter } from 'next/router'
import { usePathname } from 'next/navigation'
import { useMapbox } from '@carbonplan/maps'

import useStore from '../store/index'

const Router = () => {
    const { map } = useMapbox()
    const router = useRouter()
    const pathname = usePathname()

    const zoom = useStore((state) => state.zoom)
    const setZoom = useStore((state) => state.setZoom)
    const center = useStore((state) => state.center)
    const setCenter = useStore((state) => state.setCenter)

    const getInitialZoom = useCallback((url) => {
        let initialZoom
        let tempZoom = url.searchParams.get("zoom")

        if (tempZoom != null && typeof parseFloat(tempZoom) == 'number' && parseFloat(tempZoom) > 0.0) {
            initialZoom = tempZoom
        } else {
            initialZoom = 1.3
        }

        url.searchParams.set('zoom', initialZoom)
        return initialZoom
    })

    const getInitialCenter = useCallback((url) => {
        let initialCenter

        // this makes sure that the center search param is in array format, so we don't need to check the type
        let tempCenter = url.searchParams.get("center")
        if(tempCenter == null) {
            url.searchParams.set('center', '-40,40')
            return [-40, 40]
        }

        tempCenter = tempCenter.split(',').map((d) => parseFloat(d))

        if (tempCenter.length == 2 && typeof tempCenter[0] == 'number' && !Number.isNaN(tempCenter[0]) && typeof tempCenter[1] == 'number' && !Number.isNaN(tempCenter[1])) {
            if(tempCenter[1] >= -90 && tempCenter[1] <= 90) {
                initialCenter = tempCenter.toString()
            } else {
                initialCenter = '-40,40'
            }
        } else {
            initialCenter = '-40,40'
        }

        url.searchParams.set('center', initialCenter)
        return initialCenter.split(',').map((d) => parseFloat(d))
    })

    useEffect(() => {
        const url = new URL(window.location)
        let savedZoom = getInitialZoom(url)
        let savedCenter = getInitialCenter(url)

        setZoom(savedZoom)
        setCenter(savedCenter)

        if (map && savedZoom && savedCenter) {
            map.easeTo({
                center: savedCenter,
                zoom: parseFloat(savedZoom),
                duration: 0,
            })
        }

        router.replace(`${pathname}?zoom=${url.searchParams.get('zoom')}&center=${url.searchParams.get('center')}`)
        // prevent back button
        // https://developer.mozilla.org/en-US/docs/Web/API/Window/popstate_event
        window.history.pushState(null, null, url);
        window.onpopstate = () => window.history.go(1)

    }, [window.onload]);

    useEffect(() => {
        map.on('moveend', () => {
            let zoom = map.getZoom().toFixed(2)
            let center = [parseFloat(map.getCenter().lng.toFixed(2)), parseFloat(map.getCenter().lat.toFixed(2))]
            setZoom(zoom)
            setCenter(center)
        })
    }, [])

    useEffect(() => {
        if (center && zoom) { 
            const url = new URL(window.location)
            url.searchParams.set('zoom', zoom)
            url.searchParams.set('center', center)
            router.replace(`${pathname}?zoom=${url.searchParams.get('zoom')}&center=${url.searchParams.get('center')}`)
        }

    }, [zoom, center])

    return null
}

export default Router