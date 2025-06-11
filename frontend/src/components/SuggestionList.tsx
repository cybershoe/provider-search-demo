import { GeoCoordinates } from "../lib/Geolocate";
import { isLatLong } from "../lib/Utility";
import { point, distance } from '@turf/turf';

export type ProviderItem = {
  name: {
    first: string;
    last: string;
    prefix: string;
  }
  location: any;
  providerType: string;
  score: number;
  scoreDetails: any;
  telephone: any;
  _id: any;
}

export interface SuggestionListProps {
    lineItems: Array<ProviderItem>
    geoCoords?: GeoCoordinates
    itemClassNames?: Array<string>
    clickCallback?: (item: ProviderItem) => void
}

export const SuggestionList = ({
    lineItems, 
    geoCoords = undefined, 
    itemClassNames = ["lineitem"],
    clickCallback = (item) => {}}: SuggestionListProps) => {

      const listItems = lineItems.map( (e: ProviderItem,i) => {
        let dist = null

        if (geoCoords && isLatLong(geoCoords)) { 
          const origin = point([geoCoords.long, geoCoords.lat])
          const dest = point(e.location.geoLocation.coordinates)

          dist = distance(origin, dest)
        } 

        const className = 
            itemClassNames[0] + 
            (i % itemClassNames.length ?
            ` ${itemClassNames[i % itemClassNames.length]}` : "")

        return (
        <div 
          key={`result${i}`} 
          className={className}
          onClick={()=>{
            clickCallback(e)
          }}
        >
          <p style={{marginTop: 0, fontSize: "small", fontWeight: "bold"}}>{e.name.first} {e.name.last}, {e.providerType}</p>
          <p style={{marginBottom: 0}}>{e.location.streetAddress}, {e.location.municipality}, {e.location.province}  {e.location.postalCode} { dist && `  ---  ${Math.round(dist)} km Away` }</p>
          <p style={{marginBottom: 5}}>Phone: {e.telephone.main}, Fax: {e.telephone.fax}</p>
          <p style={{paddingBottom: 8, fontWeight: "bold"}}>Score: {e.score }</p> 
          
        </div>)
      })

      return (
        <>
          {listItems}
        </>
      )
    }