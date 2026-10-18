
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      cesium: require.resolve("cesium"),
    };
    return config;
  },
};

export default nextConfig;