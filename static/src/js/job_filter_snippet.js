/** @odoo-module **/

import publicWidget from 'web.public.widget';

publicWidget.registry.DynamicJobFilterSnippet = publicWidget.Widget.extend({
  selector: '#job_filter_bar',
  events: {
    'click a[data-filter]': '_onFilterClick',
    'click .dropdown-menu a': '_onDropdownSelect',
  },

  _onFilterClick: function (ev) {
    ev.preventDefault();
    const filter = ev.currentTarget.dataset.filter;
    if (filter === 'job') {
      // exemple : redirige vers /jobs ou déclenche une modale de recherche avancée
      window.location.href = '/jobs';
    } else if (filter === 'contract') {
      // peut déclencher une modale ou un menu local
      alert('Filtrage par type de contrat à implémenter.');
    }
  },

  _onDropdownSelect: function (ev) {
    ev.preventDefault();
    const href = ev.currentTarget.getAttribute('href');
    if (href) {
      window.location.href = href;
    }
  },
});
