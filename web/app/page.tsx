
"use client";

import { useState } from "react";
import Viewer from "./Viewer";

const layers = [
  { name: "Basemap (OHRC)", color: "#a7a9ad" },
  { name: "DEM (Elevation)", color: "#39b9c7" },
  { name: "Slope", color: "#e8a64b" },
  { name: "Surface Roughness", color: "#9ca3af" },
  { name: "DFSAR (CPR)", color: "#647de8" },
  { name: "DFSAR (DOP)", color: "#8b78c8" },
  { name: "Illumination", color: "#d8dce4" },
  { name: "Resource Potential", color: "#ec4899" },
  { name: "Prediction Uncertainty", color: "#a855f7" },
  { name: "Landing Sites", color: "#22c55e" },
  { name: "Rover Path", color: "#38bdf8" },
];

const previews = [
  { title: "OHRC · Optical", color: "#777d84" },
  { title: "DFSAR · CPR", color: "#374d9b" },
  { title: "DEM · Elevation", color: "#168b83" },
  { title: "Illumination", color: "#b0b0b0" },
  { title: "Resource Potential", color: "#9b347d" },
];

export default function Home() {
  const [enabled, setEnabled] = useState<Record<string, boolean>>({
    "DEM (Elevation)": true,
    "Resource Potential": false,
    "Landing Sites": true,
    "Rover Path": true,
  });
  const [opacity, setOpacity] = useState(70);
  const [showInfo, setShowInfo] = useState(true);

  const toggleLayer = (name: string) => {
    setEnabled((current) => ({
      ...current,
      [name]: !current[name],
    }));
  };

  const panel: React.CSSProperties = {
    background: "#0d1a28",
    border: "1px solid #24384b",
    borderRadius: 10,
    padding: 12,
    minWidth: 0,
  };

  const muted: React.CSSProperties = {
    color: "#94a8ba",
    fontSize: 12,
  };

  return (
    <main
      style={{
        height: "100vh",
        minHeight: 600,
        overflow: "hidden",
        boxSizing: "border-box",
        padding: 12,
        background: "#050b13",
        color: "#e7eef6",
        fontFamily: "Arial, sans-serif",
        display: "flex",
        flexDirection: "column",
        gap: 10,
      }}
    >
      <header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          flexShrink: 0,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 23,
              fontWeight: 800,
              letterSpacing: 3,
            }}
          >
            LUNAR<span style={{ color: "#48b5ff" }}>TWIN</span>
          </div>
          <div style={{ ...muted, marginTop: 4 }}>
            Lunar Digital Twin · Terrain Intelligence & Exploration
          </div>
        </div>
        <div style={{ ...panel, padding: "8px 12px", ...muted }}>
          SOUTH POLAR REGION · LOLA DEM
        </div>
      </header>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "230px minmax(0, 1fr) 250px",
          gap: 10,
          flex: 1,
          minHeight: 0,
        }}
      >
        {/* Left: data layers */}
        <aside style={{ ...panel, overflowY: "auto" }}>
          <h3 style={{ fontSize: 15, margin: "2px 0 12px" }}>
            Data Layers
          </h3>

          {layers.map((layer) => (
            <button
              key={layer.name}
              onClick={() => toggleLayer(layer.name)}
              aria-pressed={!!enabled[layer.name]}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                width: "100%",
                textAlign: "left",
                padding: "10px 4px",
                border: 0,
                borderBottom: "1px solid #1c2c3c",
                background: enabled[layer.name]
                  ? "#132b40"
                  : "transparent",
                color: "#dce6f0",
                cursor: "pointer",
                fontSize: 12,
              }}
            >
              <span
                style={{
                  width: 24,
                  height: 24,
                  borderRadius: 5,
                  flexShrink: 0,
                  background: layer.color,
                  border: "1px solid #506175",
                }}
              />
              <span style={{ flex: 1 }}>{layer.name}</span>
              <span
                style={{
                  width: 29,
                  height: 16,
                  borderRadius: 20,
                  background: enabled[layer.name] ? "#168ee0" : "#334252",
                  padding: 2,
                  boxSizing: "border-box",
                  flexShrink: 0,
                }}
              >
                <span
                  style={{
                    display: "block",
                    width: 12,
                    height: 12,
                    borderRadius: "50%",
                    background: "#f3f7fb",
                    marginLeft: enabled[layer.name] ? 13 : 0,
                  }}
                />
              </span>
            </button>
          ))}

          <p style={{ ...muted, lineHeight: 1.5, marginTop: 12 }}>
            Layer switches are interface controls for now. Additional
            scientific overlays must be connected to their datasets.
          </p>
        </aside>

        {/* Center: previews and existing 3D viewer */}
        <section
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 8,
            minWidth: 0,
            minHeight: 0,
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(5, minmax(0, 1fr))",
              gap: 7,
              flexShrink: 0,
            }}
          >
            {previews.map((preview, index) => (
              <button
                key={preview.title}
                onClick={() => {
                  const target = [
                    "Basemap (OHRC)",
                    "DFSAR (CPR)",
                    "DEM (Elevation)",
                    "Illumination",
                    "Resource Potential",
                  ][index];
                  toggleLayer(target);
                }}
                style={{
                  minWidth: 0,
                  height: 76,
                  padding: 8,
                  textAlign: "left",
                  color: "white",
                  cursor: "pointer",
                  border: "1px solid #31465b",
                  borderRadius: 7,
                  background: `linear-gradient(145deg, ${preview.color}, #07101d 85%)`,
                }}
              >
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    lineHeight: 1.3,
                  }}
                >
                  {preview.title}
                </span>
                <span
                  style={{
                    display: "block",
                    marginTop: 23,
                    fontSize: 10,
                    color: "#d1dce7",
                  }}
                >
                  Layer preview
                </span>
              </button>
            ))}
          </div>

          <div
            style={{
              flex: 1,
              minHeight: 0,
              position: "relative",
              overflow: "hidden",
              border: "1px solid #2b4053",
              borderRadius: 10,
              background: "#050812",
            }}
          >
            <div style={{ position: "absolute", inset: 0 }}>
              <Viewer />
            </div>

            <div
              style={{
                position: "absolute",
                right: 14,
                top: 12,
                zIndex: 5,
                pointerEvents: "none",
                color: "#eaf2fc",
                fontSize: 21,
                textShadow: "0 2px 5px black",
              }}
            >
              ↑
              <div style={{ fontSize: 10, textAlign: "center" }}>N</div>
            </div>

            <div
              style={{
                position: "absolute",
                left: 12,
                bottom: 12,
                zIndex: 5,
                padding: "9px 12px",
                border: "1px solid #33475b",
                borderRadius: 7,
                background: "rgba(5, 12, 22, .92)",
                fontSize: 11,
                pointerEvents: "none",
              }}
            >
              <strong>Terrain elevation</strong>
              <div
                style={{
                  width: 155,
                  height: 8,
                  margin: "8px 0 4px",
                  background:
                    "linear-gradient(90deg, #222a36, #777e86, #e0e3e6)",
                }}
              />
              <div style={{ ...muted, display: "flex", justifyContent: "space-between" }}>
                Low
                <span>High</span>
              </div>
            </div>
          </div>

          <div
            style={{
              ...panel,
              display: "flex",
              justifyContent: "space-between",
              gap: 8,
              flexWrap: "wrap",
              fontSize: 11,
              flexShrink: 0,
            }}
          >
            <span>● Landing site</span>
            <span style={{ color: "#38bdf8" }}>┄ Rover path</span>
            <span style={{ color: "#f59e0b" }}>■ Study region</span>
            <span style={muted}>Regional DEM · 360 × 360</span>
          </div>
        </section>

        {/* Right: location and view controls */}
        <aside
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 10,
            overflowY: "auto",
            minWidth: 0,
          }}
        >
          <section style={panel}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <h3 style={{ fontSize: 15, margin: "2px 0 14px" }}>
                Location Information
              </h3>
              <button
                onClick={() => setShowInfo((value) => !value)}
                aria-label="Toggle location information"
                style={{
                  color: "#cbd5e1",
                  background: "transparent",
                  border: 0,
                  cursor: "pointer",
                }}
              >
                {showInfo ? "−" : "+"}
              </button>
            </div>

            {showInfo && (
              <>
                {[
                  ["Dataset", "LOLA DEM"],
                  ["Region", "South polar"],
                  ["Grid", "360 × 360"],
                  ["Elevation units", "Meters"],
                  ["Projection", "Simple cylindrical"],
                ].map(([label, value]) => (
                  <div
                    key={label}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      gap: 8,
                      marginBottom: 11,
                      fontSize: 12,
                    }}
                  >
                    <span style={muted}>{label}</span>
                    <span style={{ textAlign: "right" }}>{value}</span>
                  </div>
                ))}
                <div
                  style={{
                    borderTop: "1px solid #2a3d50",
                    paddingTop: 10,
                    ...muted,
                    lineHeight: 1.5,
                  }}
                >
                  Elevation statistics describe the source raster, not a
                  selected point on the Moon.
                </div>
              </>
            )}
          </section>

          <section style={panel}>
            <h3 style={{ fontSize: 14, margin: "2px 0 12px" }}>
              Layer Opacity
            </h3>
            <input
              type="range"
              min="0"
              max="100"
              value={opacity}
              onChange={(event) => setOpacity(Number(event.target.value))}
              style={{ width: "100%", accentColor: "#249ef0" }}
              aria-label="Layer opacity"
            />
            <div style={muted}>{opacity}%</div>
          </section>

          <section style={panel}>
            <h3 style={{ fontSize: 14, margin: "2px 0 12px" }}>
              3D View Controls
            </h3>
            <p style={{ ...muted, lineHeight: 1.6 }}>
              Rotate: drag the terrain
              <br />
              Zoom: scroll over the terrain
              <br />
              Pan: right-click and drag
            </p>
            <button
              onClick={() => window.location.reload()}
              style={{
                width: "100%",
                padding: 9,
                border: "1px solid #36516b",
                borderRadius: 6,
                background: "#14283a",
                color: "#edf6ff",
                cursor: "pointer",
              }}
            >
              Reset View
            </button>
          </section>

          <section style={panel}>
            <h3 style={{ fontSize: 14, margin: "2px 0 8px" }}>
              Top View (2D)
            </h3>
            <div
              style={{
                height: 125,
                borderRadius: 6,
                border: "1px solid #34495e",
                background:
                  "radial-gradient(ellipse at 40% 45%, #707982, #313c48 42%, #0a111b 75%)",
                display: "grid",
                placeItems: "center",
                color: "#e5edf6",
                fontSize: 11,
              }}
            >
              Regional overview placeholder
            </div>
            <p style={muted}>
              A geographic 2D overview will be connected in a later step.
            </p>
          </section>
        </aside>
      </div>
    </main>
  );
}
