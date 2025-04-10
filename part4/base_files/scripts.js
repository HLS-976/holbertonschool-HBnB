document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');

  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();

      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;

      try {
        const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
          throw new Error("Erreur de connexion");
        }

        const data = await response.json();
        console.log("Connexion réussie");
        document.cookie = `token=${data.access_token}; path=/`;
        window.location.replace('index.html');
      } catch (error) {
        console.error('Erreur :', error.message);
        alert('Login error: ' + error.message);
      }
    });
  }

  function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');

    if (!loginLink) return; // Sécurité

    if (!token) {
      loginLink.style.display = 'inline';
    } else {
      loginLink.style.display = 'none';
      fetchPlaces(token); // à définir ailleurs
    }
  }

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
      return parts.pop().split(';').shift();
    }
    return null;
  }

  checkAuthentication();
});
