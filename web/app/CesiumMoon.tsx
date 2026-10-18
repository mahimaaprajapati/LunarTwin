"use client";

import { useEffect, useRef } from "react";

type LunarDem = {
  width: number;
  height: number;
  longitudes: number[];
  latitudes: number[];
  elevations: (number | null)[][];
};

type CesiumBrowser = typeof import("cesium");

declare global {
  interface Window {
    Cesium?: CesiumBrowser;
    CESIUM_BASE_URL?: string;
  }
}

function loadCesiumScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (window.Cesium) {
      resolve();
      return;
    }

    const existing = document.querySelector<HTMLScriptElement>(
      'script[data-cesium-browser="true"]',
    );

    if (existing) {
      existing.addEventListener(
        "load",
        () => {
          if (window.Cesium) resolve();
          else reject(new Error("Cesium browser bundle is unavailable."));
        },
        { once: true },
      );

      existing.addEventListener(
        "error",
        () => reject(new Error("Failed to load Cesium.js")),
        { once: true },
      );
      return;
    }

    const script = document.createElement("script");
    script.src = "/cesium/Cesium.js";
    script.dataset.cesiumBrowser = "true";

    script.onload = () => {
      if (window.Cesium) resolve();
      else reject(new Error("Cesium.js loaded without window.Cesium."));
    };

    script.onerror = () =>
      reject(new Error("Could not load /cesium/Cesium.js"));

    document.head.appendChild(script);
  });
}

