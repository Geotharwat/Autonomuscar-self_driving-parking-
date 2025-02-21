import {
  setMode,
  setParkingSlot,
  setSpeed,
  setTicks,
} from "../features/appSlice";
import ParkingSlot from "../models/ParkingSlot";
import SSEMessage from "../models/SSEMessage";
import { store } from "./store";

const { dispatch, getState } = store;

export function connect() {
  const sse = new EventSource("/api/events");
  sse.onmessage = (ev: MessageEvent<any>) => {
    const data = JSON.parse(ev.data);
    const [type, value]: SSEMessage = data;
    if (type === "mode") {
      dispatch(setMode(value));
    } else if (type === "speed") {
      dispatch(setSpeed(value));
    } else if (type === "ticks") {
      dispatch(setTicks(value));
    } else if (type === "parkingSlot" && !value) {
      dispatch(setParkingSlot(null));
    } else if (type === "parkingSlot" && value) {
      const [[startX, startDepth], [endX, endDepth], width, depth] = value;
      const slot: ParkingSlot = {
        depth,
        width,
        start: {
          x: startX,
          depth: startDepth,
        },
        end: {
          x: endX,
          depth: endDepth,
        },
      };
      dispatch(setParkingSlot(slot));
    } else {
      console.error("SSE: received unknown message", data);
    }
  };
  return () => sse.close();
}

export default connect;
