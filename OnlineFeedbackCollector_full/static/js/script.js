async function submitFeedback() {
  const name = document.getElementById('name').value.trim();
  const email = document.getElementById('email').value.trim();
  const rating = document.getElementById('rating').value;
  const comments = document.getElementById('comments').value.trim();
  const msgDiv = document.getElementById('formMsg');

  msgDiv.innerHTML = '';

  if (!name) {
    msgDiv.innerHTML = '<div class="alert alert-warning">Please enter your name.</div>';
    return;
  }
  if (!rating) {
    msgDiv.innerHTML = '<div class="alert alert-warning">Please choose a rating.</div>';
    return;
  }

  const payload = { name, email, rating, comments };

  try {
    const res = await fetch('/submit-feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (res.ok && data.success) {
      msgDiv.innerHTML = '<div class="alert alert-success">' + data.message + '</div>';
      document.getElementById('feedbackForm').reset();
    } else {
      msgDiv.innerHTML = '<div class="alert alert-danger">' + (data.error || 'Submission failed') + '</div>';
    }
  } catch (err) {
    msgDiv.innerHTML = '<div class="alert alert-danger">Network error. Try again later.</div>';
  }
}
