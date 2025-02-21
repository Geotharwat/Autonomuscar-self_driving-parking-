import { useEffect} from "react";
import Button from "../components/Button";
import CarStatistics from "../components/CarStatistics";
import { connect } from "../app/sse";
import { useAppSelector } from "../app/hooks";
import {
  selectMode,
} from "../features/appSlice";
import { invokeAction } from "../app/api";
import Car from "../components/Car";

function Home() {
  const mode = useAppSelector(selectMode);
  useEffect(() => {
    return connect();
  }, []);
  return (
    <>
      <svg
        width="100vw"
        viewBox="0 0 360 142"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          zIndex: 0,
        }}
      >
        <path
          d="M360 141.5C314.833 121 174.4 88 0 106V-1H360V141.5Z"
          fill="url(#paint0_linear_2_533)"
        />
        <defs>
          <linearGradient
            id="paint0_linear_2_533"
            x1="180"
            y1="-1"
            x2="180"
            y2="141.5"
            gradientUnits="userSpaceOnUse"
          >
            <stop stop-color="#CCD8EF" />
            <stop offset="1" stop-color="#EEEEEE" />
          </linearGradient>
        </defs>
      </svg>
      <div className="App col">
        <CarStatistics />
        <Car />
        <div className="col align-items-center p4">
          <Button
            label={mode == "idle" ? "D" : "S"}
            size="large"
            color={mode == "idle" ? "primary" : "secondary"}
            onClick={() => {
              if (mode === "idle") {
                invokeAction("drive");
              } else {
                invokeAction("stop");
              }
            }}
          >
            {mode == "idle" ? "Drive" : "Stop"}
          </Button>
        </div>
      </div>
    </>
  );
}

export default Home;
