




import React, { useState, useEffect, useRef } from "react";
import TinderCard from "react-tinder-card";
import "./TinderCard.css";
import SpotifyPlayer from 'react-spotify-player';

function Card(props) {
  const track_uri = `spotify:track:${props.data.track_id}`

    // Trigger the "play" method on the Spotify iframe's audio element


  {console.log(props)}
  {console.log(props.data.images[0].url)}
  return (
    <div>
      <div className="card__container">



          <TinderCard
            className="swipe"
          preventSwipe={["up", "down"]}
          onSwipe={(direction) => props.handleSwipe(direction)}
          /*onCardLeftScreen={(direction) => props.handleSwipe(direction)}*/


          >
            <div
              style={{
                backgroundImage: props.data.images ? `url(${props.data.images[0].url})` : "",
              }}
              className="card"

            >

            <iframe
            title="Spotify"
            className="SpotifyPlayer"
            src={`https://embed.spotify.com/?uri=${track_uri}&view=coverart&theme=black`}
            width="300px"
            height="80px"
            frameBorder="0"
            allowtransparency="true"
          />
            </div>
          </TinderCard>

      </div>
    </div>
  );
}

export default Card;
