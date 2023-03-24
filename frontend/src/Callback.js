import {React, useEffect, useState} from "react"
import axios from "axios"

function Callback(){
    const [data, setData] = useState('');


    useEffect(()=>{
        const searchParams = new URLSearchParams(window.location.search);
        const code = searchParams.get('code');
        console.log(code)


        const fetchData = async (code) => {
            const response = await axios.get(`http://localhost:8000/accounts/spotify/login/callback/?code=${code}`);
            console.log(response)
            const json = response.json();
            console.log(json)
            setData(json);
          };
        fetchData(code);


    }, [])


    return(
        <div>
            <h1>access code</h1>
            <p>{data}</p>

        </div>

    )

}

export default Callback
