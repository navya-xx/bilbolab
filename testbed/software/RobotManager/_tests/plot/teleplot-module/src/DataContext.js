import React, { createContext, useEffect, useState } from "react";

export const DataContext = createContext();

export const DataProvider = ({ children }) => {
  const [dataBuffer, setDataBuffer] = useState([]);
  const [availableKeys, setAvailableKeys] = useState(new Set());

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8080");
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        const timestamp = Date.now() / 1000;
        const keys = Object.keys(msg);
        setAvailableKeys((prev) => {
          const newKeys = new Set(prev);
          keys.forEach((k) => newKeys.add(k));
          return newKeys;
        });
        setDataBuffer((prev) => [...prev, { timestamp, data: msg }]);
      } catch (e) {
        console.error("Error parsing message", e);
      }
    };
    return () => ws.close();
  }, []);

  return (
    <DataContext.Provider value={{ dataBuffer, availableKeys }}>
      {children}
    </DataContext.Provider>
  );
};
