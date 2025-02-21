import { useEffect, useState } from "react";
import CarSvg from "./CarSvg";
import { useSpring, animated } from "@react-spring/web";
import Parking from "./Parking";
import { SVGProps } from "react";
import { useAppDispatch, useAppSelector } from "../app/hooks";
import { selectParkingSlot, selectTicks } from "../features/appSlice";
import Text from "./Text";
import Button from "./Button";
import { invokeAction } from "../app/api";
import FlagIcon from "./FlagIcon";

function Car() {
  const parkingSlot = useAppSelector(selectParkingSlot);
  const ticks = useAppSelector(selectTicks);
  const [isFeedOpen, setIsFeedOpen] = useState(true);
  const distanceToSlot = parkingSlot
    ? ((ticks - (parkingSlot.start.x + parkingSlot.end.x) / 2) *
        2.25 *
        2 *
        Math.PI) /
      10
    : -1;
  const isParking = Boolean(parkingSlot);
  // const [isParking, setIsParking] = useState(Boolean(parkingSlot));
  const carAnimations = useSpring({
    from: {
      y: 0,
    },
    to: {
      y: isParking ? -150 : isFeedOpen ? 100 : 0,
    },
  });
  const parkingAnimations = useSpring({
    from: {
      scale: isParking ? 2 : 1,
      opacity: isParking ? 0 : 1,
      flex: isParking ? 0 : 2,
      y: isParking ? 0 : 100,
      x: isParking ? 0 : 20,
    },
    to: {
      scale: !isParking ? 2 : 1,
      opacity: !isParking ? 0 : 1,
      flex: !isParking ? 0 : 2,
      y: !isParking ? 0 : 100,
      x: !isParking ? 0 : 20,
    },
  });

  const feedAnimations = useSpring({
    from: {
      opacity: 0,
      scale: 0,
      x: "-50%",
      y: "-100%",
    },
    to: {
      scale: isFeedOpen ? 1 : 0,
      opacity: isFeedOpen ? 1 : 0,
      width: isParking && isFeedOpen ? "200%" : isFeedOpen ? "110%" : "100%",
      x: isFeedOpen && isParking ? "40%" : isFeedOpen ? "-50%" : "0%",
      y: isFeedOpen && isParking ? "25%" : isFeedOpen ? "-100%" : "0%",
    },
  });

  return (
    <div
      className="row align-items-center justify-content-center flex-1"
      style={{
        padding: "0 56px",
      }}
    >
      <animated.div
        style={{
          position: "relative",
          flex: 1,
          ...carAnimations,
        }}
      >
        <CarSvg
          width="100%"
          height="100%"
          style={{
            maxHeight: "50vh",
          }}
          // onClick={() => setIsParking((p) => !p)}
        />
        <animated.div
          style={{
            position: "absolute",
            top: 0,
            left: "50%",
            transformOrigin: "50% 100%",
            ...feedAnimations,
          }}
          onClick={() => setIsFeedOpen((p) => !p)}
        >
          <div
            className="col s1 p1"
            style={{
              borderRadius: "12px",
              background: "var(--black)",
              overflow: "hidden",
              boxShadow: "0px 4px 12px 2px rgba(0, 0, 0, 0.25)",
            }}
          >
            <Text
              color="primary"
              textAlign="center"
              style={{ whiteSpace: "nowrap" }}
            >
              Rear Camera
            </Text>
            <img
              width="100%"
              src={isFeedOpen ? "/api/live" : undefined}
              style={{ borderRadius: "12px" }}
            />
          </div>
        </animated.div>

        <Button
          color="primary"
          size="small"
          style={{
            position: "absolute",
            top: 0,
            left: "50%",
            transform: "translate(-50%, -50%)",
            transformOrigin: "50% 100%",
          }}
          onClick={() => setIsFeedOpen((p) => !p)}
          label={
            <svg
              width="1em"
              height="1em"
              fill="none"
              viewBox="0 0 16 16"
              xmlns="http://www.w3.org/2000/svg"
            >
              <g clipPath="url(#a)" fill="#EEE">
                <path d="M8 .16a7.84 7.84 0 1 0 0 15.68A7.84 7.84 0 0 0 8 .16Zm0 13.778A5.938 5.938 0 1 1 8 2.063a5.938 5.938 0 0 1 0 11.875Z" />
                <path d="M8 2.94a5.06 5.06 0 1 0 0 10.12A5.06 5.06 0 0 0 8 2.94Zm0 3.374c-1.469 0-2.658-.596-2.658-1.33 0-.734 1.19-1.33 2.658-1.33 1.469 0 2.658.596 2.658 1.33 0 .734-1.19 1.33-2.658 1.33Z" />
              </g>
              <defs>
                <clipPath id="a">
                  <rect width={16} height={16} rx={7} fill="#fff" />
                </clipPath>
              </defs>
            </svg>
          }
        >
          Rear cam
        </Button>
      </animated.div>
      <animated.div
        style={{
          transformOrigin: "0px 50%",
          ...parkingAnimations,
        }}
      >
        <Text
          style={{
            position: "absolute",
            left: "50%",
            top: "32.5%",
            transform: "translate(-50%, -50%)",
          }}
          color="primary"
          fontSize="md"
          fontWeight="bold"
        >
          {Math.round(parkingSlot?.depth || 0)}cm
        </Text>
        <Text
          color="primary"
          fontSize="md"
          fontWeight="bold"
          className="col align-items-center"
          style={{
            position: "absolute",
            left: "0",
            top: "55%",
            transform: "translate(-100%, -50%)",
          }}
        >
          <FlagIcon />
          <span>{Math.round(distanceToSlot)}cm</span>
        </Text>
        <Text
          style={{
            position: "absolute",
            left: "calc(100% + 10px)",
            top: "55%",
            transform: "translate(-50%, -50%) rotate(90deg)",
          }}
          color="primary"
          fontSize="md"
          fontWeight="bold"
        >
          {Math.round(parkingSlot?.width || 0)}cm
        </Text>
        <Button
          label="P"
          size="small"
          style={{
            position: "absolute",
            top: "55%",
            left: "55%",
            transform: "translate(-50%, -50%)",
          }}
          onClick={() => {
            invokeAction("park");
          }}
        >
          Tap to park
        </Button>
        <Parking width="100%" height="100%" />
      </animated.div>
    </div>
  );
}

export default Car;
