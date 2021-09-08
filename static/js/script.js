document.addEventListener('DOMContentLoaded', function() {
  var menu = document.querySelectorAll('.sidenav');
  var instances = M.Sidenav.init(menu, {edge: 'right'});
});

document.addEventListener('DOMContentLoaded', function() {
  var modal = document.querySelectorAll('.modal');
  var instances = M.Modal.init(modal, {});
});
