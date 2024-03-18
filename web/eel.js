(function() {
    if (!window.eel) {
        console.error("Eel library not loaded! Make sure to include eel.js in your HTML.");
        return;
    }

    function exposeFunctions() {
        window.addEventListener('DOMContentLoaded', function() {
            eel._start();
        });
    }

    exposeFunctions();
})();
