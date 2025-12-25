function copy_to_clipboard() {
    /* Get the text field */
    let copyText = document.getElementById("manifest_url");

    /* Select the text field */
    copyText.setSelectionRange(0, copyText.value.length); /* For mobile devices */

    /* Copy the text inside the text field */
    try {
        navigator.clipboard.writeText(copyText.value).then(() => alert("Copied Manifest URL to clipboard"));
    } catch (Exception) {
        try {
            // noinspection JSDeprecatedSymbols
            document.execCommand('copy')
        } catch (Exception) {
            alert("Failed to copy to clipboard");
        }
    }
}

function toggleLanguageSelect() {
    const checkbox = document.getElementById('advancedCheck');
    const languageDiv = document.getElementById('languageSelectDiv');
    
    if (checkbox.checked) {
        languageDiv.style.display = 'block';
        updateManifestUrl();
    } else {
        languageDiv.style.display = 'none';
        updateManifestUrl();
    }
}

function toggleTooltip(event) {
    event.stopPropagation();
    event.preventDefault();
    const icon = event.currentTarget;
    
    // Toggle active state on click
    icon.classList.toggle('active');
    
    // Remove focus to prevent issues on mobile
    icon.blur();
}

// Handle hover events (only on non-touch devices)
const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

document.addEventListener('DOMContentLoaded', function() {
    if (!isTouchDevice) {
        document.querySelectorAll('.info-icon').forEach(icon => {
            icon.addEventListener('mouseenter', function() {
                this.classList.add('active');
            });
            
            icon.addEventListener('mouseleave', function() {
                this.classList.remove('active');
            });
        });
    }
});

document.addEventListener('click', function(event) {
    const tooltips = document.querySelectorAll('.info-icon.active');
    tooltips.forEach(tooltip => {
        if (!tooltip.contains(event.target)) {
            tooltip.classList.remove('active');
        }
    });
});

function updateManifestUrl() {
    const checkbox = document.getElementById('advancedCheck');
    const languageSelect = document.getElementById('languageSelect');
    const manifestInput = document.getElementById('manifest_url');
    const baseUrl = manifestInput.value.replace(/\/(hin|tam|tel|jpn|eng)\/manifest\.json$/, '/manifest.json').replace(/\/manifest\.json$/, '');
    
    if (checkbox.checked) {
        const lang = languageSelect.value;
        manifestInput.value = `${baseUrl}/${lang}/manifest.json`;
    } else {
        manifestInput.value = `${baseUrl}/manifest.json`;
    }
    
    // Update install button
    const installBtn = document.querySelector('.btn-success');
    installBtn.onclick = function() {
        location.href = manifestInput.value.replace(/^https?:\/\//, 'stremio://');
    };
}

function toast() {
    /* Get the snackbar DIV */
    let x = document.getElementById("toast");
    x.show();
}
