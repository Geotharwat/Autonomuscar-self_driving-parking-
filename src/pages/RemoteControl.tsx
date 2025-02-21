import { useCallback, useEffect, useState } from "react";
import Button from "../components/Button";
import CarStatistics from "../components/CarStatistics";
import { connect } from "../app/sse";
import { useAppSelector } from "../app/hooks";
import { selectMode } from "../features/appSlice";
import { invokeAction, invokeActionSignaled } from "../app/api";
import Car from "../components/Car";
import { Joystick } from "react-joystick-component";
import { IJoystickUpdateEvent } from "react-joystick-component/build/lib/Joystick";

const maxSpeed = 80;

function RemoteControl() {
  const mode = useAppSelector(selectMode);
  useEffect(() => {
    return connect();
  }, []);
  const [x, setX] = useState(0);
  const [y, setY] = useState(0);
  const handleStick = useCallback((e: IJoystickUpdateEvent) => {
    let x = e.x || 0;
    let y = e.y || 0;
    const mag = Math.sqrt(x * x + y * y);
    if (mag > 0.1) {
      y = Math.sign(y) * mag * maxSpeed;
    } else y = 0;

    if (Math.abs(x) > 0.5) {
      x = Math.sign(x);
    } else x = 0;
    setX(x);
    setY(Math.round(y));
  }, []);

  useEffect(() => {
    const ctrl = new AbortController();
    const timeout = setTimeout(() => {
      invokeActionSignaled(ctrl.signal, "control", x, y).catch(() => {});
    }, 33);
    return () => {
      clearTimeout(timeout);
      ctrl.abort();
    };
  }, [x, y]);
  return (
    <div
      className="col align-items-center p2"
      style={{
        height: "100vh",
        boxSizing: "border-box",
        paddingBottom: "54px",
      }}
    >
      <img
        width="100%"
        src="/icon.png"
        style={{
          flex: 1,
        }}
      />
      <div
        className="flex-1"
        style={{
          flex: 1,
        }}
      />
      <Joystick
        size={window.innerWidth * 0.6}
        stickSize={window.innerWidth * 0.2}
        baseColor="var(--white)"
        stickColor="var(--primary)"
        move={handleStick}
        stop={handleStick}
      />
    </div>
  );
}

export default RemoteControl;
