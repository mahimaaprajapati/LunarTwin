"use client";

import { useEffect, useRef, useState } from "react";

type LunarDem = {
    width: number;
  height: number;
  x_km: number[];
  y_km: number[];
  elevations: (number | null)[][];
};

function calculateLocalRelief(
  elevations: (number | null)[][],
  width: number,
  height: number,
  sigma = 8,
): number[] {
  const n = width * height;
  const values = new Float64Array(n);
  const valid = new Float64Array(n);
  for (let r = 0; r < height; r++) {
    for (let c = 0; c < width; c++) {
      const v = elevations[r]?.[c];
      if (typeof v === "number" && Number.isFinite(v)) {
        values[r * width + c] = v;
        valid[r * width + c] = 1;
      }
    }
  }

  const radius = Math.max(1, Math.ceil(sigma * 3));
  const kernel = Array.from({ length: radius * 2 + 1 }, (_, j) => {
    const x = j - radius;
    return Math.exp(-(x * x) / (2 * sigma * sigma));
  });
  const convolve = (input: Float64Array, horizontal: boolean) => {
    const out = new Float64Array(n);
    for (let r = 0; r < height; r++) {
      for (let c = 0; c < width; c++) {
        let sum = 0;
        for (let k = -radius; k <= radius; k++) {
          const rr = horizontal ? r : r + k;
          const cc = horizontal ? c + k : c;
          if (rr >= 0 && rr < height && cc >= 0 && cc < width) {
            sum += input[rr * width + cc] * kernel[k + radius];
          }
        }
        out[r * width + c] = sum;
      }
    }
    return out;
  };

  const weighted = new Float64Array(n);
  for (let i = 0; i < n; i++) weighted[i] = values[i] * valid[i];
  const numerator = convolve(convolve(weighted, true), false);
  const denominator = convolve(convolve(valid, true), false);
  return Array.from({ length: n }, (_, i) =>
    valid[i] && denominator[i] > 1e-12
      ? values[i] - numerator[i] / denominator[i]
      : 0
  );
}

