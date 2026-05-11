let selectedBookId = null;

// Функция загрузки книг с применением фильтров
async function loadBooks(isAdmin = false) {
    const category = document.getElementById('filterCategory')?.value || '';
    const author = document.getElementById('filterAuthor')?.value || '';
    const year = document.getElementById('filterYear')?.value || '';

    let url = `/api/books?category=${category}&author=${author}`;
    if (year) url += `&year=${year}`;

    try {
        const response = await fetch(url);
        const books = await response.json();
        const container = isAdmin ? document.getElementById('admin-book-list') : document.getElementById('book-container');
        
        if (!container) return;
        container.innerHTML = '';

        books.forEach(book => {
            const card = document.createElement('div');
            card.className = 'book-card';
            card.innerHTML = `
                <h3>${book.title}</h3>
                <p><strong>Author:</strong> ${book.author}</p>
                <p><strong>Category:</strong> ${book.category} (${book.year})</p>
                <p><strong>Price:</strong> $${book.price}</p>
                <p>Status: <span class="status-${book.status.toLowerCase()}">${book.status}</span></p>
                ${isAdmin ? 
                    `<button onclick="toggleAvailability(${book.id}, ${!book.availability})" style="background: #666">
                        ${book.availability ? 'Make Unavailable' : 'Make Available'}
                    </button>` : 
                    (book.availability ? 
                        `<button onclick="openRentModal(${book.id})">Rent / Purchase</button>` : 
                        `<button disabled style="background: #ccc">Out of Stock</button>`)
                }
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error("Error loading books:", error);
    }
}

// Функции для аренды
function openRentModal(id) {
    selectedBookId = id;
    document.getElementById('rentModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('rentModal').style.display = 'none';
}

async function confirmRent() {
    const email = document.getElementById('userEmail').value;
    const duration = parseInt(document.getElementById('duration').value);

    if (!email) return alert("Please enter email");

    const response = await fetch('/api/rent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            book_id: selectedBookId,
            duration_weeks: duration,
            user_email: email
        })
    });

    const result = await response.json();
    if (response.ok) {
        alert(result.message);
        closeModal();
        loadBooks(false);
    } else {
        alert(result.detail || "Error occurred");
    }
}

// Функции администратора
async function addBook() {
    const bookData = {
        title: document.getElementById('title').value,
        author: document.getElementById('author').value,
        year: parseInt(document.getElementById('year').value),
        category: document.getElementById('category').value,
        price: parseFloat(document.getElementById('price').value)
    };

    const response = await fetch('/api/books', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bookData)
    });

    if (response.ok) {
        alert("Book added successfully!");
        loadBooks(true);
    }
}

async function toggleAvailability(id, newState) {
    await fetch(`/api/books/${id}?available=${newState}`, { method: 'PATCH' });
    loadBooks(true);
}

async function checkReminders() {
    const response = await fetch('/api/admin/reminders');
    const result = await response.json();
    alert(`System checked! Reminders sent to ${result.reminders_sent} users.`);
}

// Инициализация страниц
document.addEventListener('DOMContentLoaded', () => {
    const isAdminPage = window.location.pathname.includes('admin');
    loadBooks(isAdminPage);
});