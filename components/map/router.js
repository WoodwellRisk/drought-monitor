import { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { usePathname } from 'next/navigation';

import { useMap } from './map-provider';
import { useStore } from '../store/index';

const Router = () => {
  const { map } = useMap();
  const router = useRouter();
  const pathname = usePathname();

  const [mapReady, setMapReady] = useState(false);
  const zoom = useStore((state) => state.zoom);
  const setZoom = useStore((state) => state.setZoom);
  const center = useStore((state) => state.center);
  const setCenter = useStore((state) => state.setCenter);

  const getInitialZoom = useCallback((url) => {
    let initialZoom;
    let tempZoom = url.searchParams.get('zoom');

    if (tempZoom != null && typeof parseFloat(tempZoom) == 'number' && parseFloat(tempZoom) > 0.0) {
      initialZoom = tempZoom;
    } else {
      initialZoom = 1.3;
    }

    url.searchParams.set('zoom', initialZoom);
    return initialZoom;
  });

  const getInitialCenter = useCallback((url) => {
    let initialCenter;

    // this makes sure that the center search param is in array format, so we don't need to check the type
    let tempCenter = url.searchParams.get('center');
    if (tempCenter == null) {
      url.searchParams.set('center', '-40,40');
      return [-40, 40];
    }

    tempCenter = tempCenter.split(',').map((d) => parseFloat(d));

    if (
      tempCenter.length == 2 &&
      typeof tempCenter[0] == 'number' &&
      !Number.isNaN(tempCenter[0]) &&
      typeof tempCenter[1] == 'number' &&
      !Number.isNaN(tempCenter[1])
    ) {
      if (tempCenter[1] >= -90 && tempCenter[1] <= 90) {
        initialCenter = tempCenter.toString();
      } else {
        initialCenter = '-40,40';
      }
    } else {
      initialCenter = '-40,40';
    }

    url.searchParams.set('center', initialCenter);
    return initialCenter.split(',').map((d) => parseFloat(d));
  });

  useEffect(() => {
    const handleLoad = () => {
      setMapReady(true);
    };

    // check if page is already fully loaded
    if (document.readyState === 'complete') {
      handleLoad();
    } else {
      // page is still loading, attach listener
      window.addEventListener('load', handleLoad);
      return () => window.removeEventListener('load', handleLoad);
    }
  }, []);

  useEffect(() => {
    if (!map) return;

    const url = new URL(window.location.href);
    let savedZoom = getInitialZoom(url);
    let savedCenter = getInitialCenter(url);

    setZoom(savedZoom);
    setCenter(savedCenter);

    map.easeTo({
      center: savedCenter,
      zoom: parseFloat(savedZoom),
      duration: 0,
    });

    router.replace(
      `${pathname}?zoom=${url.searchParams.get('zoom')}&center=${url.searchParams.get('center')}`
    );
    // prevent back button
    // https://developer.mozilla.org/en-US/docs/Web/API/Window/popstate_event
    window.history.pushState(null, null, url);
    window.onpopstate = () => window.history.go(1);
  }, [mapReady]);

  useEffect(() => {
    if (!map) return;

    const handleMoveEnd = () => {
      const newZoom = map.getZoom().toFixed(2);
      const newCenter = [
        parseFloat(map.getCenter().lng.toFixed(2)),
        parseFloat(map.getCenter().lat.toFixed(2)),
      ];

      setZoom(newZoom);
      setCenter(newCenter);

      if (router.isReady) {
        const url = new URL(window.location.href);
        url.searchParams.set('zoom', newZoom);
        url.searchParams.set('center', newCenter);
        router.replace(
          `${pathname}?zoom=${url.searchParams.get('zoom')}&center=${url.searchParams.get(
            'center'
          )}`
        );
      }
    };

    map.on('moveend', handleMoveEnd);

    return () => {
      map.off('moveend', handleMoveEnd);
    };
  }, [map, router.isReady, pathname]);

  return null;
};

export default Router;
