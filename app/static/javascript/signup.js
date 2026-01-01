/* Minimal signup page interactivity */

document.addEventListener('DOMContentLoaded', function () {
  var t1 = document.getElementById('togglePassword');
  var p1 = document.getElementById('password');
  var t2 = document.getElementById('togglePassword2');
  var p2 = document.getElementById('confirm-password');

  function wire(toggle, input) {
    if (toggle && input) {
      toggle.addEventListener('click', function () {
        input.type = input.type === 'password' ? 'text' : 'password';
      });
    }
  }

  wire(t1, p1);
  wire(t2, p2);
});
