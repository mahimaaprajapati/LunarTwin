"use client";

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

type Layer = "terrain" | "resource" | "slope" | "illumination" | "uncertainty";

const LAYERS: { id: Layer; label: string; description: string }[] = [
  { id: "terrain", label: "Elevation", description: "Grayscale elevation and crater shading" },
  { id: "resource", label: "Resource potential", description: "Illustrative low-to-high prospecting overlay" },
  { id: "slope", label: "Slope", description: "Illustrative slope intensity derived from terrain gradients" },
  { id: "illumination", label: "Illumination", description: "Directional-light estimate for visual exploration" },
  { id: "uncertainty", label: "Uncertainty", description: "Illustrative uncertainty overlay" },
];

/**
 * LunarTwin TerrainPrototype
 *
 * A self-contained Three.js terrain prototype with selectable visual layers.
 * It uses procedural terrain as a fallback and does not claim to be actual LOLA
 * DEM data. Connect a decoded DEM height array to the height-generation section
 * when the source file format and dimensions are known.
 */
export default function TerrainPrototype() {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const [layer, setLayer] = useState<Layer>("terrain");
  const [opacity, setOpacity] = useState(78);
  const [relief, setRelief] = useState(true);
  const [showGrid, setShowGrid] = useState(false);
  const [resetToken, setResetToken] = useState(0);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    } catch {
      host.innerHTML =
        '<div style="padding:20px;color:#e6f1ff;font:14px system-ui">WebGL could not start. Enable browser hardware acceleration and reload.</div>';
      return;
    }

    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.12;
    renderer.domElement.style.cssText = "display:block;width:100%;height:100%;outline:none;";
    host.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#050a12");
    scene.fog = new THREE.Fog("#050a12", 52, 120);

    const camera = new THREE.PerspectiveCamera(43, 1, 0.1, 250);
    camera.position.set(0, 23, 34);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 0.4, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.065;
    controls.minDistance = 11;
    controls.maxDistance = 78;
    controls.maxPolarAngle = Math.PI * 0.48;
    controls.update();

    scene.add(new THREE.HemisphereLight("#c6dcff", "#20232b", 1.35));
    const sun = new THREE.DirectionalLight("#fff0d6", relief ? 3.1 : 1.65);
    sun.position.set(-22, 30, 15);
    scene.add(sun);
    const fill = new THREE.DirectionalLight("#5388ff", 0.7);
    fill.position.set(18, 9, -20);
    scene.add(fill);

    // Stable seeded randomness keeps the demo terrain repeatable.
    let seed = 317921;
    const random = () => {
      seed = (seed * 1664525 + 1013904223) >>> 0;
      return seed / 4294967296;
    };

    const craters = [
      { x: -7.8, z: 5.0, r: 5.2, depth: 1.9, rim: 0.72 },
      { x: 5.7, z: -4.4, r: 3.4, depth: 1.1, rim: 0.48 },
      { x: 1.2, z: 7.8, r: 2.25, depth: 0.7, rim: 0.34 },
      { x: 10.0, z: 4.8, r: 1.8, depth: 0.58, rim: 0.28 },
      { x: -1.0, z: -8.2, r: 2.7, depth: 0.82, rim: 0.4 },
      { x: -13.5, z: -7.5, r: 2.1, depth: 0.65, rim: 0.32 },
      { x: 13.5, z: -10.5, r: 3.0, depth: 0.9, rim: 0.45 },
      { x: -14.0, z: 12.0, r: 2.8, depth: 0.82, rim: 0.42 },
    ];
    for (let i = 0; i < 35; i++) {
      const r = 0.45 + Math.pow(random(), 1.7) * 2.2;
      craters.push({
        x: (random() - 0.5) * 44,
        z: (random() - 0.5) * 44,
        r,
        depth: 0.22 + r * (0.12 + random() * 0.1),
        rim: 0.1 + r * 0.05,
      });
    }

    const terrainHeight = (x: number, z: number) => {
      let y =
        0.32 * Math.sin(x * 0.18 + Math.sin(z * 0.13)) +
        0.24 * Math.cos(z * 0.21) +
        0.13 * Math.sin((x + z) * 0.72) +
        0.06 * Math.cos(x * 1.35 - z * 0.94);
      for (const crater of craters) {
        const q = Math.hypot(x - crater.x, z - crater.z) / crater.r;
        if (q < 1.7) {
          y +=
            -crater.depth * Math.exp(-Math.pow(q / 0.72, 2) * 1.65) +
            crater.rim * Math.exp(-Math.pow((q - 0.94) / 0.13, 2)) +
            0.09 * crater.depth * Math.exp(-Math.pow((q - 1.2) / 0.3, 2));
        }
      }
      // Soften the edge so the mesh blends into the dark scene.
      const radius = Math.hypot(x, z);
      const fade = THREE.MathUtils.clamp((radius - 28) / 18, 0, 0.88);
      return y * (1 - fade);
    };

    const geometry = new THREE.PlaneGeometry(72, 72, 260, 260);
    geometry.rotateX(-Math.PI / 2);
    const positions = geometry.attributes.position as THREE.BufferAttribute;
    const colors: number[] = [];
    const c = new THREE.Color();
    const base = new THREE.Color("#888b90");
    const dark = new THREE.Color("#222a39");
    const low = new THREE.Color("#2923a6");
    const blue = new THREE.Color("#087be8");
    const cyan = new THREE.Color("#23d8d0");
    const yellow = new THREE.Color("#ffe44d");
    const red = new THREE.Color("#ef3828");
    const purple = new THREE.Color("#922dca");

    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i);
      const z = positions.getZ(i);
      const y = terrainHeight(x, z);
      positions.setY(i, y);

      const dx = (terrainHeight(x + 0.16, z) - terrainHeight(x - 0.16, z)) / 0.32;
      const dz = (terrainHeight(x, z + 0.16) - terrainHeight(x, z - 0.16)) / 0.32;
      const slope = Math.min(1, Math.hypot(dx, dz) / 1.15);
      const prospect = THREE.MathUtils.clamp(
        0.5 + 0.23 * Math.sin(x * 0.17 + z * 0.1) +
          0.18 * Math.cos(z * 0.21 - x * 0.08) +
          0.1 * Math.sin((x - z) * 0.34),
        0,
        1
      );
      const illumination = THREE.MathUtils.clamp(
        0.5 + 0.3 * Math.sin(x * 0.1 + z * 0.04) - 0.25 * slope,
        0,
        1
      );
      const uncertainty = THREE.MathUtils.clamp(
        0.18 + 0.42 * Math.abs(Math.sin(x * 0.13) * Math.cos(z * 0.11)) + slope * 0.25,
        0,
        1
      );

      // Terrain-derived values are illustrative until real scientific rasters are connected.
      if (layer === "terrain") {
        const elevation = THREE.MathUtils.clamp((y + 1.8) / 3.8, 0, 1);
        c.copy(dark).lerp(base, 0.28 + elevation * 0.68);
      } else if (layer === "resource") {
        if (prospect < 0.28) c.copy(low).lerp(blue, prospect / 0.28);
        else if (prospect < 0.55) c.copy(blue).lerp(cyan, (prospect - 0.28) / 0.27);
        else if (prospect < 0.78) c.copy(cyan).lerp(yellow, (prospect - 0.55) / 0.23);
        else c.copy(yellow).lerp(red, (prospect - 0.78) / 0.22);
        c.lerp(base, 0.15);
      } else if (layer === "slope") {
        c.copy(new THREE.Color("#163a93")).lerp(new THREE.Color("#31d8cc"), slope);
        if (slope > 0.62) c.lerp(new THREE.Color("#ffb12b"), (slope - 0.62) / 0.38);
      } else if (layer === "illumination") {
        c.copy(new THREE.Color("#202b75")).lerp(new THREE.Color("#ffe9a0"), illumination);
        c.lerp(new THREE.Color("#ffffff"), Math.max(0, illumination - 0.78) * 0.45);
      } else {
        c.copy(new THREE.Color("#211b6e")).lerp(purple, uncertainty);
        c.lerp(new THREE.Color("#ff4d9a"), Math.max(0, uncertainty - 0.68) * 0.7);
      }

      if (layer !== "terrain") c.lerp(base, 1 - opacity / 100);
      colors.push(c.r, c.g, c.b);
    }

    geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
    geometry.computeVertexNormals();

    const material = new THREE.MeshStandardMaterial({
      vertexColors: true,
      roughness: 1,
      metalness: 0,
      flatShading: false,
    });
    const terrain = new THREE.Mesh(geometry, material);
    terrain.position.y = -0.4;
    terrain.receiveShadow = true;
    scene.add(terrain);

    // Small, low-poly rocks create scale and surface texture.
    const rockGeometry = new THREE.IcosahedronGeometry(0.11, 0);
    const rockMaterial = new THREE.MeshStandardMaterial({ color: "#666b73", roughness: 1 });
    const rocks = new THREE.InstancedMesh(rockGeometry, rockMaterial, 420);
    const dummy = new THREE.Object3D();
    for (let i = 0; i < 420; i++) {
      const x = (random() - 0.5) * 66;
      const z = (random() - 0.5) * 66;
      dummy.position.set(x, terrainHeight(x, z) - 0.28, z);
      const scale = 0.22 + random() * 1.6;
      dummy.scale.set(scale, 0.25 + random() * 0.55, scale);
      dummy.rotation.set(random() * 2, random() * 2, random() * 2);
      dummy.updateMatrix();
      rocks.setMatrixAt(i, dummy.matrix);
    }
    scene.add(rocks);

    // Optional subtle grid for visual orientation.
    let grid: THREE.GridHelper | null = null;
    if (showGrid) {
      grid = new THREE.GridHelper(72, 36, "#31506b", "#1c3045");
      grid.position.y = -0.3;
      const gridMat = grid.material as THREE.Material;
      gridMat.transparent = true;
      gridMat.opacity = 0.22;
      scene.add(grid);
    }

    // Mission path is a demo layer; terrain-following samples the same height function.
    const pathXZ = [
      [15, 17], [11, 12], [8, 8], [5.5, 4.5], [3, 1], [0.5, -2], [-2, -5], [-5.5, -9],
    ];
    const routePoints = pathXZ.map(([x, z]) => new THREE.Vector3(x, terrainHeight(x, z) + 0.12, z));
    const routeCurve = new THREE.CatmullRomCurve3(routePoints);
    const routeGeometry = new THREE.TubeGeometry(routeCurve, 120, 0.055, 7, false);
    const routeMaterial = new THREE.MeshBasicMaterial({ color: "#e9f8ff" });
    const route = new THREE.Mesh(routeGeometry, routeMaterial);
    scene.add(route);

    const waypointGeo = new THREE.SphereGeometry(0.22, 14, 10);
    const waypointMat = new THREE.MeshStandardMaterial({
      color: "#7de2ff",
      emissive: "#1378ac",
      emissiveIntensity: 1.4,
    });
    routePoints.slice(1, -1).forEach((point) => {
      const marker = new THREE.Mesh(waypointGeo, waypointMat);
      marker.position.copy(point);
      marker.position.y += 0.08;
      scene.add(marker);
    });

    // Landing-site pin at the end of the route.
    const landing = new THREE.Group();
    const pin = new THREE.Mesh(
      new THREE.CylinderGeometry(0.045, 0.045, 0.9, 10),
      new THREE.MeshStandardMaterial({ color: "#f2f5fa" })
    );
    pin.position.y = 0.48;
    landing.add(pin);
    const head = new THREE.Mesh(
      new THREE.SphereGeometry(0.28, 18, 14),
      new THREE.MeshStandardMaterial({ color: "#ff665e", emissive: "#9f1723", emissiveIntensity: 0.8 })
    );
    head.position.y = 1.0;
    landing.add(head);
    landing.position.set(-5.5, terrainHeight(-5.5, -9) - 0.28, -9);
    scene.add(landing);

    // Simple rover at the start of the route.
    const rover = new THREE.Group();
    const body = new THREE.Mesh(
      new THREE.BoxGeometry(1.05, 0.3, 0.76),
      new THREE.MeshStandardMaterial({ color: "#d7b66f", metalness: 0.2, roughness: 0.65 })
    );
    body.position.y = 0.55;
    rover.add(body);
    const wheelMat = new THREE.MeshStandardMaterial({ color: "#20252c", roughness: 0.95 });
    for (const x of [-0.43, 0.43]) {
      for (const z of [-0.4, 0.4]) {
        const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.12, 12), wheelMat);
        wheel.rotation.z = Math.PI / 2;
        wheel.position.set(x, 0.28, z);
        rover.add(wheel);
      }
    }
    const mast = new THREE.Mesh(
      new THREE.CylinderGeometry(0.035, 0.035, 0.48, 8),
      new THREE.MeshStandardMaterial({ color: "#dce8f2", metalness: 0.35 })
    );
    mast.position.set(0.18, 0.95, -0.1);
    rover.add(mast);
    rover.position.set(15, terrainHeight(15, 17) - 0.28, 17);
    rover.rotation.y = -0.55;
    scene.add(rover);

    const resize = () => {
      const width = Math.max(1, host.clientWidth);
      const height = Math.max(1, host.clientHeight);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height, false);
    };
    const observer = new ResizeObserver(resize);
    observer.observe(host);
    resize();

    let animationId = 0;
    const animate = () => {
      animationId = requestAnimationFrame(animate);
      controls.update();
      head.scale.setScalar(1 + Math.sin(performance.now() * 0.004) * 0.06);
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(animationId);
      observer.disconnect();
      controls.dispose();
      renderer.dispose();
      if (renderer.domElement.parentElement === host) host.removeChild(renderer.domElement);
      scene.traverse((object) => {
        const mesh = object as THREE.Mesh;
        if (mesh.geometry) mesh.geometry.dispose();
        if (mesh.material) {
          const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
          materials.forEach((m) => m.dispose());
        }
      });
    };
  }, [layer, opacity, relief, showGrid, resetToken]);

  const currentLayer = LAYERS.find((item) => item.id === layer)!;

  return (
    <section
      style={{
        width: "100%",
        minHeight: 560,
        height: "min(76vh, 820px)",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        border: "1px solid #20374b",
        borderRadius: 14,
        background: "#07111d",
        color: "#e8f2ff",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
      }}
    >
      <header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          flexWrap: "wrap",
          padding: "13px 16px",
          borderBottom: "1px solid #20374b",
          background: "linear-gradient(90deg,#0c1d2d,#091421)",
        }}
      >
        <div>
          <div style={{ fontSize: 15, fontWeight: 800, letterSpacing: 1.4 }}>
            LUNAR<span style={{ color: "#39baff" }}>TWIN</span>
          </div>
          <div style={{ marginTop: 3, color: "#8faec9", fontSize: 11 }}>
            TERRAIN INTELLIGENCE WORKSPACE
          </div>
        </div>
        <div style={{ color: "#75cfff", fontSize: 11, border: "1px solid #244963", borderRadius: 20, padding: "7px 10px" }}>
          SOUTH POLAR REGION · DEMO TERRAIN
        </div>
      </header>

      <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
        <aside
          style={{
            width: 218,
            flex: "0 0 218px",
            padding: 13,
            borderRight: "1px solid #20374b",
            background: "#0b1826",
            display: "flex",
            flexDirection: "column",
            gap: 9,
          }}
        >
          <div style={{ fontSize: 13, fontWeight: 750, marginBottom: 2 }}>Scientific Layers</div>
          {LAYERS.map((item) => {
            const active = layer === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setLayer(item.id)}
                title={item.description}
                aria-pressed={active}
                style={{
                  textAlign: "left",
                  display: "flex",
                  alignItems: "center",
                  gap: 9,
                  padding: "10px 9px",
                  borderRadius: 8,
                  border: active ? "1px solid #168ed0" : "1px solid #1c3043",
                  background: active ? "#10314a" : "#0c1d2d",
                  color: active ? "#f3fbff" : "#b5c8d9",
                  cursor: "pointer",
                  fontSize: 12,
                }}
              >
                <span
                  style={{
                    width: 10,
                    height: 10,
                    flex: "0 0 10px",
                    borderRadius: 3,
                    background:
                      item.id === "resource" ? "linear-gradient(90deg,#2923a6,#23d8d0,#ffe44d,#ef3828)" :
                      item.id === "slope" ? "linear-gradient(90deg,#163a93,#31d8cc,#ffb12b)" :
                      item.id === "illumination" ? "linear-gradient(90deg,#202b75,#ffe9a0)" :
                      item.id === "uncertainty" ? "linear-gradient(90deg,#211b6e,#922dca,#ff4d9a)" : "#aeb8c4",
                  }}
                />
                {item.label}
                <span style={{ marginLeft: "auto", color: active ? "#48c7ff" : "#526b80" }}>{active ? "●" : "○"}</span>
              </button>
            );
          })}

          <div style={{ height: 1, background: "#20374b", margin: "5px 0" }} />
          <label style={{ fontSize: 11, color: "#a7bfd3", display: "flex", justifyContent: "space-between" }}>
            Overlay opacity <strong style={{ color: "#5dcaff" }}>{opacity}%</strong>
          </label>
          <input
            type="range"
            min={0}
            max={100}
            value={opacity}
            onChange={(event) => setOpacity(Number(event.target.value))}
            aria-label="Overlay opacity"
            style={{ width: "100%", accentColor: "#28a9f4" }}
          />
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 11, color: "#b7c9d8" }}>
            <input type="checkbox" checked={relief} onChange={(event) => setRelief(event.target.checked)} />
            Enhanced terrain relief
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 11, color: "#b7c9d8" }}>
            <input type="checkbox" checked={showGrid} onChange={(event) => setShowGrid(event.target.checked)} />
            Show reference grid
          </label>
          <button
            type="button"
            onClick={() => setResetToken((value) => value + 1)}
            style={{
              marginTop: "auto",
              padding: "10px 12px",
              border: "1px solid #2a4b65",
              borderRadius: 8,
              background: "#13283a",
              color: "#e5f3ff",
              cursor: "pointer",
              fontSize: 12,
            }}
          >
            Reset 3D view
          </button>
        </aside>

        <div style={{ position: "relative", flex: 1, minWidth: 0, minHeight: 0 }}>
          <div ref={hostRef} style={{ position: "absolute", inset: 0 }} />
          <div style={{ position: "absolute", top: 12, left: 12, pointerEvents: "none", background: "rgba(5,13,23,.82)", border: "1px solid #28445c", borderRadius: 8, padding: "9px 11px" }}>
            <div style={{ color: "#62cfff", fontSize: 10, fontWeight: 800, letterSpacing: 1 }}>3D TERRAIN VIEW</div>
            <div style={{ color: "#b4c8d9", fontSize: 10, marginTop: 3 }}>Drag to rotate · Scroll to zoom · Right-drag to pan</div>
          </div>
          <div style={{ position: "absolute", top: 12, right: 12, pointerEvents: "none", background: "rgba(5,13,23,.82)", border: "1px solid #28445c", borderRadius: 8, padding: "7px 9px", color: "#93b7d4", fontSize: 10 }}>
            {currentLayer.label.toUpperCase()}
          </div>
          <div style={{ position: "absolute", left: 12, bottom: 12, pointerEvents: "none", width: 180, background: "rgba(5,13,23,.9)", border: "1px solid #28445c", borderRadius: 8, padding: 10 }}>
            <div style={{ fontSize: 11, fontWeight: 700, marginBottom: 8 }}>{currentLayer.label} legend</div>
            <div
              style={{
                height: 9,
                borderRadius: 3,
                background:
                  layer === "resource" ? "linear-gradient(90deg,#2923a6,#087be8,#23d8d0,#ffe44d,#ef3828)" :
                  layer === "slope" ? "linear-gradient(90deg,#163a93,#31d8cc,#ffb12b)" :
                  layer === "illumination" ? "linear-gradient(90deg,#202b75,#ffe9a0,#fff)" :
                  layer === "uncertainty" ? "linear-gradient(90deg,#211b6e,#922dca,#ff4d9a)" :
                  "linear-gradient(90deg,#222a39,#888b90,#d4d5d4)",
              }}
            />
            <div style={{ display: "flex", justifyContent: "space-between", color: "#9eb5c9", fontSize: 10, marginTop: 5 }}>
              <span>{layer === "terrain" ? "Low" : "Low"}</span><span>High</span>
            </div>
          </div>
        </div>
      </div>

      <footer style={{ display: "flex", justifyContent: "space-between", gap: 10, flexWrap: "wrap", padding: "10px 15px", borderTop: "1px solid #20374b", background: "#0a1724", color: "#9db6cb", fontSize: 10 }}>
        <span>● Landing site</span>
        <span style={{ color: "#53c9ff" }}>━ Rover path · Waypoints</span>
        <span style={{ color: "#eab34e" }}>Terrain-following demo route</span>
        <span>Procedural preview · Not scientific measurements</span>
      </footer>
    </section>
  );
}
