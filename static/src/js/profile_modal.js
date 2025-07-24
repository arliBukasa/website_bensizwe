/** @odoo-module **/

import publicWidget from 'web.public.widget';

publicWidget.registry.ProfileModal = publicWidget.Widget.extend({
    selector: '#profileModal',
    read_events: {
        'click [data-url]': '_onClickOpenModal',
        'click [data-url]': '_onClickCloseModal',
        'click': '_onClickCloseModal',

    },
    start: function () {
        var modal = document.getElementById('profileModal');
        var openBtn = document.getElementById('openProfileModal');
        var closeBtn = document.getElementById('closeProfileModal');
        var closeBtn2 = document.getElementById('closeProfileModal2');
        console.log('openBtn', openBtn);
        console.log('modal', modal);
        console.log('closeBtn', closeBtn);
        
       


        if (openBtn) {
            openBtn.onclick = function() {
                modal.style.display = 'block';
            };
        }
        if (closeBtn) {
            closeBtn.onclick = function() {
                modal.style.display = 'none';
            };
        }
        if (closeBtn2) {
            closeBtn2.onclick = function() {
                modal.style.display = 'none';
            };
        }

        return this._super.apply(this, arguments);
    },
}); 