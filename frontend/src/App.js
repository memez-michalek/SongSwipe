import logo from './logo.svg';
import './App.css';

import queryString from "query-string";
import { BrowserRouter, Route } from "react-router-dom"
import SpotifyAuth from './Authentication';



function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Route path="/authentication" element={SpotifyAuth}></Route>
        <Route path="/callback" element={SpotifyAuth}></Route>
      </BrowserRouter>
    </div>
  );
}

export default App;
