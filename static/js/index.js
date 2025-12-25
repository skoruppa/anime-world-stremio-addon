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
