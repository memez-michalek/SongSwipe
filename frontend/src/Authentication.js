import React from 'react';
import './LoginPage.css'; // import custom CSS file for styling
import querystring from 'querystring';
import randomstring from 'randomstring';
import axios from 'axios';


const LoginPage = () => {
  const handleSpotifyLogin = () => {

    const authorizeUrl = "http://localhost:8000/accounts/spotify/login"
    window.location = authorizeUrl

    //const resp = axios.get(authorizeUrl)
    //console.log(resp)

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
