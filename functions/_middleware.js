// functions/_middleware.js

export async function onRequest(context) {
    const url = new URL(context.request.url);
    
    // List of paths that don't require authentication
    const publicPaths = ['/login.html', '/login'];
    
    // Check if current path is public
    if (publicPaths.includes(url.pathname)) {
      return context.next();
    }
    
    // Check for auth cookie
    const cookie = context.request.headers.get('Cookie') || '';
    const isAuthenticated = cookie.includes('auth=valid');
    
    // If not authenticated and not on login page, redirect to login
    if (!isAuthenticated) {
      // Avoid redirect loop by checking if we're already going to login
      if (!url.pathname.includes('login')) {
        return Response.redirect(`${url.origin}/login.html`, 302);
      }
    }
    
    // Continue to the requested page
    return context.next();
  }
  
  // Handle POST requests separately
  export async function onRequestPost(context) {
    const url = new URL(context.request.url);
    
    // Handle login endpoint
    if (url.pathname === '/api/login') {
      try {
        const formData = await context.request.formData();
        const username = formData.get('username');
        const password = formData.get('password');
        
        // Check credentials
        if (username === 'kyle' && password === 'TravelAgency2024') {
          // Create successful response with auth cookie
          return new Response(JSON.stringify({ success: true }), {
            status: 200,
            headers: {
              'Content-Type': 'application/json',
              'Set-Cookie': 'auth=valid; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=86400' // Changed to Lax for better compatibility
            }
          });
        } else {
          // Invalid credentials
          return new Response(JSON.stringify({ success: false, error: 'Invalid credentials' }), {
            status: 401,
            headers: {
              'Content-Type': 'application/json'
            }
          });
        }
      } catch (error) {
        // Error handling
        return new Response(JSON.stringify({ success: false, error: 'Server error' }), {
          status: 500,
          headers: {
            'Content-Type': 'application/json'
          }
        });
      }
    }
    
    // For other POST requests, continue normally
    return context.next();
  }