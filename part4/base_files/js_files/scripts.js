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
    const logoutButton = document.getElementById('logout-button');
    const filterSelector = document.getElementById('filter');

    if (!loginLink || !logoutButton || !filterSelector) return;

    if (!token) {
      loginLink.style.display = 'inline';
      logoutButton.style.display = 'none';
      filterSelector.style.display = 'none';
      fetchPlaces();
    } else {
      loginLink.style.display = 'none';
      logoutButton.style.display = 'inline';
      filterSelector.style.display = 'block';
      fetchPlaces(token);
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

  const logoutButton = document.getElementById("logout-button");
  if (logoutButton) {
    logoutButton.addEventListener("click", (e) => {
      e.preventDefault();
      document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      sessionStorage.removeItem('wasLoggedIn');
      window.location.href = "login.html";
    });
  }

  checkAuthentication();

  async function fetchPlaces(token = null) {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/v1/places/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const places = await response.json();
      displayPlaces(places);
    } catch (error) {
      console.error('Failed to fetch places:', error);
    }
  }

  const placeImages = [
    "images/appartments/appartement-blanc.jpg",
    "images/appartments/appartement-chaleureux.jpg",
    "images/appartments/appartement-lumineux.jpg",
    "images/appartments/appartement-simple.jpg",
    "images/appartments/maison-piscine.jpg",
    "images/appartments/penthouse.jpg",
    "images/appartments/gite-foret.jpg",
    "images/appartments/camping-car.jpg",
    "images/appartments/maison-atypique.jpg"
  ];

  function displayPlaces(places) {
    const placeList = document.getElementById('places-list');
    placeList.innerHTML = '';

    places.forEach((place, index) => {
      const imageIndex = index % placeImages.length;
      const imageUrl = placeImages[imageIndex];

      const placeCard = document.createElement('div');
      placeCard.className = 'place-card';

      placeCard.innerHTML = `
        <img src="${imageUrl}" alt="place image" class="place-image">
        <h3 class="title-card">${place.title}</h3>
        <p class="price-card"><strong>Price:</strong> ${place.price} €</p>
        <p class="desc-card">${place.description}</p>
        <p class="coord-card">📍 ${place.latitude}, ${place.longitude}</p>
        <a href="place.html?id=${place.id}">
          <button class="details-button">View Details</button>
        </a>
      `;

      placeList.appendChild(placeCard);
    });
  }

  const priceFilter = document.getElementById('price-filter');
  if (priceFilter) {
    priceFilter.addEventListener('change', (event) => {
      const selectedValue = event.target.value;
      const places = document.querySelectorAll('.place-card');

      places.forEach(card => {
        const priceText = card.querySelector('p').textContent;
        const price = parseFloat(priceText.replace(/[^0-9.]/g, ''));

        if (selectedValue === 'all' || price <= parseFloat(selectedValue)) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    });
  }
});
