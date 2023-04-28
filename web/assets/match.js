// Select the mobile view container
const mobileView = document.querySelector('.mobile-view');

// If mobile view container doesn't exist, stop execution
if (!mobileView) {
    console.error('Mobile view container not found.');
}

// Select the table body rows
const rows = document.querySelectorAll('tbody tr');

// If there are no rows, stop execution
if (rows.length === 0) {
    console.error('No rows found in table body.');
}

// Loop through each row of the table
rows.forEach(row => {
// Create a new card element for each row
const card = document.createElement('div');
card.classList.add('card');

// Loop through each column of the row and add the data to the card
const cells = row.querySelectorAll('td');
cells.forEach(cell => {
  const label = cell.parentElement.querySelector('th').textContent;
  const value = cell.textContent;
  const data = document.createElement('div');
  data.classList.add('data');
  data.innerHTML = `<span class="label">${label}:</span> ${value}`;
  card.appendChild(data);
});

// Add the card to the mobile view container
mobileView.appendChild(card);
});

// If no cards were added to the mobile view container, display an error message
if (mobileView.children.length === 0) {
console.error('No cards added to mobile view container.');
}