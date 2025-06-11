import './App.css';
import { useState, useEffect } from 'react'
import { useDebouncedCallback } from 'use-debounce';
import { Sidebar, SidebarButton } from './components/Sidebar'
import { fetchResults } from './lib/Autocomplete';
import { ProviderItem, SuggestionList } from './components/SuggestionList';
import { SearchError } from './components/SearchError';
import { ItemDetails } from './components/ItemDetails';
import { getPosition, GeoCoordinates } from './lib/Geolocate';
import { TimingStats } from './components/Timing';
import { isLatLong } from './lib/Utility';

export function App() {

  const [searchInput, setSearchInput] = useState("");
  const [results, setResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [dbTime, setDbTime] = useState<number>(-1);
  const [details, setDetails] = useState<ProviderItem>();
  const [useGeo, setUseGeo] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [sidebarExpanded, setSidebarExpanded] = useState<boolean>(false)

  const [geoCoords, setGeoCoords] = useState<GeoCoordinates>()

  useEffect(()=>setSidebarExpanded(false), [])

  const debouncedFetchResults = useDebouncedCallback(fetchResults, 500, {leading: true})

  useEffect(()=>{
    if ( searchInput.length >= 3 || ( useGeo && isLatLong(geoCoords as GeoCoordinates)) ) {
      debouncedFetchResults(
        searchInput, 
        showDetails,
        (r) => { 
          setSearchError(r.error || "");
          setResults(r.results);
          setDbTime(r.databaseTime);
        },
        geoCoords
      )
    } else {
      debouncedFetchResults.cancel()
      setResults([])
    }
  }, [searchInput, useGeo, geoCoords])

  return (
    <div className={"container"}>
      <ItemDetails
        data={details as ProviderItem}
        visible={showResults}
        onClose={() => setShowResults(false)}
        className="itemDetails"
      />
    <div className={"main"}>
      <SidebarButton
        onClick={() => setSidebarExpanded(!sidebarExpanded)}
        expanded={sidebarExpanded}/>
      <TimingStats 
        value={dbTime}
        className="timeStats"
      />
      <div className={"mainContent"}>
      <h1>Find my provider</h1>
      <input 
        value={searchInput}
        className={"providerSearch"}
        onChange={(e) => setSearchInput(e.target.value)}
      />
      <SearchError 
        className="searchError"
        message={searchError}
      />
      <div style={{fontSize: 10, gap:0}}>
        <SuggestionList
          lineItems={results}
          geoCoords={geoCoords}
          itemClassNames={["listSlice", "listSliceAlt"]}
          clickCallback={(i: ProviderItem) => {
            setDetails(i)
            setShowResults(true)
          }}
        />
      </div>
    </div>
    </div>

    {/* Options Panel */}
    <Sidebar
      expanded={sidebarExpanded}
      className="sidebarContainer" 
      width={300}
    >
      <div
       className="sidebarContent"
      >
        <h3>Options</h3>
        <div className="optionsContainer">
        <div className="optionsItem">
          <p>Detailed search stats (slow!) :</p>
          <div className="optionsControl">

          <input 
          type="checkbox"
          checked={showDetails}
          onChange={(e) => (
            setShowDetails(e.target.checked)
          )}
          />
          </div>
        </div>
        <div className="optionsItem">
        <p>Use Geolocation:</p>
        <div  className="optionsControl">
        <input 
          type="checkbox"
          checked={useGeo}
          onChange={(e) => (
            setUseGeo(e.target.checked)
          )}
        />
        </div>
        </div>
        <div className="optionsItem">
        <p>Latitude:</p>
        <div className="optionsControl">
        <input 
        className={"latLon"}
        value={geoCoords?.lat || ""}
        onChange={(e: any)=>{
          setGeoCoords({"lat": e.target.value, "long": geoCoords?.long || 0})
        }}
        />
        </div>
        </div>
        <div className="optionsItem">
        <p>Longitude:</p>
        <div className="optionsControl">
        <input 
        className={"latLon"}
        value={geoCoords?.long || ""}
        onChange={(e: any)=>{
          setGeoCoords({"lat": geoCoords?.lat || 0, "long": e.target.value})
        }}
        />
        </div>
        </div>
        <div className="optionsItem">
          <div className="optionsControl">
        <button
          onClick={() => getPosition((pos) => setGeoCoords(pos))}
        >Update Geolocation</button>
        </div>
        </div>
        </div>
      </div>
    </Sidebar>
    </div>
  );
}
