window.applyJobFilters = function () {
    const contrat = document.getElementById('filter_contrat').value;
    const localisation = document.getElementById('filter_localisation').value.trim();
    const metier = document.getElementById('filter_metier').value.trim();

    let url = '/jobs';

    const parts = [];

    if (localisation) {
        parts.push('country/' + encodeURIComponent(localisation));
    }

    // PAS de route contract/role dans le contrôleur → on les garde en querystring
    if (contrat) {
        parts.push('?contract=' + encodeURIComponent(contrat));
    }

    if (metier) {
        if (parts.includes('?contract=' + encodeURIComponent(contrat))) {
            parts.push('&metier=' + encodeURIComponent(metier));
        } else {
            parts.push('?metier=' + encodeURIComponent(metier));
        }
    }

    url += parts.length ? '/' + parts.join('') : '';

    window.location.href = url;
};
