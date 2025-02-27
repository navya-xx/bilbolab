import React, { useState } from "react";
import GridLayout from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import PlotWindow from "./PlotWindow";
import { DataProvider } from "./DataContext";

const App = () => {
  // Start with two plots.
  const [layout, setLayout] = useState([
    { i: "plot1", x: 0, y: 0, w: 4, h: 8 },
    { i: "plot2", x: 4, y: 0, w: 4, h: 8 }
  ]);

  const addPlot = () => {
    const newId = `plot${layout.length + 1}`;
    const newLayoutItem = { i: newId, x: 0, y: Infinity, w: 4, h: 8 };
    setLayout([...layout, newLayoutItem]);
  };

  const removePlot = (id) => {
    setLayout(layout.filter((item) => item.i !== id));
  };

  return (
    <DataProvider>
      <div style={{ padding: 10, height: "100vh", fontFamily: '"Roboto", sans-serif' }}>
        {/* Place the add button in the upper left */}
        <div style={{ textAlign: "left", marginBottom: "10px" }}>
          <button onClick={addPlot} className="no-drag add-button">
            +
          </button>
        </div>
        <GridLayout
          className="layout"
          layout={layout}
          cols={12}
          rowHeight={30}
          width={1200}
          draggableHandle=".drag-handle"
          draggableCancel=".no-drag"
          onLayoutChange={(newLayout) => setLayout(newLayout)}
        >
          {layout.map((item) => (
            <div key={item.i} style={{ height: "100%" }}>
              <PlotWindow id={item.i} onClose={() => removePlot(item.i)} />
            </div>
          ))}
        </GridLayout>
      </div>
    </DataProvider>
  );
};

export default App;
