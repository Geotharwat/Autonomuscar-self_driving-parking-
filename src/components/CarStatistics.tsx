import * as React from "react";
import { useAppSelector } from "../app/hooks";
import { selectDistance, selectSpeed } from "../features/appSlice";
import Text from "./Text";

function CarStatistics() {
  const distance = useAppSelector(selectDistance);
  const speed = useAppSelector(selectSpeed);
  return (
    <div className="row s1 p4 justify-content-between">
      <div className="col align-items-center">
        <div className="row align-items-end">
          <Text fontSize="lg" color="primary" fontWeight="bold">
            {speed > 100 ? Math.round(speed / 10) / 10 : Math.round(speed)}
          </Text>
          <Text fontSize="sm" color="black" fontWeight="bold">
            {speed > 100 ? "m/s" : "cm/s"}
          </Text>
        </div>
        <Text color="black" fontWeight="bold">
          Speed
        </Text>
      </div>
      <div className="col align-items-center">
        <div className="row align-items-end">
          <Text fontSize="lg" color="primary" fontWeight="bold">
            {distance > 100 ? Math.round(distance / 10) / 10 : distance}
          </Text>
          <Text fontSize="sm" color="black" fontWeight="bold">
            {distance > 100 ? "m" : "cm"}
          </Text>
        </div>
        <Text color="black" fontWeight="bold">
          Distance
        </Text>
      </div>
    </div>
  );
}

export default CarStatistics;
