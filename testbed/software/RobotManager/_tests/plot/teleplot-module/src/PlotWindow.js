import React, { useContext, useEffect, useRef, useState } from "react";
import uPlot from "uplot";
import "uplot/dist/uPlot.min.css";
import { DataContext } from "./DataContext";

// Helper: convert a slider value [0,100] to a logarithmic time window (10s to 300s)
export const sliderToSeconds = (value) => {
  const min = Math.log(10);
  const max = Math.log(300);
  return Math.exp(min + (max - min) * (value / 100));
};

const PlotWindow = ({ id, onClose, initialSignals = [] }) => {
  const { dataBuffer, availableKeys } = useContext(DataContext);
  const containerRef = useRef(null);
  const plotRef = useRef(null);
  const uplotRef = useRef(null);
  const [signals, setSignals] = useState(initialSignals); // array of { key, color }
  const [sliderValue, setSliderValue] = useState(50); // slider value (0-100)

  const topBarHeight = 30;

  // Initialize uPlot
  const initPlot = () => {
    const series = [
      { label: "Time" },
      ...signals.map(({ key, color }) => ({
        label: key,
        stroke: color || "black"
      }))
    ];

    const opts = {
      title:
        signals.length > 0
          ? signals.map((s) => s.key).join(", ")
          : "No signals selected",
      width: plotRef.current ? plotRef.current.clientWidth : 400,
      height: plotRef.current ? plotRef.current.clientHeight : 200,
      scales: { x: { time: true } },
      axes: [
        { stroke: "#444", grid: { stroke: "#ccc" } },
        { stroke: "#444", grid: { stroke: "#ccc" } }
      ],
      series
    };

    const data = [[], ...signals.map(() => [])];
    uplotRef.current = new uPlot(opts, data, plotRef.current);
  };

  // Reinitialize uPlot when signals or sliderValue changes
  useEffect(() => {
    if (uplotRef.current) {
      uplotRef.current.destroy();
      uplotRef.current = null;
    }
    initPlot();
  }, [signals, sliderValue]);

  // Update plot data when new data arrives
  useEffect(() => {
    if (!uplotRef.current) return;
    const timeWindow = sliderToSeconds(sliderValue);
    const now = Date.now() / 1000;
    const startTime = now - timeWindow;

    const filtered = dataBuffer.filter((pt) => pt.timestamp >= startTime);
    const xs = filtered.map((pt) => pt.timestamp);
    const seriesData = signals.map(({ key }) =>
      filtered.map((pt) => (pt.data[key] !== undefined ? pt.data[key] : null))
    );
    const newData = [xs, ...seriesData];
    uplotRef.current.setData(newData);
  }, [dataBuffer, signals, sliderValue]);

  // Use ResizeObserver to update uPlot on container resize
  useEffect(() => {
    if (!plotRef.current || !uplotRef.current) return;
    const ro = new ResizeObserver((entries) => {
      for (let entry of entries) {
        const { width, height } = entry.contentRect;
        uplotRef.current.setSize({ width, height });
      }
    });
    ro.observe(plotRef.current);
    return () => ro.disconnect();
  }, [plotRef.current, uplotRef.current]);

  // Toggle signal selection
  const handleToggleSignal = (key) => {
    setSignals((prev) => {
      if (prev.find((s) => s.key === key)) {
        return prev.filter((s) => s.key !== key);
      } else {
        const color = "#" + Math.floor(Math.random() * 16777215).toString(16);
        return [...prev, { key, color }];
      }
    });
  };

  return (
    <div
      ref={containerRef}
      style={{
        border: "1px solid #ccc",
        margin: 5,
        background: "#fff",
        display: "flex",
        flexDirection: "column",
        height: "100%",
        position: "relative",
        overflow: "hidden",
        boxSizing: "border-box"
      }}
    >
      {/* Top bar */}
      <div
        className="drag-handle"
        style={{
          display: "flex",
          alignItems: "center",
          background: "#f0f0f0",
          padding: "0 5px",
          height: topBarHeight,
          flexShrink: 0,
          cursor: "move",
          whiteSpace: "nowrap"
        }}
      >
        <div style={{ flexGrow: 1, fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis" }}>
          {signals.length > 0
            ? signals.map((s) => s.key).join(", ")
            : "No signals selected"}
        </div>
        <div style={{ position: "relative", margin: "0 5px" }}>
          <button
            className="no-drag"
            onClick={(e) => {
              const dropdown = e.currentTarget.nextSibling;
              dropdown.style.display =
                dropdown.style.display === "block" ? "none" : "block";
            }}
          >
            Signals ▾
          </button>
          <div
            className="no-drag"
            style={{
              display: "none",
              position: "absolute",
              top: "100%",
              right: 0,
              border: "1px solid #ccc",
              background: "#fff",
              zIndex: 1000,
              maxHeight: "200px",
              overflowY: "auto",
              minWidth: "100px"
            }}
          >
            {Array.from(availableKeys).map((key) => (
              <div key={key} style={{ padding: "2px 5px" }}>
                <label>
                  <input
                    type="checkbox"
                    className="no-drag"
                    checked={!!signals.find((s) => s.key === key)}
                    onChange={() => handleToggleSignal(key)}
                  />{" "}
                  {key}
                </label>
              </div>
            ))}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", marginRight: 5 }}>
          <input
            type="range"
            className="no-drag"
            min="0"
            max="100"
            value={sliderValue}
            onChange={(e) => setSliderValue(Number(e.target.value))}
          />
          <span className="no-drag" style={{ marginLeft: 5 }}>
            {Math.round(sliderToSeconds(sliderValue))}s
          </span>
        </div>
        {onClose && (
          <button className="no-drag close-button" onClick={onClose}>
            &times;
          </button>
        )}
      </div>
      {/* Plot container */}
      <div
        ref={plotRef}
        style={{
          width: "100%",
          height: `calc(100% - ${topBarHeight + 80}px)`,
          boxSizing: "border-box"
        }}
      />
    </div>
  );
};

export default PlotWindow;
