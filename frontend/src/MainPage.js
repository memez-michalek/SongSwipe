import {React, useEffect, useState} from "react"
import axios from "axios"
import Cookie from "js-cookie"

function MainPage(){
    const [data, setData] = useState('');
    const access_token = Cookie.get('sessionid')
    const message = Cookie.get('message')

    useEffect(()=>{
        //const code = searchParams.get('code');
        //console.log(code)


        const fetchData = async () => {
            const response = await axios.get(`http://localhost:8000/api/song/`,
            {
                withCredentials: true,
            }
            );
            console.log(response)
            const json = response.json();
            console.log(json)
            setData(json);
          };
        fetchData();


    }, [])

    return(

        <div>

            <h1>access code</h1>
            <p>{access_token}</p>
            <p>{data}</p>

        </div>

    )

}

export default MainPage
