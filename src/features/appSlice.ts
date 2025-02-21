import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "../app/store";
import ParkingSlot from "../models/ParkingSlot";
import SDCMode from "../models/SDCMode";

export interface AppState {
  mode: SDCMode;
  parkingSlot: ParkingSlot | null;
  speed: number;
  ticks: number;
}

const initialState: AppState = {
  mode: "idle",
  parkingSlot: null,
  speed: 0,
  ticks: 0,
};

export const counterSlice = createSlice({
  name: "counter",
  initialState,
  reducers: {
    setParkingSlot(state, { payload }: PayloadAction<AppState["parkingSlot"]>) {
      state.parkingSlot = payload;
    },
    setMode(state, { payload }: PayloadAction<AppState["mode"]>) {
      state.mode = payload;
    },
    setTicks(state, { payload }: PayloadAction<AppState["ticks"]>) {
      state.ticks = payload;
    },
    setSpeed(state, { payload }: PayloadAction<AppState["speed"]>) {
      state.speed = payload;
    },
  },
});

export const {
  setMode,
  setParkingSlot,
  setTicks,
  setSpeed,
} = counterSlice.actions;

export const selectMode = (state: RootState) => state.app.mode;
export const selectParkingSlot = (state: RootState) => state.app.parkingSlot;
export const selectDistance = (state: RootState) =>
  Math.round((state.app.ticks * 2.25 * 2 * Math.PI) / 10);
export const selectSpeed = (state: RootState) => state.app.speed;
export const selectTicks = (state: RootState) => state.app.ticks;

export default counterSlice.reducer;
