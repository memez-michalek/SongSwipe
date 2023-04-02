import React from 'react'
import { IconButton } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import './Header.css'
import { Link, useNavigate } from 'react-router-dom';

function Header() {



    return (
        <div className='header'>
            <link rel="preconnect" href="https://fonts.googleapis.com"/>
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
            <link href="https://fonts.googleapis.com/css2?family=Damion&display=swap" rel="stylesheet"/>


            <h1>SongSwipe</h1>

        </div>
    )
}

export default Header
