/** @odoo-module **/

import publicWidget from 'web.public.widget';

var DJobs = publicWidget.Widget.extend({
  selector: '.s_row_jobs',
  read_events: {
    'click [data-url]': '_onCallToAction',
    'click': '_onClickRefresh',
    'click .pagination a': '_onPaginationClick',
  },

  start() {
    this.currentPage = 1;
    this.jobsPerPage = 12;
    this.totalJobs = 0;
    this.totalPages = 0;
    this._loadJobs();
    this._loadTrainings();
  },

  _loadJobs(page = 1) {
    let jobrow = this.el.querySelector('#rows_job');
    if (!jobrow) return;

    this._rpc({
      route: '/jobs_row/',
      params: {}
    }).then(data => {
      this.totalJobs = data.length;
      this.totalPages = Math.ceil(data.length / this.jobsPerPage);
      const start = (page - 1) * this.jobsPerPage;
      const end = start + this.jobsPerPage;
      const jobsToDisplay = data.slice(start, end);

      let html = ``;
      let formatDateDMY = function (dateStr) {
        const date = new Date(dateStr);
        if (isNaN(date)) return '';
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
      };

      jobsToDisplay.forEach(jobs => {
        const dateCloture = new Date(jobs['date_cloture']);
        let today = new Date();
        let timeDiff = dateCloture - today;
        let daysRemaining = Math.ceil(timeDiff / (1000 * 3600 * 24));
        let joburl = jobs['url'];
        let badgeColor = 'rgb(3, 252, 20)';
        if (daysRemaining < 0) {
          badgeColor = 'red';
          joburl = '#';
        } else if (daysRemaining <= 7) {
          badgeColor = 'orange';
        }

        html += `
          <a href="${joburl}" class="d-block w-100" data-url="${joburl}" style="margin: 15px; padding: 0;margin-bottom: 10px;">
            <div class="row s_col_no_resize s_col_no_bgcolor no-gutters rounded o_colored_level align-items-start o_cc o_cc2"
                style="background-color: rgb(251, 251, 251); border: none; border-bottom: 2px solid rgb(69, 163, 245); padding: 8px 0;">
              <div class="s_media_list_body col-12 custom-job-card " style="padding: 0;padding-left: 5px;">
                <h6 style="font-size: 22px;">
                  <span class="s_badge badge o_animable" style="background-color:${badgeColor};">
                    <font style="color:#fff;">${(jobs['duree_contrat'] || '').toUpperCase()}</font>
                  </span>
                  <strong><span style="font-size: 20px;">${jobs['name']}</span></strong>
                </h6>
                <p class="detail_post">
                  <h6>
                    <div class="d-flex justify-content-between small mt-1 detail_post" id="job_time_location">
                      <strong><span style="font-size:16px;"><img src="/website_bensizwe/static/src/img/icons/location-dot-solid.svg" width="12" style="margin-right:4px;"/>${jobs['localisation']}</span></strong>
                      <strong><span style="font-size:14px;"><img src="/website_bensizwe/static/src/img/icons/clock-regular.svg" width="12" style="margin-right:4px;"/> Publié le ${jobs['write_date']}</span></strong>
                      <strong><span style="font-size:14px;"><img src="/website_bensizwe/static/src/img/icons/clock-regular.svg" width="12" style="margin-right:4px;"/> Échéance: ${formatDateDMY(jobs['date_cloture'])}</span></strong>
                    </div>
                  </h6>
                </p>
              </div>
            </div>
          </a>`;
      });
      jobrow.innerHTML = html;
      this._renderPagination();
    });
  },

  _renderPagination() {
    const container = this.el.querySelector('#pagination_container');
    const pagesWrapper = this.el.querySelector('#pagination-pages');
    if (!container || !pagesWrapper) return;

    pagesWrapper.innerHTML = `
      <li class="page-item"><a class="page-link" href="#" data-page="first"><strong>«</strong></a></li>
      <li class="page-item"><a class="page-link" href="#" data-page="prev"><strong>‹</strong></a></li>
    `;

    for (let i = 1; i <= this.totalPages; i++) {
      pagesWrapper.innerHTML += `<li class="page-item ${i === this.currentPage ? 'active' : ''}"><a class="page-link" href="#" data-page="${i}"><strong>${i}</strong></a></li>`;
    }

    pagesWrapper.innerHTML += `
      <li class="page-item"><a class="page-link" href="#" data-page="next">›</a></li>
      <li class="page-item"><a class="page-link" href="#" data-page="last">»</a></li>
    `;
  },

  _onPaginationClick: function (ev) {
    ev.preventDefault();
    const target = ev.currentTarget;
    let page = target.dataset.page;

    if (page === 'prev') this.currentPage = Math.max(1, this.currentPage - 1);
    else if (page === 'next') this.currentPage = Math.min(this.totalPages, this.currentPage + 1);
    else if (page === 'first') this.currentPage = 1;
    else if (page === 'last') this.currentPage = this.totalPages;
    else this.currentPage = parseInt(page);

    this._loadJobs(this.currentPage);
  },

  _loadTrainings() {
    let formations = this.el.querySelector('#rows_trainning');
    if (!formations) return;

    this._rpc({ route: '/training_row/', params: {} }).then(data => {
      let formationhtml = ``;
      data.forEach(trainings => {
        formationhtml += `
          <a href="/${trainings['url']}" class="col-lg-4"
            data-name="${trainings['name']}"
            data-date-start="${trainings['date_start']}"
            data-date-end="${trainings['date_end']}"
            data-url="${trainings['url']}">
            <div class="row s_col_no_resize s_col_no_bgcolor no-gutters o_cc o_cc1 rounded o_colored_level align-items-top" style="background-color: rgb(251, 251, 251); border: none; border-bottom: 2px solid rgb(69, 163, 245); padding: 0px 0;align-items:top !important;margin:15px;">
              <div class="align-self-stretch s_media_list_img_wrapper col-lg-3" style ="">
                <img src="data:image/png;base64,${trainings['header']}" class="s_media_list_img w-100 h-auto" loading="lazy" style =""/>
              </div>
              <div class="col-lg-8 tranning-time" style="items-align: top;padding-left: 15px; margin-left: 5px;">
                <p class="" style ="margin-bottom: 0px;padding-top:15px;">
                  <strong><span style="font-size: 20px;color:#444444">${trainings['name']}</span></strong>
                </p>
                <p class="col" style="margin: 0;padding: 0;">
                  <span><strong style="color:#767373">Du ${trainings['date_start']} au ${trainings['date_end']}</strong></span><br/> 
                  <strong><span style="font-size: 24px;"><font class="text-o-color-1">${trainings['cout']}$</font></span></strong>
                </p>
                </p>
              </div>
            </div>
          </a>`;
      });
      formations.innerHTML = formationhtml;
    });
  },

  _onCallToAction: function (ev) {
    ev.preventDefault();
    if (ev.currentTarget.dataset.url) {
      window.location.href = ev.currentTarget.dataset.url;
    }
  },

  _onClickRefresh: function (ev) {
    ev.preventDefault();
    if (ev.target.dataset.url) {
      window.location.href = ev.target.dataset.url;
    }
  },
});

publicWidget.registry.snippet_jobs_rows = DJobs;
export default DJobs;
