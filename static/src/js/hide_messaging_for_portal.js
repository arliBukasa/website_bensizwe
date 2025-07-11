
odoo.define('website_bensizwe.hide_messaging_for_portal', function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');

    publicWidget.registry.HideMessaging = publicWidget.Widget.extend({
        start: function () {
            if (odoo.session_info.user_groups.includes('base.group_portal')) {
                const discussEl = document.querySelector('.o_MessagingMenu');
                if (discussEl) {
                    discussEl.remove();
                }
            }
            return this._super.apply(this, arguments);
        },
    });

    return publicWidget.registry.HideMessaging;

        /**
     * JavaScript pour l'espace utilisateur moderne
     * Gestion des interactions, preview d'avatar, smooth scroll, etc.
     */
    
    document.addEventListener('DOMContentLoaded', function() {
        
        // ===================================
        // GESTION DE L'UPLOAD D'AVATAR
        // ===================================
        
        const avatarInput = document.getElementById('avatar_upload');
        const avatarPreview = document.querySelector('.avatar-preview');
        const avatarImg = document.querySelector('.avatar');
        
        if (avatarInput) {
            avatarInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        showAvatarPreview(e.target.result);
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
        
        function showAvatarPreview(imageSrc) {
            if (avatarPreview) {
                const previewImg = avatarPreview.querySelector('.preview-image');
                if (previewImg) {
                    previewImg.src = imageSrc;
                }
                avatarPreview.classList.add('show');
            }
        }
        
        // Boutons de confirmation/annulation pour l'avatar
        const confirmAvatarBtn = document.querySelector('.btn-confirm');
        const cancelAvatarBtn = document.querySelector('.btn-cancel');
        
        if (confirmAvatarBtn) {
            confirmAvatarBtn.addEventListener('click', function() {
                const previewImg = avatarPreview.querySelector('.preview-image');
                if (avatarImg && previewImg) {
                    avatarImg.src = previewImg.src;
                    avatarImg.style.backgroundImage = 'none';
                }
                avatarPreview.classList.remove('show');
            });
        }
        
        if (cancelAvatarBtn) {
            cancelAvatarBtn.addEventListener('click', function() {
                avatarPreview.classList.remove('show');
                if (avatarInput) {
                    avatarInput.value = '';
                }
            });
        }
        
        // Fermer la preview en cliquant à l'extérieur
        if (avatarPreview) {
            avatarPreview.addEventListener('click', function(e) {
                if (e.target === avatarPreview) {
                    avatarPreview.classList.remove('show');
                }
            });
        }
        
        // ===================================
        // SMOOTH SCROLL POUR LA NAVIGATION
        // ===================================
        
        const navItems = document.querySelectorAll('.nav-item[href^="#"]');
        
        navItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // ===================================
        // ANIMATIONS D'APPARITION
        // ===================================
        
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('slide-in-up');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);
        
        // Observer les éléments à animer
        const elementsToAnimate = document.querySelectorAll(
            '.stat-card, .timeline-item, .nav-item, .form-section'
        );
        
        elementsToAnimate.forEach(el => {
            observer.observe(el);
        });
        
        // ===================================
        // VALIDATION DE FORMULAIRE EN TEMPS RÉEL
        // ===================================
        
        const formInputs = document.querySelectorAll('.form-control');
        
        formInputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
        
        function validateField(field) {
            const value = field.value.trim();
            const fieldType = field.type;
            const isRequired = field.hasAttribute('required');
            
            // Reset classes
            field.classList.remove('is-valid', 'is-invalid');
            
            // Validation basique
            let isValid = true;
            
            if (isRequired && !value) {
                isValid = false;
            } else if (fieldType === 'email' && value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                isValid = emailRegex.test(value);
            } else if (fieldType === 'tel' && value) {
                const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
                isValid = phoneRegex.test(value);
            }
            
            // Appliquer les classes
            if (value && isValid) {
                field.classList.add('is-valid');
            } else if (!isValid) {
                field.classList.add('is-invalid');
            }
            
            return isValid;
        }
        
        // ===================================
        // SOUMISSION DE FORMULAIRE AVEC LOADING
        // ===================================
        
        const profileForm = document.querySelector('.profile-edit-form form');
        
        if (profileForm) {
            profileForm.addEventListener('submit', function(e) {
                // Valider tous les champs
                let allValid = true;
                const requiredFields = this.querySelectorAll('[required]');
                
                requiredFields.forEach(field => {
                    if (!validateField(field)) {
                        allValid = false;
                    }
                });
                
                if (!allValid) {
                    e.preventDefault();
                    showNotification('Veuillez corriger les erreurs dans le formulaire', 'error');
                    return;
                }
                
                // Ajouter l'état de chargement
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enregistrement...';
                }
                
                // Ajouter la classe loading au formulaire
                this.closest('.profile-edit-form').classList.add('loading');
            });
        }
        
        // ===================================
        // SYSTÈME DE NOTIFICATIONS
        // ===================================
        
        function showNotification(message, type = 'info') {
            // Créer l'élément de notification s'il n'existe pas
            let notificationContainer = document.querySelector('.notification-container');
            
            if (!notificationContainer) {
                notificationContainer = document.createElement('div');
                notificationContainer.className = 'notification-container';
                notificationContainer.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    max-width: 400px;
                `;
                document.body.appendChild(notificationContainer);
            }
            
            // Créer la notification
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.style.cssText = `
                background: white;
                border-radius: 8px;
                padding: 1rem 1.5rem;
                margin-bottom: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                border-left: 4px solid ${getNotificationColor(type)};
                animation: slideInRight 0.3s ease-out;
                position: relative;
                cursor: pointer;
            `;
            
            notification.innerHTML = `
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <i class="fas ${getNotificationIcon(type)}" style="color: ${getNotificationColor(type)};"></i>
                    <span>${message}</span>
                    <button onclick="this.parentElement.parentElement.remove()" 
                            style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); 
                                   background: none; border: none; font-size: 1.2rem; cursor: pointer; color: #999;">
                        ×
                    </button>
                </div>
            `;
            
            notificationContainer.appendChild(notification);
            
            // Auto-suppression après 5 secondes
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.style.animation = 'slideOutRight 0.3s ease-in';
                    setTimeout(() => notification.remove(), 300);
                }
            }, 5000);
            
            // Suppression au clic
            notification.addEventListener('click', function() {
                this.remove();
            });
        }
        
        function getNotificationColor(type) {
            const colors = {
                'success': '#28a745',
                'error': '#dc3545',
                'warning': '#ffc107',
                'info': '#04A1D0'
            };
            return colors[type] || colors.info;
        }
        
        function getNotificationIcon(type) {
            const icons = {
                'success': 'fa-check-circle',
                'error': 'fa-exclamation-circle',
                'warning': 'fa-exclamation-triangle',
                'info': 'fa-info-circle'
            };
            return icons[type] || icons.info;
        }
        
        // ===================================
        // ANIMATIONS DE LA TIMELINE
        // ===================================
        
        const timelineItems = document.querySelectorAll('.timeline-item');
        
        timelineItems.forEach((item, index) => {
            // Délai d'animation basé sur l'index
            item.style.animationDelay = `${index * 0.1}s`;
            
            // Effet de hover amélioré
            item.addEventListener('mouseenter', function() {
                this.style.transform = 'translateX(10px)';
                this.style.transition = 'transform 0.3s ease';
            });
            
            item.addEventListener('mouseleave', function() {
                this.style.transform = 'translateX(0)';
            });
        });
        
        // ===================================
        // MISE À JOUR DES STATISTIQUES
        // ===================================
        
        function animateNumber(element, start, end, duration = 1000) {
            const startTime = performance.now();
            
            function updateNumber(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                const current = Math.floor(start + (end - start) * progress);
                element.textContent = current;
                
                if (progress < 1) {
                    requestAnimationFrame(updateNumber);
                }
            }
            
            requestAnimationFrame(updateNumber);
        }
        
        // Animer les nombres au scroll
        const statNumbers = document.querySelectorAll('.stat-number');
        const statsObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const finalNumber = parseInt(element.textContent);
                    element.textContent = '0';
                    animateNumber(element, 0, finalNumber);
                    statsObserver.unobserve(element);
                }
            });
        }, { threshold: 0.5 });
        
        statNumbers.forEach(el => {
            statsObserver.observe(el);
        });
        
        // ===================================
        // RESPONSIVE MENU TOGGLE
        // ===================================
        
        const menuToggle = document.querySelector('.menu-toggle');
        const mobileMenu = document.querySelector('.mobile-menu');
        
        if (menuToggle && mobileMenu) {
            menuToggle.addEventListener('click', function() {
                mobileMenu.classList.toggle('show');
                this.classList.toggle('active');
            });
        }
        
        // ===================================
        // FONCTIONS UTILITAIRES
        // ===================================
        
        // Debounce function pour optimiser les performances
        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
        
        // Fonction pour détecter le support des animations CSS
        function supportsAnimation() {
            const div = document.createElement('div');
            return 'animationName' in div.style;
        }
        
        // Initialiser les tooltips si Bootstrap est disponible
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function(tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
        
        // Log de démarrage
        console.log('✅ User Space JavaScript initialized successfully');
        
    });
    
    // ===================================
    // CSS ANIMATIONS KEYFRAMES (ajouté via JS)
    // ===================================
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(100%);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideOutRight {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100%);
            }
        }
    `;
    document.head.appendChild(style);
});
