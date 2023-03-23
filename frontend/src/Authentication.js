import React from 'react';
import './LoginPage.css'; // import custom CSS file for styling
import querystring from 'querystring';
import process from 'process';


const LoginPage = () => {
  const handleSpotifyLogin = () => {

    const scope = "user-read-email user-read-private user-library-read user-top-read user-library-modify playlist-modify-public playlist-modify-private"
    const queryParams = querystring.stringify({
        response_type: 'code',
        client_id: process.env.REACT_APP_SPOTIFY_CLIENT_ID,
        scope: scope,
        redirect_uri:  process.env.REACT_APP_SPOTIFY_REDIRECT_URL,
      })

    const authorizeUrl = `https://accounts.spotify.com/authorize?${queryParams}`;
    window.location = authorizeUrl


  };

  return (
    <div className="login-container">
      <div className="login-form-container">
        <h1 className="login-header">Sign In to Spotify</h1>
        <button className="spotify-button" onClick={handleSpotifyLogin}>
          <img
            className="spotify-icon"
            src="https://img.icons8.com/color/48/000000/spotify--v1.png"
            alt="Spotify Icon"
          />
          Connect with Spotify
        </button>
      </div>
    </div>
  );
};

export default LoginPage;
