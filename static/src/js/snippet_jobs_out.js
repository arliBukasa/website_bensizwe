/** @odoo-module **/

import publicWidget from 'web.public.widget';
console.log("ici avant random")
var DJobsOut = publicWidget.Widget.extend({
    selector: '.s_row_out_jobs',
    read_events: {
        'click [data-url]': '_onCallToAction',
        'click': '_onClickRefresh',

    },

    start() {
        console.log("ici dans random")
        let jobrow = this.el.querySelector('#rows_out_job')
        console.log(this.el)
        console.log(jobrow)
        if (jobrow) {
            this._rpc({
                route: '/jobs_row_out/',
                params: {}
            }).then(data => {
                let html = ``
                let jobs = data
                console.log(" elements fournies : ", jobs)
                data.forEach(jobs => {
                    html += `
                               <div class="s_col_no_bgcolor pt16 pb16 col-lg-2 offset-lg-1" data-original-title="" title="" aria-describedby="tooltip480011">
                                    <div class="card h-100" style="">
                                    <div class="card-body">
                                        <h4 class="card-title">
                                        <span style="font-size: 18px;">
                                            <strong>
                                            <a class="btn btn-primary" href="/jobs/detail/web-developer-1" data-original-title="" title="">
                                                <strong data-original-title="" title="" aria-describedby="tooltip345568">
                                                <span style="font-size: 18px;">Recycling water</span>
                                                </strong>
                                            </a>
                                            </strong>
                                        </span>
                                        </h4>
                                        <div class="s_hr text-left pt0 pb0" data-snippet="s_hr" data-name="Separator">
                                        <hr class="w-100 mx-auto" style="border-top-width: 1px; border-top-style: solid;"/>
                                        </div>
                                        <p class="card-text" data-original-title="" title="" aria-describedby="tooltip272750">
                                        <span class="s_badge badge o_animable" data-name="Badge" data-snippet="s_badge" style="background-color: rgb(0, 255, 0) !important;">CDI</span>
                                        </p>
                                        <p class="card-text">
                                        <span class="fa fa-map-marker"/>
                                        <strong>Goma</strong>
                                        </p>
                                        <p class="card-text">
                                        <span style="font-size: 12px;">
                                            <span class="fa fa-clock-o"/>
                                        Date de debur : 2025-03-01</span>
                                        </p>
                                        <p class="card-text">
                                        <span style="font-size: 12px;">
                                            <span class="fa fa-clock-o"/>
                                            Date de fin : 2025-04-01</span>
                                        </p>
                                        <p class="card-text">
                                        <span style="font-size: 12px;">1 Affectations</span>
                                        </p>
                                    </div>
                                    <div class="card-footer" data-original-title="" title="" aria-describedby="tooltip598031">
                                        <a href="#" class="card-link" data-original-title="" title="" target="_blank">
                                        <font class="text-o-color-1">
                                            <span style="font-size: 12px;">&amp;nbsp;</span>
                                        </font>
                                        <font data-original-title="" title="" aria-describedby="tooltip989997" class="text-o-color-1">
                                            <span style="font-size: 12px;" data-original-title="" title="" aria-describedby="tooltip655007">informations additionelles+</span>
                                        </font>
                                        </a>
                                        <br/>
                                    </div>
                                    </div>
                                </div>
                            `
                })
                jobrow.innerHTML = html
            })
        }
    },
    _onCallToAction: function (ev) {
        ev.preventDefault();
        console.log("============ vous venez de clicker");
        console.log(ev);
    },
    _onClickRefresh: function (ev) {
        ev.preventDefault();
        console.log("============ vous venez de clicker");
        console.log(ev);
    },
});
publicWidget.registry.snippet_jobs_out_rows = DJobsOut
console.log(publicWidget)



export default DJobsOut;

