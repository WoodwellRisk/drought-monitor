window.onload = function () {
    let tabs = document.querySelectorAll('.nav-item > .nav-link');
    let settingsButton = document.querySelector('#settings_button');
    let sidebarContainer = document.querySelector('#sidebar-container');
    let main = document.querySelector('#main')

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
          if(tab.innerText == 'Historical data') {
            settingsButton.setAttribute('disabled', '');
            sidebarContainer.style.display = 'none';
            main.style.maxWidth = '100%';
          } else{
            settingsButton.removeAttribute('disabled', '');
            main.style.maxWidth = '900px';
            if(window.innerWidth > 576) {
              sidebarContainer.style.display = 'block';
            }
          }
        });
    })

    settingsButton.addEventListener('click', () => {
        if(!settingsButton.disabled) {
            // we need to use window.getComputedStyle(element).display instead of element.style.display
            // because we are using external css, not inline styling
            // https://developer.mozilla.org/en-US/docs/Web/API/Window/getComputedStyle
            let computedStyle = window.getComputedStyle(sidebarContainer).display;

            if (computedStyle == 'none' || computedStyle == '') {
                sidebarContainer.style.display = 'block';
            } else {
                sidebarContainer.style.display = 'none';
            }
        }
    });
}
