document.addEventListener('DOMContentLoaded', () => {
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }

  function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
  }

  function fetchPlaceDetails(token, placeId) {
    fetch(`http://127.0.0.1:5000/api/v1/places/${placeId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    })
      .then(response => {
        if (!response.ok) throw new Error(`Failed to fetch details`);
        return response.json();
      })
      .then(data => displayPlaceDetails(data))
      .catch(error => console.error('Error fetching place:', error));
  }

  function displayPlaceDetails(place) {
    const image = document.createElement('img');
    image.src = placeImages[place.title] || 'images/default.jpg';
    image.alt = place.title;
    image.className = 'detail-image';

    const placeDetails = document.getElementById('place-details');
    placeDetails.innerHTML = '';

    const container = document.createElement('div');
    container.className = 'info-container';

    const title = document.createElement('h2');
    title.textContent = place.title;

    const description = document.createElement('p');
    description.innerHTML = `<strong>Description:</strong> ${place.description}`;

    const price = document.createElement('p');
    price.innerHTML = `<strong>Price:</strong> ${place.price} €`;

    const amenities = document.createElement('p');
    const amenityList = place.amenities?.map(a => a.name).join(', ') || 'None';
    amenities.innerHTML = `<strong>Amenities:</strong> ${amenityList}`;

    const reviewSection = document.getElementById('reviews');
    const reviewDiv = document.getElementById('reviews-container');
    const placeDetailsSection = document.getElementById('place-details');
    const mainPage = document.getElementById('review-page');
    reviewDiv.innerHTML = '';

    if (place.reviews.length > 0) {
      reviewSection.style.display = 'block';
      place.reviews.forEach(review => {
        const reviewCard = document.createElement('div');
        reviewCard.className = 'review-card';
        reviewCard.innerHTML = `
          <p><strong>Rating:</strong> ${review.rating} ★</p>
          <p>${review.text}</p>
        `;
        reviewDiv.appendChild(reviewCard);
      });
      placeDetailsSection.classList.remove('centered');
      mainPage.classList.remove('centered');
    } else {
      reviewSection.style.display = 'none';
      mainPage.classList.add('centered');
      placeDetailsSection.classList.add('centered');
    }

    container.appendChild(image);
    container.appendChild(title);
    container.appendChild(description);
    container.appendChild(price);
    container.appendChild(amenities);

    placeDetails.appendChild(container);
  }

  async function submitReview(token, placeId, reviewText, rating) {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/v1/reviews/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          text: reviewText,
          rating: parseInt(rating),
          place_id: placeId
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Review submission failed');
      }

      const newReview = await response.json();

      alert('Review submitted successfully!');
      document.getElementById('review-form').reset();

      const reviewsContainer = document.getElementById('reviews-container');
      const reviewCard = document.createElement('div');
      reviewCard.className = 'review-card';
      reviewCard.innerHTML = `
        <p><strong>Rating:</strong> ${newReview.rating || 'N/A'} ★</p>
        <p>${newReview.text}</p>
      `;
      reviewsContainer.appendChild(reviewCard);

      const reviewSection = document.getElementById('reviews');
      reviewSection.style.display = 'block';
      document.getElementById('place-details').classList.remove('centered');
    } catch (error) {
      console.error('Error submitting review:', error);
      alert(`Error: ${error.message}`);
    }
  }

  const placeImages = {
    "White Apartment": "images/appartments/appartement-blanc.jpg",
    "Cozy Apartment": "images/appartments/appartement-chaleureux.jpg",
    "Bright Apartment": "images/appartments/appartement-lumineux.jpg",
    "Simple Apartment": "images/appartments/appartement-simple.jpg",
    "House with Pool": "images/appartments/maison-piscine.jpg",
    "Penthouse": "images/appartments/penthouse.jpg",
    "Forest Cottage": "images/appartments/gite-foret.jpg",
    "Camper Van": "images/appartments/camping-car.jpg",
    "Unusual House": "images/appartments/maison-atypique.jpg"
  };

  const token = getCookie('token');
  const placeId = getPlaceIdFromURL();
  const addReviewSection = document.getElementById('add-review');
  const loginLink = document.getElementById('login-link');
  const logoutButton = document.getElementById("logout-button");

  if (token) {
    loginLink.style.display = 'none';
    logoutButton.style.display = 'inline';
    addReviewSection.style.display = 'block';
    sessionStorage.setItem('wasLoggedIn', 'true');
  } else {
    loginLink.style.display = 'inline';
    logoutButton.style.display = 'none';
    addReviewSection.style.display = 'none';
    if (sessionStorage.getItem('wasLoggedIn') === 'true') {
      sessionStorage.removeItem('wasLoggedIn');
      window.location.href = 'index.html';
    }
  }

  if (logoutButton) {
    logoutButton.addEventListener("click", (e) => {
      e.preventDefault();
      document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      sessionStorage.removeItem('wasLoggedIn');
      window.location.href = "login.html";
    });
  }

  if (placeId) {
    fetchPlaceDetails(token, placeId);
  }

  const reviewForm = document.getElementById('review-form');
  if (reviewForm) {
    reviewForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const reviewText = document.getElementById('review-text').value.trim();
      const rating = document.getElementById('review-rating').value;

      if (!reviewText || !rating) {
        alert('Please fill in all fields before submitting.');
        return;
      }

      if (token && placeId) {
        submitReview(token, placeId, reviewText, rating);
      }
    });
  }
});
