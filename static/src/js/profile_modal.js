/** @odoo-module **/

import publicWidget from 'web.public.widget';

publicWidget.registry.ProfileModal = publicWidget.Widget.extend({
    selector: '#profileModal',

    read_events: {
        'click [data-url]': '_onClickOpenModal',  // ⚠️ conflit possible ici, même sélecteur pour 2 méthodes
        'click .o_close_modal': '_onClickCloseModal',
    },

    start: function () {
        var modal = document.getElementById('profileModal');
        var openBtn = document.getElementById('openProfileModal');
        var closeBtn = document.getElementById('closeProfileModal');
        var closeBtn2 = document.getElementById('closeProfileModal2');

        if (openBtn) {
            openBtn.onclick = function () {
                modal.style.display = 'block';
            };
        }
        if (closeBtn) {
            closeBtn.onclick = function () {
                modal.style.display = 'none';
            };
        }
        if (closeBtn2) {
            closeBtn2.onclick = function () {
                modal.style.display = 'none';
            };
        }

        return this._super.apply(this, arguments);
    },

    _onClickOpenModal: function (ev) {
        ev.preventDefault();
        console.log('Open modal clicked');
        var modal = document.getElementById('profileModal');
        if (modal) {
            modal.style.display = 'block';
        }
    },

    _onClickCloseModal: function (ev) {
        ev.preventDefault();
        console.log('Close modal clicked');
        var modal = document.getElementById('profileModal');
        if (modal) {
            modal.style.display = 'none';
        }
    },
});