export default function CesiumMoon() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let disposed = false;
    let viewer: import("cesium").Viewer | undefined;

    async function initialize() {
      window.CESIUM_BASE_URL = "/cesium/";
      await loadCesiumScript();

      if (disposed || !containerRef.current) return;

      const Cesium = window.Cesium;
      if (!Cesium) {
        throw new Error("Cesium browser bundle is unavailable.");
      }

      const radius = 1737400;
      const ellipsoid = new Cesium.Ellipsoid(radius, radius, radius);
      const globe = new Cesium.Globe(ellipsoid);

      globe.baseColor = Cesium.Color.fromCssColorString("#777777");
      globe.showGroundAtmosphere = false;

      viewer = new Cesium.Viewer(containerRef.current, {
        baseLayer: false,
        baseLayerPicker: false,
        geocoder: false,
        homeButton: false,
        sceneModePicker: false,
        navigationHelpButton: false,
        animation: false,
        timeline: false,
        fullscreenButton: false,
        infoBox: false,
        selectionIndicator: false,
        globe,
        skyBox: false,
        skyAtmosphere: false,
        requestRenderMode: false,
      });

      viewer.scene.backgroundColor =
        Cesium.Color.fromCssColorString("#050812");
      viewer.scene.globe.enableLighting = true;

      const imagery = new Cesium.SingleTileImageryProvider({
        url: "/cesium/Assets/Textures/moonSmall.jpg",
        rectangle: Cesium.Rectangle.MAX_VALUE,
      });

      viewer.imageryLayers.addImageryProvider(imagery);

      const response = await fetch("/lunar-dem-360.json");
      if (!response.ok) {
        throw new Error(`DEM request failed: HTTP ${response.status}`);
      }

      const dem: LunarDem = await response.json();
      if (disposed || !viewer) return;

      const { width, height, longitudes, latitudes, elevations } = dem;

      if (
        width < 2 ||
        height < 2 ||
        longitudes.length !== width ||
        latitudes.length !== height ||
        elevations.length !== height ||
        elevations.some((row) => row.length !== width)
      ) {
        throw new Error("DEM dimensions are inconsistent.");
      }

      const positions: number[] = [];
      const colors: number[] = [];
      const indices: number[] = [];

      let min = Infinity;
      let max = -Infinity;

      for (const row of elevations) {
        for (const value of row) {
          if (typeof value === "number" && Number.isFinite(value)) {
            min = Math.min(min, value);
            max = Math.max(max, value);
          }
        }
      }

      const isValid = (row: number, col: number) => {
        const value = elevations[row]?.[col];
        return typeof value === "number" && Number.isFinite(value);
      };

      for (let row = 0; row < height; row++) {
        for (let col = 0; col < width; col++) {
          const elevation = elevations[row][col];
          const valid =
            typeof elevation === "number" && Number.isFinite(elevation);

          const longitude = (longitudes[col] * Math.PI) / 180;
          const latitude = (latitudes[row] * Math.PI) / 180;
          const r = radius + (valid ? elevation : 0);
          const cosLat = Math.cos(latitude);

          positions.push(
            r * cosLat * Math.cos(longitude),
            r * cosLat * Math.sin(longitude),
            r * Math.sin(latitude),
          );

          const t =
            valid && max > min ? (elevation - min) / (max - min) : 0.5;
          const shade = 0.34 + t * 0.42;

          colors.push(shade, shade, shade);
        }
      }

      for (let row = 0; row < height - 1; row++) {
        for (let col = 0; col < width - 1; col++) {
          const a = row * width + col;
          const b = a + 1;
          const c = a + width;
          const d = c + 1;

          if (
            isValid(row, col) &&
            isValid(row, col + 1) &&
            isValid(row + 1, col)
          ) {
            indices.push(a, b, c);
          }

          if (
            isValid(row, col + 1) &&
            isValid(row + 1, col) &&
            isValid(row + 1, col + 1)
          ) {
            indices.push(b, d, c);
          }
        }
      }

      // Cesium's PerInstanceColorAppearance uses per-instance color,
      // so use a supported vertex-color appearance for this mesh.
      const vertexColors = new Float32Array(positions.length / 3 * 4);

      for (let vertex = 0; vertex < positions.length / 3; vertex++) {
        vertexColors[vertex * 4] = colors[vertex * 3];
        vertexColors[vertex * 4 + 1] = colors[vertex * 3 + 1];
        vertexColors[vertex * 4 + 2] = colors[vertex * 3 + 2];
        vertexColors[vertex * 4 + 3] = 1;
      }

      const attributes = {
        position: new Cesium.GeometryAttribute({
          componentDatatype: Cesium.ComponentDatatype.DOUBLE,
          componentsPerAttribute: 3,
          values: new Float64Array(positions),
        }),
        color: new Cesium.GeometryAttribute({
          componentDatatype: Cesium.ComponentDatatype.FLOAT,
          componentsPerAttribute: 4,
          values: vertexColors,
        }),
        normal: undefined,
        st: undefined,
        bitangent: undefined,
        tangent: undefined,
      };

      const geometry = new Cesium.Geometry({
        attributes,
        indices: new Uint32Array(indices),
        primitiveType: Cesium.PrimitiveType.TRIANGLES,
        boundingSphere: Cesium.BoundingSphere.fromVertices(positions),
      });

      const instance = new Cesium.GeometryInstance({
        geometry,
      });

      const terrainPrimitive = new Cesium.Primitive({
        geometryInstances: instance,
        appearance: new Cesium.PerInstanceColorAppearance({
          flat: false,
          translucent: false,
          closed: false,
          faceForward: true,
        }),
        asynchronous: false,
      });

      viewer.scene.primitives.add(terrainPrimitive);
      viewer.scene.requestRender();

      console.log("LOLA terrain mesh added", {
        width,
        height,
        vertices: positions.length / 3,
        triangles: indices.length / 3,
        longitudeRange: [longitudes[0], longitudes[width - 1]],
        latitudeRange: [latitudes[0], latitudes[height - 1]],
      });

      let readinessChecks = 0;

      const checkTerrainReady = () => {
        if (disposed || !viewer || viewer.isDestroyed()) return;

        readinessChecks++;
        console.log(
          "Terrain readiness check:",
          readinessChecks,
          terrainPrimitive.ready,
        );

        if (!terrainPrimitive.ready && readinessChecks < 10) {
          requestAnimationFrame(checkTerrainReady);
        }
      };

      requestAnimationFrame(checkTerrainReady);

      viewer.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(5, -85, 4800000, ellipsoid),
      });
    }

    initialize().catch((error: unknown) => {
      if (!disposed) {
        console.error("Cesium Moon initialization failed:", error);
      }
    });

    return () => {
      disposed = true;
      if (viewer && !viewer.isDestroyed()) {
        viewer.destroy();
      }
    };
  }, []);

  return (
    <div
      ref={containerRef}
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
      }}
    />
  );
}
