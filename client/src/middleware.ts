import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Note: Since we're using localStorage for token management (client-side only),
// middleware cannot access these tokens. Auth checks are performed in components.
// This middleware is kept minimal and serves as a placeholder for future enhancements.

export function middleware(request: NextRequest) {
  // For now, just pass through all requests
  // Auth checks are handled client-side in the components
  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/auth"],
};

