import * as React from "react"
import { SVGProps } from "react"

const FlagIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg
    width="1em"
    height="1em"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    <g clipPath="url(#a)">
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M4.625 14.634c9.22.66 8.74-4.19 19.375-6.508C16.453 2.134 10.571 6.21 4.625 1.414v-.248C4.625.522 4.06 0 3.364 0c-.697 0-1.262.522-1.262 1.166v20.89H.827c-.455 0-.827.344-.827.765V24h6.727v-1.18c0-.418-.371-.763-.826-.763H4.625v-7.423Z"
        fill="currentColor"
      />
    </g>
    <defs>
      <clipPath id="a">
        <path fill="#fff" d="M0 0h24v24H0z" />
      </clipPath>
    </defs>
  </svg>
)

export default FlagIcon
