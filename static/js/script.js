document.addEventListener('DOMContentLoaded', function() {
  const sidenavs = document.querySelectorAll(".sidenav");
  const sidenavsInstance = M.Sidenav.init(sidenavs, {edge: "right"});
  const selects = document.querySelectorAll("select");
  const selectsInstance = M.FormSelect.init(selects);
  const modals = document.querySelectorAll('.modal');
  const modalInstances = M.Modal.init(modals, {});
});
