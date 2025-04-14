odoo.define('website_training.snippet', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.DynamicTrainingSnippet = publicWidget.Widget.extend({
        selector: '#dynamic_training_section',
        start: function () {
            this.currentPage = 1;
            this.loadTrainings();
            this.bindEvents();
        },
        bindEvents: function () {
            this.$('#next_trainings').on('click', () => {
                this.currentPage += 1;
                this.loadTrainings();
            });
            this.$('#prev_trainings').on('click', () => {
                if (this.currentPage > 1) {
                    this.currentPage -= 1;
                    this.loadTrainings();
                }
            });
        },
        loadTrainings: function () {
            const self = this;
            this._rpc({
                route: '/formations/liste',
                params: { page: this.currentPage },
            }).then(function (data) {
                const container = self.$('#training_cards_container');
                container.empty();

                data.trainings.forEach((training) => {
                    const card = $(`
                        <div class="col-md-4 mb-4">
                            <div class="card h-100 shadow-sm">
                                <img class="card-img-top  w-100 h-100" src="data:image/png;base64,${training.header}" alt="${training.name}" style="object-fit: cover; border-top-left-radius: 0.25rem; border-top-right-radius: 0.25rem;"/>
                                <div class="card-body" style="text-align: center;">
                                    <h4 class="card-title text-o-color-2"><strong>${training.name}</strong></h4>
                                    <p class="card-text text-muted small text-600">
                                       <strong> Du ${training.date_start || ''} au ${training.date_end || ''}  </strong>
                                    </p>
                                    <p class="card-text">
                                        <h4>
                                            <strong class="text-o-color-2">${training.cout || ''}$
                                            </strong>
                                        </h4>
                                    </p>
                                </div>
                            </div>
                        </div>
                    `);
                    container.append(card);
                });
            });
        },
    });

    return publicWidget.registry.DynamicTrainingSnippet;
});
