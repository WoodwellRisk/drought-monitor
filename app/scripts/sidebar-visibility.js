document.addEventListener('DOMContentLoaded', function () {
  let tabs = document.querySelectorAll('.nav-item > .nav-link');
  let settingsButton = document.querySelector('#settings_button');
  let sidebarContainer = document.querySelector('#sidebar-container');
  let main = document.querySelector('#main')

  tabs.forEach(tab => {
    function setGlobalView(isGlobal) {
      if (isGlobal) {
        settingsButton.setAttribute('disabled', '');
        sidebarContainer.style.display = 'none';
        main.style.maxWidth = '100%';
      } else {
        settingsButton.removeAttribute('disabled');
        main.style.maxWidth = '900px';
        if (window.innerWidth > 576) {
          sidebarContainer.style.display = 'block';
        }
      }
    }

    // user click
    tab.addEventListener('click', () => {
      setGlobalView(tab.innerText === 'Global view');
    });

    // keyboard navigation
    tab.addEventListener('focus', () => {
      setGlobalView(tab.innerText === 'Global view');
    });
  })

  settingsButton.addEventListener('click', () => {
    if (!settingsButton.disabled) {
      let computedStyle = window.getComputedStyle(sidebarContainer).display;

      if (computedStyle == 'none' || computedStyle == '') {
        sidebarContainer.style.display = 'block';
      } else {
        sidebarContainer.style.display = 'none';
      }
    }
  });
});
