/**
 * Formation Video Player - JavaScript pour les fonctionnalités vidéo
 * Module: website_bensizwe
 * Description: Gestion des vidéos YouTube intégrées avec contrôles personnalisés
 */

(function() {
    'use strict';

    // Fonction pour le mode plein écran
    window.toggleFullscreen = function(button) {
        const videoContainer = button.closest('.video-container');
        const iframe = videoContainer.querySelector('iframe');
        
        if (!document.fullscreenElement) {
            if (videoContainer.requestFullscreen) {
                videoContainer.requestFullscreen();
            } else if (videoContainer.webkitRequestFullscreen) {
                videoContainer.webkitRequestFullscreen();
            } else if (videoContainer.msRequestFullscreen) {
                videoContainer.msRequestFullscreen();
            }
            button.innerHTML = '<i class="fa fa-compress"></i>';
            button.title = 'Quitter le plein écran';
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
            button.innerHTML = '<i class="fa fa-expand"></i>';
            button.title = 'Plein écran';
        }
    };

    // Gestion des événements plein écran
    document.addEventListener('fullscreenchange', function() {
        const buttons = document.querySelectorAll('.video-overlay button');
        buttons.forEach(button => {
            if (!document.fullscreenElement) {
                button.innerHTML = '<i class="fa fa-expand"></i>';
                button.title = 'Plein écran';
            }
        });
    });

    // Optimisation du chargement vidéo
    document.addEventListener('DOMContentLoaded', function() {
        const videoContainers = document.querySelectorAll('.video-container');
        
        // Observer pour charger les vidéos quand elles sont visibles
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const iframe = entry.target.querySelector('iframe');
                    if (iframe && !iframe.src) {
                        iframe.src = iframe.getAttribute('data-src');
                    }
                }
            });
        });

        videoContainers.forEach(container => {
            observer.observe(container);
        });

        // Gestion du responsive pour les vidéos
        function adjustVideoHeight() {
            videoContainers.forEach(container => {
                const iframe = container.querySelector('iframe');
                if (iframe) {
                    const width = container.offsetWidth;
                    const height = (width * 9) / 16; // Ratio 16:9
                    iframe.style.height = Math.min(height, 400) + 'px';
                }
            });
        }

        // Ajuster au chargement et au redimensionnement
        adjustVideoHeight();
        window.addEventListener('resize', adjustVideoHeight);

        // Initialiser les optimisations vidéo
        optimizeVideoPerformance();
    });

    // Fonction pour optimiser les performances
    function optimizeVideoPerformance() {
        const iframes = document.querySelectorAll('.video-container iframe');
        
        iframes.forEach(iframe => {
            // Écouter le chargement de l'iframe
            iframe.addEventListener('load', function() {
                // Masquer l'animation de chargement
                const container = this.closest('.video-container');
                if (container) {
                    container.classList.add('loaded');
                }
            });

            // Ajouter des attributs d'optimisation
            iframe.setAttribute('loading', 'lazy');
            iframe.setAttribute('importance', 'low');
        });
    }

    // Initialiser les optimisations quand le DOM est prêt
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', optimizeVideoPerformance);
    } else {
        optimizeVideoPerformance();
    }

})();