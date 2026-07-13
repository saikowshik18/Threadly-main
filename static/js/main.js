// Threadly Main JS Operations
document.addEventListener('DOMContentLoaded', () => {
    // Dismiss messages / alerts
    document.querySelectorAll('.alert-close').forEach(button => {
        button.addEventListener('click', () => {
            const alert = button.closest('.alert');
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        });
    });

    // Profile Tab Switcher
    const tabButtons = document.querySelectorAll('.profile-tab-btn');
    const tabContents = document.querySelectorAll('.profile-tab-content');
    if (tabButtons.length > 0) {
        tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabName = btn.dataset.tab;
                
                tabButtons.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                btn.classList.add('active');
                const targetContent = document.getElementById(`tab-${tabName}`);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
            });
        });
    }

    // Initialize Save Buttons
    document.querySelectorAll('.save-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const itemId = btn.dataset.id;
            if (itemId) {
                toggleSaveItem(btn, itemId);
            }
        });
    });
});

// Helper: Get CSRF Cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// AJAX: Toggle Save Item Bookmark
async function toggleSaveItem(btn, itemId) {
    try {
        const response = await fetch(`/save/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });
        
        if (response.status === 403) {
            window.location.href = '/accounts/login/';
            return;
        }

        if (response.ok) {
            const data = await response.json();
            if (data.saved) {
                btn.classList.add('active');
                btn.innerHTML = '<i class="fas fa-bookmark"></i>';
            } else {
                btn.classList.remove('active');
                btn.innerHTML = '<i class="far fa-bookmark"></i>';
            }
        }
    } catch (error) {
        console.error('Error saving item:', error);
    }
}
