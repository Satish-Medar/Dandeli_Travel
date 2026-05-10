const nextConfig = {
  output: "standalone",
  images: {
    deviceSizes: [320, 640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    formats: ["image/avif", "image/webp"],
    minimumCacheTTL: 31536000,
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },
  async rewrites() {
    return {
      beforeFiles: [
        {
          source: "/api/:path*",
          destination: process.env.NEXT_PUBLIC_API_URL
            ? `${process.env.NEXT_PUBLIC_API_URL}/:path*`
            : process.env.PYTHON_API_BASE_URL
              ? `${process.env.PYTHON_API_BASE_URL}/:path*`
              : "http://127.0.0.1:8000/:path*",
        },
      ],
    };
  },
  compress: true,
  reactStrictMode: true,
};

export default nextConfig;
