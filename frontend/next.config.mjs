const nextConfig = {
  output: "standalone",
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
};

export default nextConfig;
