// Riths Bistro — main.js

// Sidebar toggle (mobile)
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');
if (sidebarToggle && sidebar) {
  sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('open'));
  document.addEventListener('click', (e) => {
    if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });
}

// Auto-dismiss flash messages after 4s
document.querySelectorAll('.alert').forEach(el => {
  setTimeout(() => {
    const bs = bootstrap.Alert.getOrCreateInstance(el);
    bs.close();
  }, 4000);
});
