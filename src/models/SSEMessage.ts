import SDCMode from "./SDCMode";

export type SSESpeedMessage = ["speed", number];
export type SSEDistanceMessage = ["ticks", number];
export type SSEModeMessage = ["mode", SDCMode];
export type SSEParkingSlotMessage = [
  "parkingSlot",
  [[number, number], [number, number], number, number] | null
];

type SSEMessage =
  | SSESpeedMessage
  | SSEDistanceMessage
  | SSEModeMessage
  | SSEParkingSlotMessage;

export default SSEMessage;
