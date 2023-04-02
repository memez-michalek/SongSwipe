import React from 'react';
import './App.css'; // import custom CSS file for styling

const LoginPage = () => {
  const handleSpotifyLogin = () => {

    const authorizeUrl = "http://localhost:8000/accounts/spotify/login"
    window.location = authorizeUrl

  };
  return (
    <div className="LoginPage" style={{background: 'linear-gradient(to right, #FFC371, #FF5F6D)',}}>
    <div className="login-container">
      <div className="login-form-container">
        <h1 className="login-header">Sign In with Spotify</h1>
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
    </div>
  );
};

export default LoginPage;
