import React from 'react'
import ReplayIcon from '@mui/icons-material/Replay';
import CloseIcon from '@mui/icons-material/Close';
import StarIcon from '@mui/icons-material/Star';
import FavoriteIcon from '@mui/icons-material/Favorite';
import FlashOnIcon from '@mui/icons-material/FlashOn';
import { IconButton } from '@mui/material';
import './SwipeButtons.css'

const SwipeButtons = ({ handleSwipe}) => {
    return (
      <div className="swipe__Button">
        <IconButton className="swipeButton__left" onClick={() => handleSwipe('left')}>
          <CloseIcon fontSize="large" />
        </IconButton>
        <IconButton className="swipeButton__right" onClick={() => handleSwipe('right')}>
          <FavoriteIcon fontSize="large" />
        </IconButton>
      </div>
    );
  };

export default SwipeButtons
