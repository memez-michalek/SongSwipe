/*
import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Card from './components/Card';
import SwipeButtons from './components/SwipeButtons';

function MainPage () {
  const [data, setData] = useState(null);
  const [images, setImages] = useState([]);
  const baseUrl = 'http://localhost:8000/api';

  const handleLike = async () => {
    setData(null)
    try{
      const endpoint = `like_song/${data.track_id}/`;
      const queryParams = new URLSearchParams({
        spotify_artist_id: data.artist_seed,
        genres: data.genres,
      });
      const url = `${baseUrl}/${endpoint}?${queryParams.toString()}`;
      console.log(url);
      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(response.message);
      }

      const responseData = await response.json();
      setData(responseData);
      setImages(responseData.images.map(image => JSON.parse(image.replace(/'/g, '"'))));
    } catch(err){
      console.error(err)
    }
  };

  const handleDislike = async () => {
    try{
      const endpoint = `hate_song/${data.track_id}/`;
      const queryParams = new URLSearchParams({
        spotify_artist_id: data.artist_seed,
        genres: data.genres,
      });
      const url = `${baseUrl}/${endpoint}?${queryParams.toString()}`;

      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(response.data.message);
      }

      const responseData = await response.json();
      setData(responseData);
      setImages(responseData.images.map(image => JSON.parse(image.replace(/'/g, '"'))));
    } catch(err){
      console.error(err)
    }
  };

  const handleSwipe = async (direction) => {
    console.log(direction)
    if (direction === "right") {
      handleLike();
    } else if (direction === "left") {
      handleDislike();
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${baseUrl}/song/`, {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        const responseData = await response.json();
        setData(responseData);
        setImages(responseData.images.map(image => JSON.parse(image.replace(/'/g, '"'))));
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
      <Card data={data} images={images} handleSwipe={handleSwipe}/>
      <SwipeButtons handleSwipe={handleSwipe} />
    </div>
  )
}

export default MainPage
*/

import React, { useState, useEffect } from 'react'
import Header from './components/Header';
import Card from './components/Card';
import SwipeButtons from './components/SwipeButtons';
import axios from "axios";

