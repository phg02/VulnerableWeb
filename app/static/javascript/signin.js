/* Minimal signin page interactivity */

document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.getElementById('togglePassword');
  var input = document.getElementById('password');
  if (toggle && input) {
    toggle.addEventListener('click', function () {
      input.type = input.type === 'password' ? 'text' : 'password';
    });
  }
});
