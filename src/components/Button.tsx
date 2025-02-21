import * as React from "react";
import classNames from "classnames";
import styles from "./Button.module.css";
import AppColor from "../models/AppColor";
import AppSize from "../models/AppSize";
import Text from "./Text";
export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  color?: AppColor;
  size?: AppSize;
  placement?: "top" | "bottom";
  label?: string | any;
}

function Button({
  children,
  color = "primary",
  size = "medium",
  placement = "bottom",
  className,
  label,
  ...props
}: ButtonProps) {
  return (
    <button
      className={classNames(
        "Button-root",
        styles.root,
        styles["size-" + size],
        `bg-${color}`,
        styles[`root-label-${placement}`],
        className
      )}
      {...props}
    >
      <div
        className={classNames(
          "Button-bg",
          `bg-${color}`,
          `fg-${color}`,
          styles.bg
        )}
      />
      <Text className={classNames("Button-icon", styles.icon)}>{label}</Text>
      <Text
        className={classNames(
          "Button-label",
          `fg-${color}`,
          styles.label,
          styles[`label-${placement}`]
        )}
      >
        {children}
      </Text>
    </button>
  );
}

export default Button;
