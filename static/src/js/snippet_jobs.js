
/** @odoo-module **/

import publicWidget from 'web.public.widget';

var DJobs = publicWidget.Widget.extend({
  selector: '.s_row_jobs',
  read_events: {
    'click [data-url]': '_onCallToAction',
    'click': '_onClickRefresh',
  },

  start() {
    if (!document.querySelector('#formationModal')) {
      let modalWrapper = document.createElement('div');
      modalWrapper.innerHTML = `
      <!-- Modal pour les formations -->
      <div class="modal fade" id="formationModal" tabindex="-1" role="dialog" aria-labelledby="formationModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg modal-dialog-centered" role="document">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="formationModalLabel">Détail de la formation</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fermer"></button>
            </div>
            <div class="modal-body" id="formationModalBody">Chargement...</div>
          </div>
        </div>
      </div>`;
      document.body.appendChild(modalWrapper);
    }
    let formatDateDMY=function(dateStr) {
      const date = new Date(dateStr);
      if (isNaN(date)) return ''; // Gérer les erreurs
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      return `${day}/${month}/${year}`;
    }
    let jobrow = this.el.querySelector('#rows_job')
    let formations = this.el.querySelector('#rows_trainning')
    if (jobrow) {
      this._rpc({ route: '/jobs_row/', params: {} }).then(data => {
        let html = ``;
        
        data.forEach(jobs => {
          let dateCloture = new Date(jobs['date_cloture']);
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
          //console.log: dateCloture, today, timeDiff, daysRemaining
          console.log( ` dateCloture: ${dateCloture}`);
          console.log( ` today: ${today}`);
          console.log(` timedif: ${timeDiff}`);
          console.log(` days remaining: ${daysRemaining}`);
          console.log(` badgecolor: ${badgeColor}`);
          html += `
            <a href="${joburl}" class="col-lg-4 pt-0" data-url="${joburl}">                            
              <div class="row pt-0 s_col_no_resize s_col_no_bgcolor no-gutters rounded o_colored_level align-items-start o_cc o_cc2 pt-0" style="height: 130px; background-color: rgb(245, 242, 242) !important;">
                <div class="s_media_list_body col-lg-12" style="padding-top: 0px !important;padding-bottom: 0px !important;">
                  <span class="s_badge badge o_animable" style="background-color:${badgeColor};"><font style="color:rgb(255, 255, 255);">CDI</font></span>
                  <strong><span style="font-size: 22px;">${jobs['name']}</span></strong>
                  <p>
                    <h6 style="font-size:16px;">📍<strong> ${jobs['localisation']}</strong></h6>
                    <h6 style="font-size:14px;">🕒 <strong>Publié le ${jobs['write_date']}</strong></h6>
                    <h6 style="font-size:14px;">🕒<strong>Date de clôture: ${formatDateDMY(jobs['date_cloture'])}</strong></h6>
                  </p>
                  <div class="s_hr text-left pt0 pb8">
                    <hr class="mx-auto w-100" style="border-top: 1px solid rgb(8, 82, 148);" />
                  </div>
                </div>
              </div>
            </a>`;
        });
        jobrow.innerHTML = html;
      });
    }

    if (formations) {
      this._rpc({ route: '/training_row/', params: {} }).then(data => {
        let formationhtml = ``;
        data.forEach(trainings => {
          formationhtml += `
            <a href="/${trainings['url']}" class="col-lg-4"
               data-name="${trainings['name']}"
               data-description="${trainings['description']}"
               data-date-start="${trainings['date_start']}"
               data-date-end="${trainings['date_end']}"
               data-url="${trainings['url']}">                            
              <div class="row s_col_no_resize s_col_no_bgcolor no-gutters o_cc o_cc1 rounded o_colored_level align-items-center">
                <div class="align-self-stretch s_media_list_img_wrapper col-lg-4">
                  <img src="data:image/png;base64,${trainings['header']}" class="s_media_list_img h-100 w-100" loading="lazy" />
                </div>
                <div class="s_media_list_body col-lg-8">
                  <h3><strong><span style="font-size: 24px;">${trainings['name']}</span></strong></h3>
                  <p><strong>Du ${trainings['date_start']} au ${trainings['date_end']}</strong></p>
                  <p><strong><span style="font-size: 24px;"><font class="text-o-color-1">50$</font></span></strong></p>
                </div>
              </div>
            </a>`;
        });
        formations.innerHTML = formationhtml;

        formations.querySelectorAll('a').forEach(el => {
          el.addEventListener('mouseenter', (e) => {
            const trainingData = e.currentTarget.dataset;
            const modalBody = document.querySelector('#formationModalBody');
            modalBody.innerHTML = `
              <h4>${trainingData.name}</h4>
              <p>📅 Du ${trainingData.dateStart} au ${trainingData.dateEnd}</p>
              <p><span class="badge bg-success" style="font-size: 16px;">💵 50$</span></p>
              <p><strong>Description :</strong> ${trainingData.description || 'Non disponible'}</p>
              <a href="${trainingData.url}" class="btn btn-primary mt-3">S'inscrire</a>
            `;
            $('#formationModal').modal('show');
          });
        });
      });
    }
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
