
import React, { useState, useEffect, useCallback, useMemo } from 'react'
import Header from './components/Header';
import Card from './components/Card';
import SwipeButtons from './components/SwipeButtons';
import axios from "axios";
import Cookies from 'js-cookie';

function MainPage () {
  const [data, setData] = useState(null);
  const baseUrl = 'http://localhost:8000/api';
  const sessionid = Cookies.get('sessionid');


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
          if (error.response && error.response.status === 403) {
            window.location = "/"
          }

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
    };

  const handleDislike = async () => {
      const endpoint = `hate_song/${data.track_id}/`;
      const queryParams = new URLSearchParams({
        spotify_artist_id: data.artist_seed,
        genres: data.genres,
      });
      const url = `${baseUrl}/${endpoint}?${queryParams.toString()}`;

      const retry = async (fn, retriesLeft = 3, delay = 100) => {
        try {
          const response = await fn();
          return response;
        } catch (error) {
          if (error.response && error.response.status === 403) {
            window.location = "/"
          }

          if (retriesLeft) {
            await new Promise(resolve => setTimeout(resolve, delay));
            return retry(fn, retriesLeft - 1, delay * 2);
          } else {
            throw new Error(error.message);
          }
        }
      }

      const response = await retry(() => axios.get(url, {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json'
        }
      }));


      console.log(response.data)
      console.log(response)
      if (response.status !== 200) {
        throw new Error(response.data.message);
      }
      //const responseData = response.json();
      setData(response.data);

  };

  const handleSwipe = useCallback((direction) => {
    console.log(direction)
    if (direction === "right") {
      handleLike();
    } else if (direction === "left") {
      handleDislike();
    }
  }, [handleLike, handleDislike]);


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
      } catch (error) {
        console.error(error);
      }
    };
    fetchData();
  }, []);





  useEffect(() => {
    const endpoint = "song/"
    const url = `${baseUrl}/${endpoint}`
    const fetchData = async () => {
      try {
        const retry = async (fn, retriesLeft = 3, delay = 100) => {
          try {
            const response = await fn();
            return response;
          } catch (error) {
            if (error.response && error.response.status === 403) {
              window.location = "/"
            }

            if (retriesLeft) {
              await new Promise(resolve => setTimeout(resolve, delay));
              return retry(fn, retriesLeft - 1, delay * 2);
            } else {
              throw new Error(error.message);
            }
          }
        }

        const response = await retry(() => axios.get(url, {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json'
          }
        }));
        setData(response.data);

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
      <Card data={data} handleSwipe={handleSwipe}/>
      <SwipeButtons handleSwipe={handleSwipe} />
    </div>
  )
}

export default MainPage

/*

import React, { useState, useEffect, useCallback } from 'react'
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

  const handleSwipe = useCallback((direction) => {
    console.log(direction)
    if (direction === "right") {
      handleLike();
    } else if (direction === "left") {
      handleDislike();
    }
  }, [handleLike, handleDislike]);

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
*/
