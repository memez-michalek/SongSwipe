import logo from './logo.svg';

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./Authentication";
import MainPage from "./MainPage";

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/mainpage" element={<MainPage />} />
        </Routes>
      </div>
    </Router>
  );
}
export default App;
