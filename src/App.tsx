import { useEffect, useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import Text from "./components/Text";
import Button from "./components/Button";
import CarSvg from "./components/CarSvg";
import CarStatistics from "./components/CarStatistics";
import { useSpring, animated } from "@react-spring/web";
import Parking from "./components/Parking";
import { SVGProps } from "react";
import { connect } from "./app/sse";
import SSEMessage from "./models/SSEMessage";
import ParkingSlot from "./models/ParkingSlot";
import { useAppDispatch, useAppSelector } from "./app/hooks";
import { selectMode } from "./features/appSlice";
import { invokeAction } from "./app/api";
import Car from "./components/Car";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import RemoteControl from "./pages/RemoteControl";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route index element={<Home />} />
        <Route path="/control"  element={<RemoteControl />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