function MainPage () {
  const [data, setData] = useState(null);
  const [images, setImages] = useState([]);
  const baseUrl = 'http://localhost:8000/api';

  const handleLike = async () => {
      const endpoint = `like_song/${data.track_id}/`;
      const queryParams = new URLSearchParams({
        spotify_artist_id: data.artist_seed,
        genres: data.genres,
      });
      const url = `${baseUrl}/${endpoint}?${queryParams.toString()}`;
      console.log(url);
      const retry = async (fn, retriesLeft = 3, delay = 100) => {
        try {
          const response = await fn();
          return response;
        } catch (error) {
          if (retriesLeft) {
            await new Promise(resolve => setTimeout(resolve, delay));
            return retry(fn, retriesLeft - 1, delay * 2);
          } else {
            throw new Error(error.message);
          }
        }
      }

      // Call the retry function with the axios request
      const response = await retry(() => axios.get(url, {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json'
        }
      }));

      if (response.status !== 200) {
        throw new Error(response.message);
      }
      //const responseData =  response.json();
      setData(response.data);
      setImages(response.data.images.map(image => JSON.parse(image.replace(/'/g, '"'))));
  };

  const handleDislike = async () => {
      const endpoint = `hate_song/${data.track_id}/`;
      const queryParams = new URLSearchParams({
        spotify_artist_id: data.artist_seed,
        genres: data.genres,
      });
      const url = `${baseUrl}/${endpoint}?${queryParams.toString()}`;

      const response = await axios.get(url, {
        withCredentials: true,
        headers: {
          'Authorization': 'Bearer your_token_here',
          'Content-Type': 'application/json'
        }
      });
      console.log(response.data)
      console.log(response)
      if (response.status !== 200) {
        throw new Error(response.data.message);
      }
      //const responseData = response.json();
      setData(response.data);
      setImages(response.data.images.map(image => JSON.parse(image.replace(/'/g, '"'))));

  };

  const handleSwipe = (direction) => {
    console.log(direction)
    if (direction === "right") {
      handleLike();
    } else if (direction === "left") {
      handleDislike();
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/song/',{
            withCredentials : true,
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
      <Card data={data} images={images} handleSwipe={handleSwipe}/>
      <SwipeButtons handleSwipe={handleSwipe} />
    </div>
  )
}

export default MainPage




/*
import axios from 'axios';
import React, { useState, useEffect } from 'react'
import Header from './components/Header';
import Card from './components/Card';
import SwipeButtons from './components/SwipeButtons';

function MainPage () {
  const [data, setData] = useState(null);
  const [images, setImages] = useState([]);
  const baseUrl = 'http://localhost:8000/api';

  const handleLike = async () => {
    setData(null)
    try{
      const endpoint = `like_song/${data.track_id}/`;
      const queryParams = new URLSearchParams({
        spotify_artist_id: data.artist_seed,
        genres: data.genres,
      });
      const url = `${baseUrl}/${endpoint}?${queryParams.toString()}`;
      console.log(url);
      const response = await axios.get(
        url,{
          withCredentials : true
      })
      console.log(response);
      setData(response.data);
      setImages(response.data.images.map(image => JSON.parse(image.replace(/'/g, '"'))));
    }catch(err){
      console.error(err)
    }
  };

  const handleDislike = async () => {
    try{
      const endpoint = `hate_song/${data.track_id}/`;
      const queryParams = new URLSearchParams({
        spotify_artist_id: data.artist_seed,
        genres: data.genres,
      });
      const url = `${baseUrl}/${endpoint}?${queryParams.toString()}`;

      const response = await axios.get(
        url,{
          withCredentials : true
      })
      console.log
      setData(response.data);
      setImages(response.data.images.map(image => JSON.parse(image.replace(/'/g, '"'))));
    }catch(err){
      console.error(err)
    }
  };

  const handleSwipe = async (direction) => {
    console.log(direction)
    if (direction === "right") {
      handleLike();
    } else if (direction === "left") {
      handleDislike();
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/song/',{
            withCredentials : true,
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
      <Card data={data} images={images} handleSwipe={handleSwipe}/>
      <SwipeButtons handleSwipe={handleSwipe} />
    </div>
  )
}

export default MainPage



/*

import axios from 'axios';
import React, { useState, useEffect, useRef } from 'react'
import Header from './components/Header';
import Card from './components/Card';
import SwipeButtons from './components/SwipeButtons';

function MainPage () {
  const [data, setData] = useState(null);
  const [images, setImages] = useState([]);
  const baseUrl = 'http://localhost:8000/api';
    /*
    const handleLeft = async (song) => {

      try{

        const endpoint = `hate_song/${song.track_id}/`;
        const queryParams = new URLSearchParams({
           spotify_artist_id: song.artist_seed,
           genres: song.genres,
        });
        const url = `${baseUrl}/${endpoint}?${queryParams.toString()}`;

        const response = await axios.get(
          url,{
            withCredentials : true
        })

        setData(response.data);
        setImages(response.data.images.map(image => JSON.parse(image.replace(/'/g, '"'))));


      }catch(err){
        console.error(err)
      }





    };

    const handleRight =  async (song) => {

      try{
        const endpoint = `like_song/${song.track_id}/`;
        const queryParams = new URLSearchParams({
          spotify_artist_id: song.artist_seed,
          genres: song.genres,
        });
        const url = `${baseUrl}/${endpoint}?${queryParams.toString()}`;

        const response = await axios.get(
          url,{
            withCredentials : true
        })

        setData(response.data);
        setImages(response.data.images.map(image => JSON.parse(image.replace(/'/g, '"'))));


      }catch(err){
        console.error(err)
      }


    };


    const handleSwipe = async (direction) => {
      console.log(direction)
      if (direction === "right") {
        setData(null)
        try{
          const endpoint = `like_song/${data.track_id}/`;
          const queryParams = new URLSearchParams({
            spotify_artist_id: data.artist_seed,
            genres: data.genres,
          });
          const url = `${baseUrl}/${endpoint}?${queryParams.toString()}`;
          console.log(url);
          const response = await axios.get(
            url,{
              withCredentials : true
          })
          console.log(response);
          setData(response.data);
          setImages(response.data.images.map(image => JSON.parse(image.replace(/'/g, '"'))));


        }catch(err){
          console.error(err)
        }
      } else if (direction === "left") {
        try{
          const endpoint = `hate_song/${data.track_id}/`;
          const queryParams = new URLSearchParams({
            spotify_artist_id: data.artist_seed,
            genres: data.genres,
          });
          const url = `${baseUrl}/${endpoint}?${queryParams.toString()}`;

          const response = await axios.get(
            url,{
              withCredentials : true
          })

          setData(response.data);
          setImages(response.data.images.map(image => JSON.parse(image.replace(/'/g, '"'))));


        }catch(err){
          console.error(err)
        }



      }
    };




    useEffect(() => {
        const fetchData = async () => {
          try {
            const response = await axios.get('http://localhost:8000/api/song/',{
                withCredentials : true,

            });
            setData(response.data);
            setImages(response.data.images.map(image => JSON.parse(image.replace(/'/g, '"'))));
            console.log(images)
          } catch (error) {
            console.error(error);
          }
        };
        fetchData();
      }, [data, images]);

    if (!data) {
        return <div>Loading...</div>;
    }




  return(
    <div>
    <Header />
    <Card data={data} images={images} handleSwipe={handleSwipe}/>
    <SwipeButtons handleSwipe={handleSwipe} />
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
