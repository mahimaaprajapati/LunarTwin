
"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

type DEMData = {
  width: number;
  height: number;
  x_km: number[];
  y_km: number[];
  elevations: (number | null)[][];
};

type TerrainPrototypeProps = {
  dataUrl?: string;
  verticalExaggeration?: number;
};

export default function TerrainPrototype({
  dataUrl = "/lunar-dem-projected-360.json",
  verticalExaggeration = 1.5,
}: TerrainPrototypeProps) {
  const hostRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
  const hostElement = hostRef.current;
  if (hostElement === null) return;

  const host: HTMLDivElement = hostElement;

    let disposed = false;
    let frameId = 0;
    let observer: ResizeObserver | undefined;
    let renderer: THREE.WebGLRenderer | undefined;
    let controls: OrbitControls | undefined;
    let geometry: THREE.BufferGeometry | undefined;
    let material: THREE.MeshStandardMaterial | undefined;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#070b14");

    const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 10000);
    camera.up.set(0, 0, 1);

    scene.add(new THREE.AmbientLight(0xffffff, 1.6));

    const sun = new THREE.DirectionalLight(0xffffff, 2.2);
    sun.position.set(-1, -1, 2);
    scene.add(sun);

    const fill = new THREE.DirectionalLight(0xb8ccff, 0.5);
    fill.position.set(1, 1, 1);
    scene.add(fill);

    async function initialize() {
      try {
        const response = await fetch(dataUrl);

        if (!response.ok) {
          throw new Error(`DEM request failed: ${response.status}`);
        }

        const dem = (await response.json()) as DEMData;
        if (disposed) return;

        const { width, height, x_km, y_km, elevations } = dem;

        if (
          !Number.isInteger(width) ||
          !Number.isInteger(height) ||
          width < 2 ||
          height < 2 ||
          x_km.length !== width ||
          y_km.length !== height ||
          elevations.length !== height ||
          elevations.some((row) => !Array.isArray(row) || row.length !== width)
        ) {
          throw new Error("DEM dimensions or coordinate arrays do not match.");
        }

        const valid = (r: number, c: number): boolean => {
          const value = elevations[r]?.[c];
          return typeof value === "number" && Number.isFinite(value);
        };

        // Iterative min/max avoids spreading a large array into Math.min/max.
        let minZ = Infinity;
        let maxZ = -Infinity;
        let validCells = 0;

        for (let r = 0; r < height; r++) {
          for (let c = 0; c < width; c++) {
            if (!valid(r, c)) continue;
            const z = elevations[r][c] as number;
            minZ = Math.min(minZ, z);
            maxZ = Math.max(maxZ, z);
            validCells++;
          }
        }

        if (validCells === 0) {
          throw new Error("DEM contains no valid elevations.");
        }

        const midZ = (minZ + maxZ) / 2;

        const xMin = Math.min(...x_km);
        const xMax = Math.max(...x_km);
        const yMin = Math.min(...y_km);
        const yMax = Math.max(...y_km);

        if (
          ![xMin, xMax, yMin, yMax].every(Number.isFinite) ||
          xMax <= xMin ||
          yMax <= yMin
        ) {
          throw new Error("DEM coordinate arrays contain invalid bounds.");
        }

        const horizontalSpanKm = Math.max(xMax - xMin, yMax - yMin);
        const horizontalScale = 1 / 100;
        const verticalScale = horizontalScale * verticalExaggeration / 1000;

        const positions = new Float32Array(width * height * 3);
        const colors = new Float32Array(width * height * 3);
        const indices: number[] = [];

        for (let r = 0; r < height; r++) {
          for (let c = 0; c < width; c++) {
            const i = r * width + c;
            const z = elevations[r][c];
            const isValid = valid(r, c);

            positions[3 * i] =
              (x_km[c] - (xMin + xMax) / 2) * horizontalScale;
            positions[3 * i + 1] =
              (y_km[r] - (yMin + yMax) / 2) * horizontalScale;
            positions[3 * i + 2] = isValid
              ? ((z as number) - midZ) * verticalScale
              : 0;

            const t = isValid
              ? ((z as number) - minZ) / Math.max(1, maxZ - minZ)
              : 0;

            const shade = isValid ? 0.42 + t * 0.42 : 0.42;
            colors[3 * i] = shade;
            colors[3 * i + 1] = shade * 0.99;
            colors[3 * i + 2] = shade * 0.96;
          }
        }

        for (let r = 0; r < height - 1; r++) {
          for (let c = 0; c < width - 1; c++) {
            const a = r * width + c;
            const b = a + 1;
            const d = a + width;
            const e = d + 1;

            if (valid(r, c) && valid(r + 1, c) && valid(r, c + 1)) {
              indices.push(a, d, b);
            }

            if (
              valid(r, c + 1) &&
              valid(r + 1, c) &&
              valid(r + 1, c + 1)
            ) {
              indices.push(b, d, e);
            }
          }
        }

        if (indices.length === 0) {
          throw new Error("No valid neighboring DEM cells to build terrain.");
        }

        geometry = new THREE.BufferGeometry();
        geometry.setAttribute(
          "position",
          new THREE.BufferAttribute(positions, 3)
        );
        geometry.setAttribute(
          "color",
          new THREE.BufferAttribute(colors, 3)
        );
        geometry.setIndex(indices);
        geometry.computeVertexNormals();
        geometry.computeBoundingBox();
        geometry.computeBoundingSphere();

        material = new THREE.MeshStandardMaterial({
          vertexColors: true,
          roughness: 1,
          metalness: 0,
          side: THREE.DoubleSide,
        });

        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        host.appendChild(renderer.domElement);

        controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.06;

        const box = geometry.boundingBox;
        if (!box) throw new Error("Could not calculate terrain bounds.");

        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        const span = Math.max(size.x, size.y, size.z, 0.1);

        controls.target.copy(center);
        camera.position.set(
          center.x + span * 0.8,
          center.y - span * 1.5,
          center.z + span * 1.1
        );
        camera.near = 0.001;
        camera.far = span * 100;
        camera.updateProjectionMatrix();
        controls.update();

        const resize = () => {
          if (disposed || !renderer || !host.isConnected) return;

          const w = Math.max(1, host.clientWidth);
          const h = Math.max(1, host.clientHeight);

          renderer.setSize(w, h);
          camera.aspect = w / h;
          camera.updateProjectionMatrix();
        };

        observer = new ResizeObserver(resize);
        observer.observe(host);
        resize();

        console.info("Terrain prototype ready", {
          width,
          height,
          validCells,
          triangles: indices.length / 3,
          elevationRangeMeters: [minZ, maxZ],
          horizontalSpanKm,
        });

        const animate = () => {
          if (disposed || !renderer || !controls) return;

          frameId = requestAnimationFrame(animate);
          controls.update();
          renderer.render(scene, camera);
        };

        animate();
      } catch (error) {
        if (!disposed) {
          console.error("Terrain prototype failed:", error);
        }
      }
    }

    void initialize();

    return () => {
      disposed = true;
      cancelAnimationFrame(frameId);
      observer?.disconnect();
      controls?.dispose();

      if (geometry) geometry.dispose();
      if (material) material.dispose();

      if (renderer) {
        renderer.dispose();

        if (renderer.domElement.parentElement === host) {
          host.removeChild(renderer.domElement);
        }
      }
    };
  }, [dataUrl, verticalExaggeration]);

  return (
    <div
      ref={hostRef}
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        minHeight: 420,
        overflow: "hidden",
        borderRadius: 12,
        background: "#070b14",
      }}
    />
  );
}
