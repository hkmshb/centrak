(function($, Backbone, _, app) {
    'use strict';
    
    // BaseView ..
    var TemplateView = Backbone.View.extend({
        innerEl: null,
        templateName: '',
        initialize: function() {
            this.template = _.template($(this.templateName).html());
        },
        
        render: function() {
            var context = this.getContext()
              , html = this.template(context)
              , canvas = this.getCanvas();
            
            canvas.html(html);
            this.$alert = $('.alert');
            this.$alert.addClass('hide').text('');
        },
        
        normDate: function(field_name) {
            return moment(this.xform.get(field_name).$date).format();
        },
        
        getCanvas: function() {
            if (!_.isEmpty(this.innerEl)) {
                if (_.isEmpty(this.$innerEl))
                    this.$innerEl = $(this.innerEl, this.$el);
                return this.$innerEl;
            } else {
                this.$innerEl = null;
                return this.$el;
            }
        },
        
        getContext: function() {
            return {};
        },
        
        showMessage: function(message, tag) {
            if (_.isEmpty(message)) {
                this.$alert.addClass('hide');
            } else {
                this.$alert
                        .removeClass('hide alert-danger alert-success')
                        .addClass('alert-' + tag || 'danger')
                        .text(message);
            }
        }
    }),
    
    
    /*-----------------------------------------------------------------------+
     | API Service View 
     +---------------------------------------------------------------------- */
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
                btnClearToken.attr('disabled', '');
            } else {
                btnClearToken.removeAttr('disabled');
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
                app.xforms.on('update', $.proxy(self.render, self));
            });
        },
        
        registerXForms: function(data, callback) {
            var today = moment().format('YYYY-MM-DD');
            
            _(data).each(function(m) {
                m.set('object_id', m.id);
                m.set('api_url', m.get('url'));
                m.set('date_imported', today);
            });
           
            app.xforms.saveAll(data, function(model, resp, xhr) {
                // update local collection
                app.xforms.add(model);
                
                // propagate success via callback
                callback(model, resp, xhr);
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
        
        excludeXForms: function(data) {
            var targetIds = _(data).pluck('object_id');
            app.surveyXforms.remove(targetIds);
            this.render();
        },
        
        registerSelected: function() {
            // get selected objects
            var selected = [] 
              , entry = null;
            
            _.each($(':input[type=checkbox]:checked', this.$el), function(e) {
                entry = app.surveyXforms.get($(e).val());
                if (entry) {
                    entry = entry.clone();
                    selected.push(entry.clone());
                }
            })
            
            this.mediator.registerLocalXForms(selected);
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
            this._regions.local.mediator = this;
            this._regions.survey.mediator = this;
        },
        
        registerLocalXForms: function(data) {
            var self = this;
            if (data && data.length > 0) {
                this._regions.local.registerXForms(data, function(model, resp, xhr) {
                    if (resp == 'success') {
                        self.excludeSurveyXForms(model);
                    } else {
                        self.displayError(resp);
                    }
                });
            }
        },
        
        excludeSurveyXForms: function(data) {
            if (data && data.length > 0) {
                this._regions.survey.excludeXForms(data);
            }
        },
        displayError: function(message) {
            
        },
        
        render: function() {
            _.each(this._regions, function(r) {
                r.render();
            })
        }
    }),
    
    
    /*-----------------------------------------------------------------------+
    | AdminXForms View 
    +---------------------------------------------------------------------- */
    LocalXFormComponent = TemplateView.extend({
        templateName: '#local-xforms-template',
        initialize: function(){
            var self = this;
            TemplateView.prototype.initialize.apply(this, arguments);
            this.mediator = arguments[0].mediator;
            
            // load bootstrapped data
            app.collections.ready.done(function() {
                if (app.xforms.length === 0) {
                    var data = JSON.parse($('#bootstrap').text());
                    app.xforms.reset(data)
                    self.render();
                }
                
                // listen for changes
                app.xforms.on('update', $.proxy(self.render, self));
            });
        },
        
        register: function(options) {
            var self = this, count = 0
              , today = moment().format()
              , dispatch = function(){
                    count += 1;
                    if (count === options.data.length) {
                        self.render();
                        options.success();
                    }
                };
            
            _(options.data).each(function(m){
                m.set('date_imported', today);
                m.set('object_id', m.get('id'));
                if (_.isEmpty(m.get('description')))
                    m.unset('description');
                
                m.unset('id');
                app.xforms.create(m, {
                    wait: true,
                    success: dispatch,
                    fail: dispatch,
                })
            });
        },
        
        getContext: function() {
            return {'xforms': app.xforms || null};
        }
    }),
    
    
    SurveyXFormComponent = TemplateView.extend({
        templateName: '#survey-xforms-template',
        initialize: function() {
            var self = this;
            TemplateView.prototype.initialize.apply(this, arguments);
            this.mediator = arguments[0].mediator;
            
            // load bootstrapped data
            app.collections.ready.done(function() {
                app.surveyXforms.fetch({
                    beforeSend: self.sendAuth,
                    success: $.proxy(self.render, self),
                });
            });
        },
        
        events: {
            'click button.register': 'registerForms',
        },
        
        registerForms: function() {
            var selected = []
              , entry = null
              , self = this;
            
            _($(':input:checked')).each(function(e) {
                entry = app.surveyXforms.findWhere({id: Number($(e).val())});
                if (!_.isEmpty(entry)) {
                    selected.push(entry.clone());
                }
            });
            
            if (selected.length > 0) {
                this.mediator.registerForms({
                    data: selected,
                    success: $.proxy(self.render, self),
                });
            }
        },
        
        getContext: function() {
            // filter out forms that have already been registered
            if (!_.isEmpty(app.xforms)) {
                var registered = app.xforms.pluck('object_id')
                  , diff = [];
                
                _(app.surveyXforms.models).each(function(m) {
                    if (!_.contains(registered, m.id))
                        diff.push(m);
                });
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
    
    AdminXFormListView = TemplateView.extend({
        _comps: null,
        initialize: function() {
            $('.loading').addClass('hide');
            this._comps = {
                'local': new LocalXFormComponent({el: '#local', mediator: this}),
                'survey': new SurveyXFormComponent({el: '#survey', mediator: this}),
            }
        },
        
        registerForms: function(options){
            this._comps.local.register(options);
        },
        
        render: function() {
            _(this._comps).each(function(c) {
                c.render();
            })
        }
    }),
    
    AdminXFormView = TemplateView.extend({
        innerEl: '#local',
        templateName: '#xform-detail',
        initialize: function(options) {
            TemplateView.prototype.initialize.apply(this, arguments);
            
            // extract referred object
            if (_.isEmpty(app.xforms) || app.xforms.length === 0) {
                this.close();
            } else {
                var q = {object_id: Number(options.object_id)}
                  , f = app.xforms.findWhere(q);
                if (_.isEmpty(f))
                    this.close();
                this.xform = f;
            }
        },
        
        events: {
            'click button.update': 'update',
            'click button.cancel': 'close',
        },
        
        update: function() {
            if (_.isEmpty(this.$type.val())) {
                alert('Type must be specified.');
                return;
            }
            
            var changes = this.getChanges(), self=this;
            this.xform.save(changes, {
                wait: true,
                patch: true,
                success: function(model, resp, options) {
                    // update collections
                    app.xforms.add(model, {merge: true});
                    
                    // show message
                    self.showMessage('Update successful', 'success');
                }
            })
        },
        
        close: function() {
            app.router.r.navigate('', {trigger: true});
        },
        
        render: function() {
            TemplateView.prototype.render.apply(this, arguments);
            $('#survey').html('');
            
            this.$desc = $('textarea.description', this.$el);
            this.$type = $('select.type', this.$el);
            this.$active = $('input.active', this.$el);
        },
        
        getChanges: function() {
            var changes = {
                // id included to indicate record to update
                id: this.xform.get('_id').$oid,
                
                // need to normalize these fields else error
                last_updated: this.normDate('last_updated'),
                date_imported: this.normDate('date_imported'),
                
                // actual changes
                type: this.$type.val(),
                description: this.$desc.val(),
                active: this.$active.is(':checked'),
            }
            
            if (_.isEmpty(changes.description))
                delete changes['description'];
            return changes;
        },
        
        getContext: function() {
            return {'xform': this.xform}
        }
    });
    
    
    // register views
    app.views.ApiServiceView = ApiServiceView;
    app.views.AdminXFormView = AdminXFormView;
    app.views.AdminXFormListView = AdminXFormListView;
    
})(jQuery, Backbone, _, app);