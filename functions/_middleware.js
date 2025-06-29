export async function onRequest(context) {
    // Define the username and password
    const USERNAME = "kyle";
    const PASSWORD = "travelagency2024";
    
    // Get the Authorization header
    const authorization = context.request.headers.get("Authorization");
    
    if (!authorization) {
      return new Response("Please enter credentials", {
        status: 401,
        headers: {
          "WWW-Authenticate": 'Basic realm="Proposal Access"'
        }
      });
    }
    
    // Parse the authorization header
    const [scheme, encoded] = authorization.split(' ');
    
    if (scheme !== 'Basic') {
      return new Response("Invalid credentials", { status: 401 });
    }
    
    // Decode credentials
    const decoded = atob(encoded);
    const [username, password] = decoded.split(':');
    
    // Check credentials
    if (username !== USERNAME || password !== PASSWORD) {
      return new Response("Invalid credentials", { status: 401 });
    }
    
    // Allow the request to continue
    return context.next();
  }