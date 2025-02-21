import classNames from "classnames";
import * as React from "react";
import AppColor from "../models/AppColor";
import AppFontSize from "../models/AppFontSize";
import AppFontWeight from "../models/AppFontWeight";

import styles from "./Text.module.css";

export interface TextProps extends React.AllHTMLAttributes<HTMLElement> {
  color?: AppColor;
  fontSize?: AppFontSize;
  fontWeight?: AppFontWeight;
  component?: string | React.FunctionComponent | React.FunctionComponent;
  className?: string;
  textAlign?: "start" | "center" | "end";
  children?: any;
}

function Text({
  children,
  component = "div",
  fontSize = "md",
  fontWeight = "medium",
  color,
  textAlign = "start",
  className,
  ...props
}: TextProps) {
  return React.createElement<{ className: string }>(
    component,
    {
      className: classNames(
        "Text-root",
        styles.root,
        styles["textAlign-" + textAlign],
        styles["weight-" + fontWeight],
        `fs-${fontSize}`,
        { [`fg-${color}`]: Boolean(color) },
        className
      ),
      ...props,
    },
    children
  );
}

export default Text;
