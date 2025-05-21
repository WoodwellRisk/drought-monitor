function onSettingsClick() {
    let sidebarContainer = document.querySelector('#sidebar-container');

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