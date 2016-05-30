(function($, Backbone, _, app) {
    'use strict';
    
    // BaseView ..
    var TemplateView = Backbone.View.extend({
        targetEl: '',
        templateName: '',
        initialize: function() {
            this.template = _.template($(this.templateName).html());
        },
        render: function() {
            var context = this.getContext()
              , html = this.template(context);
            
            $(this.targetEl, this.$el).html(html);
        },
        getContext: function() {
            return {};
        }
    }),
    
    // ApiServiceView
    
    ApiServiceView = Backbone.View.extend({
        _strips: {},
        survey_token_url: app.conf.apiRoot + 'services/survey/token',
        initialize: function() {
            this._strips = {
                'info': $('#info-strip'), 'creds': $('#creds-strip'),
            };
            this.reset(true);
        },
        events: {
            'click button.set-token': 'setToken',
            'click button.clear-token': 'clearToken',
            'click #creds-strip .close': 'closeStrip',
            'submit #creds-strip form.creds': 'getToken',
            'submit #creds-strip form.token': 'applyToken',
        },
        clearToken: function(event) {
            event.preventDefault();
            var self = this
              , title='Clear Token'
              , message = 'Are you sure you want to clear the token?';
            
            app.$fn.dialog.confirm(title, message, function() {
                $.post(self.survey_token_url, {'value':null})
                    .success($.proxy(self.tokenApplyPass, self))
                    .fail($.proxy(self.displayError, self));
            });
        },
        setToken: function(event) {
            this.reset();
            $(event.currentTarget).attr('disabled', '');
            if (this._strips.creds.hasClass('hide')) {
                $.proxy(this.reset, this);
                this._strips.creds.removeClass('hide');
                $('form.auth', this._strips.creds).validate();
            }
        },
        displayToken: function(data) {
            // remove any existing error display
            $('div.error-display', this._strips.creds).html('');
            
            // display collected token
            $('.token-display', this._strips.creds).removeClass('hide');
            $('.token-value', this._strips.creds).text(data.api_token);
        },
        applyToken: function(event) {
            event.preventDefault();
            var form = $(event.currentTarget)
              , token = $('label.token-value', form).text();
            
            $.post(this.survey_token_url, {'value':token})
                .success($.proxy(this.tokenApplyPass, this))
                .fail($.proxy(this.displayError, this));
        },
        getToken: function(event) {
            event.preventDefault();
            var form = $(event.currentTarget)
              , u = $(':input[name=username]', form).val()
              , p = $(':input[name=password]', form).val()
              , creds = btoa(u + ":" + p);
            $.ajax({
                // hack: prevents browser from using cached credentials from a
                // successful authentication thus api_url is caused to change.
                url: app.conf.survey.authApiRoot,
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("Authorization", "Basic " + creds);
                }
            }).success($.proxy(this.displayToken, this))
              .fail($.proxy(this.displayError, this));
        },
        displayError: function(xhr, status, error) {
            var target = $('div.error-display', this._strips.creds);
            if (error === '')
                error = 'Unable to reach the service end-point.';
            var html = ('<div class="alert alert-danger">' + error + '</div>');
            target.html(html);
        },
        tokenApplyPass: function(data) {
            // remove any existing error display
            $('div.error-display', this._strips.creds).html('');
            $('td.api-token', this._strips.info).text(data.api_token);
            this.reset(true);
        },
        closeStrip: function(event) {
            this.reset(true);
        },
        reset: function(closeCreds) {
            var strip = this._strips.info
              , btnClearToken = $('button.clear-token', strip);
            
            $('button.set-token', strip).removeAttr('disabled');
            if ($('td.api-token', strip).text() === '') {
                // btnClearToken.attr('disabled', '');
            } else {
                // btnClearToken.removeAttr('disabled');
            }
            
            strip = this._strips.creds;
            $('.token-display', strip).addClass('hide');
            if (closeCreds === true) strip.addClass('hide');
            
            $(':input[name=username]', strip).val('');
            $(':input[name=password]', strip).val('');
            $('label.token-value', strip).text('');
        }
    }),
    
    LocalXFormRegion = TemplateView.extend({
        el: '#local',
        targetEl: '.region',
        templateName: '#local-template',
        initialize: function() {
            var self = this;
            TemplateView.prototype.initialize.apply(this, arguments);
            
            // load bootstrapped data
            app.collections.ready.done(function() {
                var data = JSON.parse($('#bootstrap').text());
                app.xforms.reset(_.pluck(data, 'fields'));
                self.render();
                
                // listen for changes
                // TODO: temporary; need to save before displaying successful
                //       updates 
                app.xforms.on('update', $.proxy(self.render, self));
            });
        },
        getContext: function() {
            return {'xforms': app.xforms || null};
        }
    }),
    
    SurveyXFormRegion = TemplateView.extend({
        el: '#survey',
        targetEl: '.region',
        templateName: '#survey-template',
        initialize: function() {
            var self = this;
            TemplateView.prototype.initialize.apply(this, arguments);
            app.collections.ready.done(function() {
                app.surveyXforms.fetch({
                    beforeSend: self.sendAuth,
                    success: $.proxy(self.render, self)
                });
            });
        },
        events: {
            'click button.register': 'registerSelected',
        },
        registerSelected: function() {
            // get selected objects
            var selected = [];
            _.each($(':input[type=checkbox]:checked', this.$el), function(e) {
                selected.push(app.surveyXforms.get($(e).val()));
            })
            
            // TODO: temporary, need proper way to do registration
            app.xforms.add(selected);
        },
        getContext: function() {
            // filter out forms that have already been registered
            // as best as possible
            if (app.xforms) {
                var localObjectIds = app.xforms.pluck('object_id')
                  , diff = [];
                
                _.each(app.surveyXforms.models, function(f) {
                    if (!_.contains(localObjectIds, f.id))
                        diff.push(f);
                })
                app.surveyXforms = new app.collections.SurveyXForms(diff);
            }
            return {'xforms': app.surveyXforms || null};
        },
        sendAuth: function(xhr) {
            xhr.setRequestHeader(
                'Authorization', 
                'Token ' + app.$fn.getCookie('survey_auth_token'));
        }
    }),
    
    AdminXFormView = Backbone.View.extend({
        _regions: null,
        initialize: function() {
            this._regions = {
                'local': new LocalXFormRegion(),
                'survey': new SurveyXFormRegion(),
            }
        },
        render: function() {
            _.each(this._regions, function(r) {
                r.render();
            })
        }
    });
    
    // register views
    app.views.ApiServiceView = ApiServiceView;
    app.views.AdminXFormView = AdminXFormView;
    
})(jQuery, Backbone, _, app);