import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import { StatusGauge } from "./StatusGauge";

test("clamps the value into 0–100 and shows the label", () => {
  render(<StatusGauge value={142} label="pwr" />);

  // label is lower-case in the DOM; .ef-gauge__l upper-cases it in CSS only
  expect(screen.getByText("100")).toBeInTheDocument();
  expect(screen.getByText("pwr")).toBeInTheDocument();
});

test("drives the ring via the --ef-gauge-v custom property", () => {
  const { container } = render(<StatusGauge value={-5} label="disk" unit="%" />);
  const gauge = container.querySelector<HTMLElement>(".ef-gauge");

  expect(gauge?.style.getPropertyValue("--ef-gauge-v")).toBe("0");
  expect(screen.getByText("%")).toBeInTheDocument();
});
