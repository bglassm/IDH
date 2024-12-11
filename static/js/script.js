document.querySelectorAll('.thumbnail').forEach(thumbnail => {
    thumbnail.addEventListener('click', function() {
        document.querySelector('.thumbnail.active').classList.remove('active');
        this.classList.add('active');
        document.getElementById('large-image').src = this.src;
    });
});
