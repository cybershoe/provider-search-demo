export type GeoCoordinates = {
  lat: number
  long: number
}

export const getPosition = (callback: (pos: GeoCoordinates) => void) => {
  if (navigator.geolocation) {
    navigator.permissions
      .query({ name: "geolocation" })
      .then(function (result) {
        if (["granted", "prompt"].includes(result.state)) {
          navigator.geolocation.getCurrentPosition(
            (e) => callback({ lat: e.coords.latitude, long: e.coords.longitude }),
            (e) => console.warn(`ERROR(${e.code}): ${e.message}`),
            {
              enableHighAccuracy: true,
              timeout: 5000
            });
        } else if (result.state === "denied") {
          console.warn("Geolocation permission denied")
        }
      });
  } else {
    console.warn("Geolocation failed");
  }
}