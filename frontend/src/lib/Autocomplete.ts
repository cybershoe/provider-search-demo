import { GeoCoordinates } from './Geolocate';
import { isLatLong } from './Utility';

export type AutocompleteResponse = {
  results: []
  databaseTime: number
  error?: string
}

export const fetchResults = async (
  query: string,
  showDetails: boolean,
  callback: (r: AutocompleteResponse) => void,
  geoCoords?: GeoCoordinates,
) => {
  let requestURL = `http://127.0.0.1:8000/search?q=${encodeURI(query)}`
  if (showDetails) requestURL += "&details=y"

  if (geoCoords && isLatLong(geoCoords)) requestURL += `&lat=${geoCoords?.lat}&lon=${geoCoords?.long}`

  fetch(requestURL)
    .then(response => response.json())
    .then(data => {
      const res = JSON.parse(data)
      callback(res)
    })
    .catch(e => {
      console.log(e)
      callback({ results: [], databaseTime: -1, error: e.message })
    })
}