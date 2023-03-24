import logo from './logo.svg';
import './App.css';

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./Authentication";
import Callback from "./Callback";

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/authentication" element={<LoginPage />} />
          <Route path="/callback" element={<Callback />} />
        </Routes>
      </div>
    </Router>
  );
}
export default App;
