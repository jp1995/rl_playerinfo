function toggleData(mmrId) {
    let items = document.querySelectorAll('.mmrdata__item');
    for (let i = 0; i < items.length; i++) {
        items[i].classList.remove('visible');
        items[i].classList.add('hidden');
    }

    document.querySelector('#' + CSS.escape(mmrId)).classList.add('visible');
    document.querySelector('#' + CSS.escape(mmrId)).classList.remove('hidden');

    // Update navbar__select text with selected value
    const selectedValue = mmrId.split('-')[1];
    const navbarButton = document.querySelector('.navbar__select_header');
    navbarButton.textContent = selectedValue;
}

const button = document.querySelector('.navbar__button');
button.addEventListener('click', toggleButton);

function toggleButton() {
    // Update the "Previous" text to the default value
    document.querySelector('.navbar__select_header').textContent = 'Previous';
}

function toggleDropdown() {
    const dropdown = document.querySelector('.dropdown-menu');
    dropdown.classList.toggle('hidden');
}

const navbarButton = document.querySelector('.navbar__button');
const navbarSelect = document.querySelector('.navbar__select');
const dropdownli = document.querySelectorAll('.dropdown-li')

navbarButton.addEventListener('click', () => {
    navbarSelect.classList.remove('active');
    navbarButton.classList.add('active');
});

dropdownli.forEach((dropdownli) => {
    dropdownli.addEventListener('click', (event) => {
        navbarButton.classList.remove('active');
        navbarSelect.classList.add('active');
    });
});


// Set initial active state to the navbar__button
navbarButton.classList.add('active');