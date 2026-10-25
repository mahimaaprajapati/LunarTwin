"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

/**
 * Procedural lunar terrain viewer.
 *
 * Replace the old Viewer.tsx with this file.
 * Requires: npm install three
 *
 * This version creates a detailed cratered lunar surface procedurally so the
 * viewer works immediately. It does NOT pretend to read your DEM file yet;
 * the DEM loader can be connected once the exact raster format/dimensions are
 * confirmed.
 */
export default function Viewer() {
  const hostRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    } catch {
      host.innerHTML =
        '<div style="padding:24px;color:#e5edf7">WebGL could not start in this browser. Enable hardware acceleration or try another browser.</div>';
      return;
    }

    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#050a12");
    scene.fog = new THREE.Fog("#050a12", 45, 125);

    const camera = new THREE.PerspectiveCamera(43, 1, 0.1, 300);
    camera.position.set(0, 21, 32);

    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    renderer.domElement.style.display = "block";
    renderer.domElement.style.width = "100%";
    renderer.domElement.style.height = "100%";
    renderer.domElement.style.outline = "none";
    host.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 1.2, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 12;
    controls.maxDistance = 75;
    controls.maxPolarAngle = Math.PI * 0.49;
    controls.rotateSpeed = 0.55;
    controls.zoomSpeed = 0.8;
    controls.panSpeed = 0.65;

    scene.add(new THREE.HemisphereLight("#b8d5ff", "#171923", 1.25));
    const sun = new THREE.DirectionalLight("#fff1dc", 3.2);
    sun.position.set(-18, 28, 12);
    scene.add(sun);
    const blueFill = new THREE.DirectionalLight("#477bff", 1.05);
    blueFill.position.set(18, 8, -20);
    scene.add(blueFill);

    // Seeded random makes the terrain stable between renders.
    let seed = 92841;
    const rand = () => {
      seed = (seed * 1664525 + 1013904223) >>> 0;
      return seed / 4294967296;
    };

    type Crater = { x: number; z: number; r: number; depth: number; rim: number };
    const craters: Crater[] = [];
    for (let i = 0; i < 44; i++) {
      const r = 0.55 + Math.pow(rand(), 1.65) * 4.2;
      craters.push({
        x: (rand() - 0.5) * 43,
        z: (rand() - 0.5) * 43,
        r,
        depth: 0.28 + r * (0.12 + rand() * 0.1),
        rim: 0.12 + r * 0.045,
      });
    }
    // A few larger, recognizable craters in the foreground.
    craters.push(
      { x: -7.5, z: 5.5, r: 5.4, depth: 1.55, rim: 0.72 },
      { x: 5.8, z: -4.5, r: 3.1, depth: 0.9, rim: 0.48 },
      { x: 1.2, z: 7.6, r: 2.0, depth: 0.58, rim: 0.34 },
      { x: 10.2, z: 4.5, r: 1.65, depth: 0.48, rim: 0.28 },
      { x: -1.0, z: -8.0, r: 2.4, depth: 0.72, rim: 0.38 }
    );

    const size = 180;
    const segments = 260;
    const geometry = new THREE.PlaneGeometry(size, size, segments, segments);
    geometry.rotateX(-Math.PI / 2);

    const positions = geometry.attributes.position as THREE.BufferAttribute;
    const colors: number[] = [];
    const color = new THREE.Color();
    const baseColor = new THREE.Color("#777b80");
    const highColor = new THREE.Color("#b9b9b5");
    const shadowColor = new THREE.Color("#252b35");
    const lowColor = new THREE.Color("#3331a8");
    const midColor = new THREE.Color("#06a9e8");
    const hotColor = new THREE.Color("#ffb82e");

    // Multi-frequency terrain plus bowl/rim profiles for each impact crater.
    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i);
      const z = positions.getZ(i);
      const radial = Math.sqrt(x * x + z * z);

      let y =
        0.34 * Math.sin(x * 0.18 + Math.sin(z * 0.12)) +
        0.26 * Math.cos(z * 0.22) +
        0.12 * Math.sin((x + z) * 0.72) +
        0.075 * Math.cos(x * 1.25 - z * 0.91) +
        0.035 * Math.sin(x * 2.3 + z * 1.8);

      for (const c of craters) {
        const dx = x - c.x;
        const dz = z - c.z;
        const d = Math.sqrt(dx * dx + dz * dz);
        const q = d / c.r;
        if (q < 1.65) {
          // Smooth bowl, raised ejecta rim and a faint outer ejecta blanket.
          const bowl = -c.depth * Math.exp(-Math.pow(q / 0.72, 2) * 1.65);
          const rim = c.rim * Math.exp(-Math.pow((q - 0.94) / 0.13, 2));
          const ejecta =
            0.1 * c.depth * Math.exp(-Math.pow((q - 1.18) / 0.3, 2));
          y += bowl + rim + ejecta;
        }
      }

      // Gently taper the edges so the terrain fades into the dark scene
      // instead of reading as a flat-sided grey tile.
      const edge = Math.max(0, Math.min(1, (radial - 62) / 22));
      y *= 1 - edge * 0.9;
      y += (rand() - 0.5) * 0.018;
      positions.setY(i, y);

      // A simulated resource-potential overlay: cool colors in lows,
      // warmer colors on selected mineral-prospecting bands.
      const prospect =
        0.5 +
        0.24 * Math.sin(x * 0.17 + z * 0.1) +
        0.18 * Math.cos(z * 0.21 - x * 0.08) +
        0.1 * Math.sin((x - z) * 0.34);
      if (prospect < 0.34) {
        color.copy(shadowColor).lerp(lowColor, 0.78);
      } else if (prospect < 0.54) {
        color.copy(lowColor).lerp(midColor, (prospect - 0.34) / 0.2);
      } else if (prospect < 0.76) {
        color.copy(midColor).lerp(new THREE.Color("#35e3b0"), (prospect - 0.54) / 0.22);
      } else {
        color.copy(hotColor).lerp(new THREE.Color("#ff4a25"), (prospect - 0.76) / 0.24);
      }

      // Use a restrained grey lunar base with the heatmap blended in.
      const overlayStrength = 0.68;
      color.lerp(baseColor, 1 - overlayStrength);
      const elevationMix = THREE.MathUtils.clamp((y + 2.0) / 4.5, 0, 1);
      color.lerp(highColor, elevationMix * 0.24);
      colors.push(color.r, color.g, color.b);
    }

    geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
    geometry.computeVertexNormals();

    const terrainMaterial = new THREE.MeshStandardMaterial({
      vertexColors: true,
      roughness: 1,
      metalness: 0,
      flatShading: false,
    });
    const terrain = new THREE.Mesh(geometry, terrainMaterial);
    terrain.position.y = -0.45;
    terrain.receiveShadow = true;
    scene.add(terrain);

    // Tiny rock clusters add texture at a distance without a heavy asset pack.
    const rockGeometry = new THREE.IcosahedronGeometry(0.12, 0);
    const rockMaterial = new THREE.MeshStandardMaterial({
      color: "#777a80",
      roughness: 1,
    });
    const rocks = new THREE.InstancedMesh(rockGeometry, rockMaterial, 650);
    const dummy = new THREE.Object3D();
    for (let i = 0; i < 650; i++) {
      const x = (rand() - 0.5) * 72;
      const z = (rand() - 0.5) * 72;
      let y =
        0.34 * Math.sin(x * 0.18 + Math.sin(z * 0.12)) +
        0.26 * Math.cos(z * 0.22) +
        0.12 * Math.sin((x + z) * 0.72);
      for (const c of craters) {
        const d = Math.hypot(x - c.x, z - c.z);
        const q = d / c.r;
        if (q < 1.65) {
          y +=
            -c.depth * Math.exp(-Math.pow(q / 0.72, 2) * 1.65) +
            c.rim * Math.exp(-Math.pow((q - 0.94) / 0.13, 2));
        }
      }
      dummy.position.set(x, y + 0.02, z);
      const s = 0.25 + rand() * 1.7;
      dummy.scale.set(s, 0.35 + rand() * 0.7, s);
      dummy.rotation.set(rand() * 2, rand() * 2, rand() * 2);
      dummy.updateMatrix();
      rocks.setMatrixAt(i, dummy.matrix);
    }
    scene.add(rocks);

    // A planned rover route with glowing waypoint markers.
    const routePoints = [
      new THREE.Vector3(13, 0.9, 18),
      new THREE.Vector3(10, 0.82, 13),
      new THREE.Vector3(8, 0.85, 9),
      new THREE.Vector3(5.8, 0.9, 5.4),
      new THREE.Vector3(3.4, 0.9, 2.0),
      new THREE.Vector3(1.0, 0.95, -1.0),
      new THREE.Vector3(-1.2, 1.0, -4.0),
      new THREE.Vector3(-3.4, 1.05, -7.2),
      new THREE.Vector3(-5.6, 1.05, -10.0),
    ];
    const routeCurve = new THREE.CatmullRomCurve3(routePoints);
    const routeGeometry = new THREE.TubeGeometry(routeCurve, 150, 0.075, 8, false);
    const routeMaterial = new THREE.MeshBasicMaterial({ color: "#e7faff" });
    const route = new THREE.Mesh(routeGeometry, routeMaterial);
    scene.add(route);

    const waypointMaterial = new THREE.MeshStandardMaterial({
      color: "#31c9ff",
      emissive: "#087dbb",
      emissiveIntensity: 1.5,
      roughness: 0.3,
    });
    const waypointGeometry = new THREE.SphereGeometry(0.28, 16, 12);
    for (const p of routePoints.slice(1, -1)) {
      const marker = new THREE.Mesh(waypointGeometry, waypointMaterial);
      marker.position.copy(p);
      marker.position.y += 0.05;
      scene.add(marker);
    }

    // Landing pin: a red beacon above the selected destination.
    const landing = new THREE.Group();
    const pinStem = new THREE.Mesh(
      new THREE.CylinderGeometry(0.055, 0.055, 1.1, 10),
      new THREE.MeshStandardMaterial({ color: "#f5f7fb", metalness: 0.15, roughness: 0.5 })
    );
    pinStem.position.y = 0.55;
    landing.add(pinStem);
    const pinHead = new THREE.Mesh(
      new THREE.SphereGeometry(0.34, 20, 16),
      new THREE.MeshStandardMaterial({
        color: "#ff665e",
        emissive: "#b51c28",
        emissiveIntensity: 0.65,
      })
    );
    pinHead.position.y = 1.22;
    landing.add(pinHead);
    landing.position.set(-5.6, 0.15, -10);
    scene.add(landing);

    // Simple rover body, wheels and mast.
    const rover = new THREE.Group();
    const body = new THREE.Mesh(
      new THREE.BoxGeometry(1.35, 0.38, 0.92),
      new THREE.MeshStandardMaterial({ color: "#d9b36a", metalness: 0.35, roughness: 0.55 })
    );
    body.position.y = 0.68;
    rover.add(body);
    const deck = new THREE.Mesh(
      new THREE.BoxGeometry(0.8, 0.1, 0.62),
      new THREE.MeshStandardMaterial({ color: "#8fa5b5", metalness: 0.4, roughness: 0.4 })
    );
    deck.position.y = 0.93;
    rover.add(deck);
    const wheelMaterial = new THREE.MeshStandardMaterial({ color: "#20252b", roughness: 0.95 });
    for (const x of [-0.55, 0.55]) {
      for (const z of [-0.48, 0.48]) {
        const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.15, 12), wheelMaterial);
        wheel.rotation.z = Math.PI / 2;
        wheel.position.set(x, 0.35, z);
        rover.add(wheel);
      }
    }
    const mast = new THREE.Mesh(
      new THREE.CylinderGeometry(0.045, 0.045, 0.62, 8),
      new THREE.MeshStandardMaterial({ color: "#b9c6d2", metalness: 0.4 })
    );
    mast.position.set(0.25, 1.25, -0.12);
    rover.add(mast);
    const cameraHead = new THREE.Mesh(
      new THREE.BoxGeometry(0.32, 0.22, 0.24),
      new THREE.MeshStandardMaterial({ color: "#2ca9ed", metalness: 0.45, roughness: 0.3 })
    );
    cameraHead.position.set(0.25, 1.58, -0.12);
    rover.add(cameraHead);
    rover.position.set(13, -0.2, 18);
    rover.rotation.y = -0.65;
    scene.add(rover);

    // Stars in the sky/background.
    const starPositions: number[] = [];
    for (let i = 0; i < 950; i++) {
      starPositions.push((rand() - 0.5) * 220, 15 + rand() * 90, (rand() - 0.5) * 220);
    }
    const starGeometry = new THREE.BufferGeometry();
    starGeometry.setAttribute("position", new THREE.Float32BufferAttribute(starPositions, 3));
    const stars = new THREE.Points(
      starGeometry,
      new THREE.PointsMaterial({ color: "#8eaccd", size: 0.12, transparent: true, opacity: 0.7 })
    );
    scene.add(stars);

    const resize = () => {
      if (!host) return;
      const width = Math.max(1, host.clientWidth);
      const height = Math.max(1, host.clientHeight);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height, false);
    };
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(host);
    resize();

    let frame = 0;
    let animationId = 0;
    const animate = () => {
      animationId = requestAnimationFrame(animate);
      controls.update();
      // Subtle beacon pulse, without moving the terrain or route.
      const pulse = 1 + Math.sin(performance.now() * 0.004) * 0.07;
      pinHead.scale.setScalar(pulse);
      renderer.render(scene, camera);
      frame++;
    };
    animate();

    return () => {
      cancelAnimationFrame(animationId);
      resizeObserver.disconnect();
      controls.dispose();
      geometry.dispose();
      terrainMaterial.dispose();
      rockGeometry.dispose();
      rockMaterial.dispose();
      routeGeometry.dispose();
      routeMaterial.dispose();
      waypointGeometry.dispose();
      waypointMaterial.dispose();
      renderer.dispose();
      if (renderer.domElement.parentElement === host) host.removeChild(renderer.domElement);
      // Dispose remaining scene geometries/materials.
      scene.traverse((object) => {
        if (object instanceof THREE.Mesh || object instanceof THREE.InstancedMesh) {
          object.geometry?.dispose();
          const materials = Array.isArray(object.material) ? object.material : [object.material];
          materials.forEach((material) => material.dispose());
        }
      });
    };
  }, []);

  return (
    <div
      ref={hostRef}
      aria-label="Interactive 3D lunar terrain"
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        minHeight: 480,
        overflow: "hidden",
        borderRadius: 10,
        background: "#050a12",
        cursor: "grab",
      }}
    >
      <div
        style={{
          position: "absolute",
          zIndex: 2,
          left: 14,
          top: 14,
          padding: "10px 13px",
          border: "1px solid rgba(133,177,218,.28)",
          borderRadius: 8,
          background: "rgba(5,12,22,.78)",
          color: "#eaf3ff",
          font: "600 12px/1.5 system-ui, sans-serif",
          pointerEvents: "none",
          backdropFilter: "blur(8px)",
        }}
      >
        <div style={{ letterSpacing: 1.2, color: "#60c8ff" }}>LUNARTWIN / TERRAIN VIEW</div>
        <div style={{ color: "#a8bdd3", fontWeight: 400 }}>Drag to rotate · Scroll to zoom · Right-drag to pan</div>
      </div>
      <div
        style={{
          position: "absolute",
          zIndex: 2,
          right: 14,
          top: 14,
          padding: "8px 10px",
          borderRadius: 7,
          background: "rgba(5,12,22,.78)",
          color: "#b8d4ed",
          font: "11px system-ui, sans-serif",
          pointerEvents: "none",
        }}
      >
        PROCEDURAL DEM PREVIEW
      </div>
    </div>
  );
}
