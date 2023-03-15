

import queryString from "query-string";


function SpotifyAuth() {
    const authenticate = () => {
        const queries = {
          response_type: "code",
          client_id: "95ad54fe6e434ff8a74ac21ef37bef51",
          scope: "user-read-email",
          redirect_uri: "http://localhost:8000/api/spotify/"
        };
        window.location.assign(
          `https://accounts.spotify.com/authorize?${queryString.stringify(queries)}`
        );
      };



    return (
      <div className="App">
        <button
        className="border-indigo-500/100 border-2 p-2 rounded"
        onClick={authenticate}
        >
          Login via spotify
        </button>
      </div>
    );
}
export default SpotifyAuth
