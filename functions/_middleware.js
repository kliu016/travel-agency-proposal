export async function onRequest(context) {
    const url = new URL(context.request.url);
    
    // Allow access to login page
    if (url.pathname === '/login.html') {
      return context.next();
    }
    
    // Check for auth cookie
    const cookie = context.request.headers.get('Cookie');
    const isAuthenticated = cookie && cookie.includes('auth=valid');
    
    if (!isAuthenticated) {
      return Response.redirect(`${url.origin}/login.html`, 302);
    }
    
    return context.next();
  }
  
  export async function onRequestPost(context) {
    const url = new URL(context.request.url);
    
    if (url.pathname === '/api/login') {
      const formData = await context.request.formData();
      const username = formData.get('username');
      const password = formData.get('password');
      
      if (username === 'kyle' && password === 'TravelAgency2024') {
        return new Response('Success', {
          status: 200,
          headers: {
            'Set-Cookie': 'auth=valid; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=86400'
          }
        });
      }
      
      return new Response('Invalid credentials', { status: 401 });
    }
  }