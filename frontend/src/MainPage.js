
import axios from 'axios';
import React, { useState, useEffect, useRef } from 'react'
import Header from './components/Header';
import Card from './components/Card';
import SwipeButtons from './components/SwipeButtons';

function MainPage () {
  const [data, setData] = useState(null);
    const [images, setImages] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
          try {
            const response = await axios.get('http://localhost:8000/api/song',{
                withCredentials : true
            });
            setData(response.data);
            setImages(response.data.images.map(image => JSON.parse(image.replace(/'/g, '"'))));
            console.log(images)
          } catch (error) {
            console.error(error);
          }
        };
        fetchData();
      }, []);

    if (!data) {
        return <div>Loading...</div>;
    }




  return(
    <div>
    <Header />
    <Card data={data} images={images}/>
    <SwipeButtons />
    </div>
  )
}

export default MainPage

/*
import {React, useEffect, useState} from "react"
import axios from "axios"
import './App.css';

function MainPage(){
    const [data, setData] = useState(null);
    const [images, setImages] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
          try {
            const response = await axios.get('http://localhost:8000/api/song',{
                withCredentials : true
            });
            setData(response.data);
            setImages(response.data.images.map(image => JSON.parse(image.replace(/'/g, '"'))));
            console.log(images)
          } catch (error) {
            console.error(error);
          }
        };
        fetchData();
      }, []);

    if (!data) {
        return <div>Loading...</div>;
    }

    return (
        <div className="App">
          <div className="player-container">
            <div className="image-container">
              <img className="album-art" src={images[0].url} alt="Album Art" />
              <div className="player-overlay">
                <i className="fa fa-play"></i>
              </div>
              <audio className="audio-player" src={data.preview_url} controls autoPlay></audio>
            </div>
            <div className="track-info">
              <h1 className="track-name">{data.track_name}</h1>
              <h2 className="artist-name">by {data.artist_name}</h2>
              <h3 className="genres-heading">Genres:</h3>
              <ul className="genres-list">
                {data.genres.map(genre => (
                  <li className="genre-item" key={genre}>{genre}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      );

}

export default MainPage
*/