export default function Viewer() {
  const containerRef = useRef<HTMLDivElement>(null);
  const reliefUpdaterRef = useRef<((enabled: boolean) => void) | null>(null);
  const [localRelief, setLocalRelief] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    let cleanup: (() => void) | undefined;

    async function start() {
      try {
        const THREE = await import("three");
        const { OrbitControls } = await import("three/examples/jsm/controls/OrbitControls.js");
        if (cancelled) return;

        const response = await fetch("/lunar-dem-projected-360.json");
        if (!response.ok) throw new Error(`DEM request failed: HTTP ${response.status}`);
        const dem = (await response.json()) as LunarDem;
        const { width, height, x_km, y_km, elevations } = dem;
        const container = containerRef.current;
        if (cancelled || !container) return;
        if (
  width < 2 || height < 2 ||
  x_km.length !== width || y_km.length !== height ||
  elevations.length !== height ||
  elevations.some((row) => !Array.isArray(row) || row.length !== width)
) {
  throw new Error("DEM dimensions are inconsistent.");
}

        let minElevation = Infinity;
        let maxElevation = -Infinity;
        let sum = 0;
        let count = 0;
        for (const row of elevations) {
          for (const v of row) {
            if (typeof v === "number" && Number.isFinite(v)) {
              minElevation = Math.min(minElevation, v);
              maxElevation = Math.max(maxElevation, v);
              sum += v;
              count++;
            }
          }
        }
        if (!count) throw new Error("DEM contains no valid elevation values.");

        const mean = sum / count;
        const localReliefValues = calculateLocalRelief(elevations, width, height);
        const xCenter = (x_km[0] + x_km[width - 1]) / 2;
const yCenter = (y_km[0] + y_km[height - 1]) / 2;
        const moonRadiusKm = 1737.4;
        const horizontalScale = 1 / 3;
        // Convert metres to kilometres, with 4x vertical exaggeration.
        const verticalScale = horizontalScale * 4 / 1000;
const mapWidthKm = 303.2335;
const mapHeightKm = 303.3500;
        const positions = new Float32Array(width * height * 3);
        const colors = new Float32Array(width * height * 3);
        const indices: number[] = [];
        const range = Math.max(1, maxElevation - minElevation);

        for (let r = 0; r < height; r++) {
          for (let c = 0; c < width; c++) {
            const i = r * width + c;
            const value = elevations[r][c];
            const ok = typeof value === "number" && Number.isFinite(value);
                        positions[3 * i] =
              (x_km[c] - xCenter) * horizontalScale;

            positions[3 * i + 1] =
              (y_km[r] - yCenter) * horizontalScale;
            positions[3 * i + 2] = ok ? (value - mean) * verticalScale : 0;

            const t = ok ? (value - minElevation) / range : 0.35;
            const shade = 0.24 + t * 0.56;
            colors[3 * i] = shade;
            colors[3 * i + 1] = shade * 0.99;
            colors[3 * i + 2] = shade * 0.97;
          }
        }
const validAtForDiagnostic = (v: unknown) =>
  typeof v === "number" && Number.isFinite(v);
 
let invalidCount = 0;

for (let r = 0; r < height; r++) {
  for (let c = 0; c < width; c++) {
    if (!validAtForDiagnostic(elevations[r]?.[c])) {
      invalidCount++;
    }
  }
}

console.log("DEM dimensions:", width, height);
console.log("Invalid elevation cells:", invalidCount);
console.log(
  "Invalid elevation percentage:",
  ((invalidCount / (width * height)) * 100).toFixed(2) + "%"
);

const validAt = (r: number, c: number) => {
  const v = elevations[r]?.[c];
  return typeof v === "number" && Number.isFinite(v);
};

for (let r = 0; r < height - 1; r++) {
  for (let c = 0; c < width - 1; c++) {
    const a = r * width + c;
    const b = a + 1;
    const d = a + width;
    const e = d + 1;

    // Render a grid cell only when all four elevations are valid.
    if (
      validAt(r, c) &&
      validAt(r, c + 1) &&
      validAt(r + 1, c) &&
      validAt(r + 1, c + 1)
    ) {
      indices.push(a, d, b, b, d, e);
    }
  }
}
        
console.log("DEM grid:", {
  width,
  height,
  firstRowSamples: elevations[0]?.slice(0, 8),
  lastRowSamples: elevations[height - 1]?.slice(0, 8),
  firstColumnSamples: elevations
    .slice(0, 8)
    .map((row) => row?.[0]),
  lastColumnSamples: elevations
    .slice(0, 8)
    .map((row) => row?.[width - 1]),
  triangleCount: indices.length / 3,
});

        if (!indices.length) throw new Error("DEM has no valid neighboring cells to render.");

        const scene = new THREE.Scene();
        scene.background = new THREE.Color("#050812");
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        container.appendChild(renderer.domElement);

        const camera = new THREE.PerspectiveCamera(42, 1, 0.05, 10000);
        camera.up.set(0, 0, 1);
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.07;
        controls.enablePan = true;
        controls.minDistance = 2;
        controls.maxDistance = 5000;

        scene.add(new THREE.AmbientLight(0xffffff, 1.0));
        const sun = new THREE.DirectionalLight(0xffffff, 2.4);
        sun.position.set(-90, -110, 140);
        scene.add(sun);
        const fill = new THREE.DirectionalLight(0xb9d3ff, 0.45);
        fill.position.set(100, 30, 70);
        scene.add(fill);

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
        geometry.setIndex(indices);
        geometry.computeVertexNormals();
        geometry.computeBoundingBox();
        geometry.computeBoundingSphere();
        const material = new THREE.MeshStandardMaterial({
          vertexColors: true, roughness: 1, metalness: 0, side: THREE.DoubleSide,
        });
        scene.add(new THREE.Mesh(geometry, material));

        const updateRelief = (enabled: boolean) => {
          const attribute = geometry.getAttribute("position") as import("three").BufferAttribute;
          for (let i = 0; i < width * height; i++) {
            const r = Math.floor(i / width), c = i % width;
            const value = elevations[r][c];
            const ok = typeof value === "number" && Number.isFinite(value);
            const z = enabled ? localReliefValues[i] * verticalScale * 2.5 : (ok ? value - mean : 0) * verticalScale;
            attribute.setZ(i, ok ? z : 0);
          }
          attribute.needsUpdate = true;
          geometry.computeVertexNormals();
          geometry.computeBoundingBox();
          geometry.computeBoundingSphere();
        };
        reliefUpdaterRef.current = updateRelief;
        updateRelief(localRelief);

        const fitCamera = () => {
          const w = Math.max(container.clientWidth, 1);
          const h = Math.max(container.clientHeight, 1);
          camera.aspect = w / h;
          camera.updateProjectionMatrix();
          renderer.setSize(w, h);
          geometry.computeBoundingBox();
          const box = geometry.boundingBox;
          if (!box) return;
          const center = box.getCenter(new THREE.Vector3());
          const size = box.getSize(new THREE.Vector3());
          controls.target.copy(center);

          const vfov = THREE.MathUtils.degToRad(camera.fov);
          const hfov = 2 * Math.atan(Math.tan(vfov / 2) * camera.aspect);
          const distance = Math.max(
            (size.y / 2) / Math.tan(vfov / 2),
            (size.x / 2) / Math.tan(hfov / 2),
          ) * 1.2;

          camera.position.set(
            center.x + size.x * 0.08,
            center.y - distance * 0.9,
            center.z + distance * 0.72 + size.z * 0.2,
          );
          camera.near = Math.max(0.02, distance / 2000);
          camera.far = Math.max(1000, distance * 20);
          camera.updateProjectionMatrix();
          controls.minDistance = Math.max(1, Math.min(size.x, size.y) * 0.025);
          controls.maxDistance = Math.max(size.x, size.y) * 12;
          controls.update();
        };
        fitCamera();

        const size = geometry.boundingBox!.getSize(new THREE.Vector3());
        const starRadius = Math.max(250, Math.max(size.x, size.y) * 3);
        const starPositions: number[] = [];
        for (let i = 0; i < 900; i++) {
          const u = Math.random() * 2 - 1, angle = Math.random() * Math.PI * 2;
          const ring = Math.sqrt(1 - u * u);
          starPositions.push(starRadius * ring * Math.cos(angle), starRadius * ring * Math.sin(angle), starRadius * u);
        }
        const starGeometry = new THREE.BufferGeometry();
        starGeometry.setAttribute("position", new THREE.Float32BufferAttribute(starPositions, 3));
        const starMaterial = new THREE.PointsMaterial({ color: "#aabbd4", size: 1, sizeAttenuation: false });
        scene.add(new THREE.Points(starGeometry, starMaterial));

        const observer = new ResizeObserver(fitCamera);
        observer.observe(container);
        let frame = 0;
        const animate = () => {
          if (cancelled) return;
          frame = requestAnimationFrame(animate);
          controls.update();
          renderer.render(scene, camera);
        };
        animate();

        cleanup = () => {
          cancelAnimationFrame(frame);
          observer.disconnect();
          controls.dispose();
          reliefUpdaterRef.current = null;
          geometry.dispose();
          material.dispose();
          starGeometry.dispose();
          starMaterial.dispose();
          renderer.dispose();
          renderer.domElement.remove();
        };
        if (cancelled) cleanup();
      } catch (err) {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : String(err);
          console.error("Lunar terrain error:", err);
          setError(message);
        }
      }
    }

    void start();
    return () => { cancelled = true; cleanup?.(); };
  }, []);

  useEffect(() => { reliefUpdaterRef.current?.(localRelief); }, [localRelief]);

  return (
    <div style={{ position: "relative", width: "100%", height: "100%", minHeight: 500, background: "#050812" }}>
      <div style={{
        position: "absolute", top: 12, left: 12, zIndex: 2, display: "flex",
        alignItems: "center", gap: 10, padding: "10px 12px", borderRadius: 8,
        background: "rgba(10,15,28,.92)", border: "1px solid rgba(125,153,183,.28)",
        color: "#E5E7EB", fontSize: 13,
      }}>
        <span>Terrain shading</span>
        <button type="button" onClick={() => setLocalRelief((v) => !v)} style={{
          border: "1px solid #64748b", borderRadius: 6, padding: "6px 10px",
          color: "#F8FAFC", background: localRelief ? "#334155" : "#111827", cursor: "pointer",
        }}>
          {localRelief ? "Local Relief ON" : "Local Relief OFF"}
        </button>
      </div>
      {error && <div style={{
        position: "absolute", zIndex: 3, left: 12, right: 12, bottom: 12,
        padding: 10, borderRadius: 6, background: "#7f1d1d", color: "#fff", fontSize: 12,
      }}>Terrain failed to load: {error}</div>}
      <div ref={containerRef} style={{
        position: "absolute", inset: 0, width: "100%", height: "100%", minHeight: 500,
        overflow: "hidden", background: "#050812",
      }} />
    </div>
  );
}
