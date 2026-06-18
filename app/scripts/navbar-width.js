// https://developer.mozilla.org/en-US/docs/Web/API/Window/matchMedia
// 576px is the mobile breakpoint for our app
let mobileSizeMatch = window.matchMedia("(min-width: 576px)");

function updateOrgTitleVisibility(m) {
    let orgTitleContainer = document.querySelector('#org-title');
    if (m.matches) {
        orgTitleContainer.style.display = 'flex';
    } else {
        orgTitleContainer.style.display = 'none';
    }
}

// call method once on page load to set the initial state, then listen for changes
document.addEventListener('DOMContentLoaded', function() {
    updateOrgTitleVisibility(mobileSizeMatch);
    mobileSizeMatch.addEventListener('change', updateOrgTitleVisibility);
});
