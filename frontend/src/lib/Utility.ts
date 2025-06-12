import { GeoCoordinates } from "./Geolocate"

const isInRange = (i: any) => {
    return (Number.isFinite(i)
        && i <= 180
        && i >= -180
    )
}

export function isLatLong(e: GeoCoordinates): boolean {

    return (isInRange(e?.lat) && isInRange(e?.long))
} 