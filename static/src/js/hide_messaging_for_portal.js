
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
});
