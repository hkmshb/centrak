/* jshint laxcomma:true */

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

            $('.date').datetimepicker({
                showClear: true,
                format: 'DD/MM/YYYY HH:mm A',
                useCurrent: false
            }).on('dp.show', function() {
                if ($(this).data('DateTimePicker').date() === null)
                    $(this).data('DateTimePicker').date(moment());
            });

            $('select.2').select2({
                theme: "bootstrap"
            });
        },
        
        getDbDate: function(model, field_name) {
            var value = model.get(field_name);
            if (!_.isEmpty(value)) {
                if (_.isObject(value))
                    value = value.$date;
                return moment(value).format();
            }
            return "";
        },

        toDbDate: function(value) {
            var fmt = 'DD/MM/YYYY HH:mm A'
              , val = moment(value, fmt);
            
            if (val.isValid()) {
                return val.format();
            }
            return value;
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
    
    MultiViewManager = TemplateView.extend({
        _comps: null,
        initialize: function(options) {
            $('.loading').addClass('hide');
            this._comps = (options.comps || []);
        },
        render: function() {
            _(this._comps).each(function(c) {
                c.render();
            });
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
    
    
    /*-----------------------------------------------------------------------+
    | AdminXForms View 
    +---------------------------------------------------------------------- */
    LocalXFormComponent = TemplateView.extend({
        templateName: '#local-xforms-template',
        initialize: function(){
            TemplateView.prototype.initialize.apply(this, arguments);
            this.mediator = arguments[0].mediator;
            var self = this, $bs = $('#bootstrap');
            
            // load bootstrapped data
            app.collections.ready.done(function() {
                this.bs_data = JSON.parse($bs.text());
                if (!_.isNull(this.bs_data.xforms)) {
                    app.xforms.reset(this.bs_data.xforms);
                    this.bs_data.xforms = null;
                    $bs.text(JSON.stringify(this.bs_data));
                    self.render();
                } else {
                    app.xforms.fetch({
                        reset: true,
                        success: $.proxy(self.render, self)
                    });
                }
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
                });
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
                    cache: false,
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
            };
        },
        
        registerForms: function(options){
            this._comps.local.register(options);
        },
        
        render: function() {
            _(this._comps).each(function(c) {
                c.render();
            });
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
            });
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
                id: (this.xform.has('_id')
                         ? this.xform.get('_id').$oid
                         : this.xform.get('id')),
                
                // need to normalize these fields else error
                last_updated: this.getDbDate(this.xform, 'last_updated'),
                date_imported: this.getDbDate(this.xform, 'date_imported'),
                
                // actual changes
                type: this.$type.val(),
                description: this.$desc.val(),
                active: this.$active.is(':checked'),
            };
            
            if (_.isEmpty(changes.description))
                delete changes['description'];
            return changes;
        },
        
        getContext: function() {
            return {'xform': this.xform};
        }
    }),
    
    
    /*-----------------------------------------------------------------------+
    | Admin PowerStation View 
    +---------------------------------------------------------------------- */
    AdminStationListComponent = TemplateView.extend({
        templateName: '#station-template',
        initialize: function(options) {
            TemplateView.prototype.initialize.apply(this, arguments);
            this.url = window.location.href.replace('#','');
            this.type = options.type;
        },
        
        events: {
            'click button.add': 'create',
        },
        
        create: function() {
            window.location = (this.url + '#/' + this.type + '/create');
        },
        
        getContext: function() {
            var title, stations;
            if (this.type === 't') {
                title = 'TRANSMISSION';
                stations = app.tstations;
            } else {
                title = 'INJECTION';
                stations = app.istations;
            }
            return {title:title, stations:stations};
        }
    }),
    
    AdminStationListView = MultiViewManager.extend({
        initialize: function() {
            var self = this
              , comps = {
                'l': new AdminStationListComponent({el:'#l-content', type:'t'}),
                'r': new AdminStationListComponent({el:'#r-content', type:'i'}),
            };
            MultiViewManager.prototype.initialize.call(this, {comps:comps}, arguments);
            
            // load bootstrapped data
            app.collections.ready.done(function() {
                if (_.isEmpty(this.bs_data)) {
                    this.bs_data = JSON.parse($('#bootstrap').text());
                }
                
                if (app.tstations.length < this.bs_data.tstations.length) 
                    app.tstations.reset(this.bs_data.tstations);
                
                if (app.istations.length < this.bs_data.istations.length)
                    app.istations.reset(this.bs_data.istations);
                
                app.voltratio = this.bs_data.voltratio;
                self.render();
            });
        },
    }),
    
    AdminStationFormView = TemplateView.extend({
        innerEl: '#l-content',
        templateName: '#new-template',
        initialize: function(options) {
            TemplateView.prototype.initialize.apply(this, arguments);
            this.type = options.type;
        },
        
        events: {
            'click button.save': 'createOne',
            'click button.cancel': 'close',
        },
        
        createOne: function() {
            var coll = (this.type === 't'? app.tstations: app.istations)
              , self = this
              , entry = {
                    object_id: Date.now(), 
                    type: this.type.toUpperCase(),
                    code: this.$code.val(),
                    name: this.$name.val(),
                    voltage_ratio: this.$vratio.val()
                };
            
            if (this.type === 'i') {
                entry.source = this.$source.val();
            }
            
            coll.create(entry, {
                wait: true,
                success: function(m, r, o) {
                    self.showMessage('Station created successfully', 'success');
                },
                fail: function(m, r, o) {
                    self.showMessage(r, 'danger');
                }
            });
        },
        
        close: function() {
            app.router.r.navigate('', {trigger: true});
        },
        
        render: function() {
            TemplateView.prototype.render.apply(this, arguments);
            $('#r-content', this.$el).html('');
            
            this.$code = $('input.code', this.$el);
            this.$name = $('input.name', this.$el);
            this.$source = $('select.source', this.$el);
            this.$vratio = $('select.voltage_ratio', this.$el);
        },
        
        getContext: function() {
            return {
                type: this.type, voltratio: app.voltratio,
                title: (this.type === 't'? 'Transmission': 'Injection').toUpperCase(),
            };
        }
    }),
    
    
    AdminProjectListView = TemplateView.extend({
        innerEl: '#l-content',
        templateName: '#list-template',
        initialize: function() {
            $('.loading').addClass('hide');
            TemplateView.prototype.initialize.apply(this, arguments);
            this.url = window.location.href.replace('#', '');
            var self = this, $bs = $('#bootstrap');
            
            // load bootstrapped data
            app.collections.ready.done(function() {
                this.bs_data = JSON.parse($bs.text());
                if (!_.isNull(this.bs_data.projects)) {
                    app.projects.reset(this.bs_data.projects);
                    this.bs_data.projects = null;
                    $bs.text(JSON.stringify(this.bs_data));
                    self.render();
                } else {
                    app.projects.fetch({
                        reset: true,
                        success: $.proxy(self.render, self)
                    });
                }
            });
        },
        
        events: {
            'click button.add': 'create',
        },
        
        create: function() {
            window.location = (this.url + '#/create');
        },
        
        getContext: function() {
            return {'projects': app.projects};
        }
    }),
    
    AdminProjectFormView = TemplateView.extend({
        innerEl: '#l-content',
        templateName: '#form-template',
        initialize: function(options) {
            TemplateView.prototype.initialize.apply(this, arguments);
            this.project_code = options.project_code;
            this.editable = options.edit || false;
            var self = this;
            
            // load bootstrapped data
            var bs_data = JSON.parse($('#bootstrap').text());
            this.choices = bs_data.choices;
            
            if (!_.isEmpty(options.project_code)) {
                if (_.isEmpty(app.projects) || app.projects.length === 0) {
                    this.close();
                } else {
                    var q = {code: options.project_code}
                      , p = app.projects.findWhere(q);
                    
                    if (_.isEmpty(p))
                        this.close();
                    this.project = p;
                }
            }
        },
        events: {
            'click button.save': 'manageOne',
            'click button.edit': 'editOne',
            'click button.cancel': 'close',
        },
        close: function() {
            var r = '';
            if (!_.isEmpty(this.project) && this.editable) {
                r = '/' + this.project.get('code') + '/';
            }
            app.router.r.navigate(r, {trigger: true});
        },
        manageOne: function() {
            var self = this, changes = null;
            if (_.isEmpty(this.project)) {
                changes = this.getChanges();
                app.projects.create(changes, {
                    wait: true,
                    success: function(m, r, o) {
                        self.showMessage('Project created successfully', 'success');
                    },
                    fail: function(m, r, o) {
                        self.showMessage(r, 'danger');
                    }
                });
            } else {
                changes = this.getChanges(true);
                this.project.save(changes, {
                    wait: true,
                    patch: true,
                    success: function(model, resp, options) {
                        // update collection & show message
                        app.projects.add(model, {merge: true});
                        self.project = app.projects.findWhere({code: self.project_code});
                        self.showMessage('Project updated successfully', 'success');
                    },
                    error: function(model, resp, options) {
                        self.showMessage('Update failed.', 'danger');
                    }
                });
            }
        }, 
        editOne: function() {
            if (_.isEmpty(this.project))
                this.close();
            
            var r = '#/' + this.project.get('code') + '/update';
            app.router.r.navigate(r, {trigger:true});
        },
        render: function() {
            TemplateView.prototype.render.apply(this, arguments);
            $('#r-content', this.$el).html('');
            
            this.$code = $('input.code', this.$el);
            this.$name = $('input.name', this.$el);
            this.$desc = $('textarea.description', this.$el);
            this.$status = $('select.status', this.$el);
            this.$xforms = $('select.xforms', this.$el);
            this.$uforms = $('select.uforms', this.$el);
            this.$active = $('input.active', this.$el);
            this.$auto_sync = $('input.auto_sync', this.$el);
            this.$dt_started = $('input.date_started', this.$el);
            this.$dt_ended = $('input.date_ended', this.$el);
        },
        getContext: function() {
            return {
                project: this.project,
                editable: this.editable,
                choices: this.choices
            };
        },
        getChanges: function(isUpdate) {
            var field = null
              , fields = [
                    'code','name','description','status','active', 'auto_sync', 
                    'xforms', 'uforms', 'date_started','date_ended']
              , changes = {
                    // need to normalize these fields else error
                    last_updated: moment().format(),
                    
                    // actual changes
                    code: this.$code.val(),
                    name: this.$name.val(),
                    description: this.$desc.val(),
                    status: this.$status.val(),
                    active: this.$active.is(':checked'),
                    auto_sync: this.$auto_sync.is(':checked'),
                    date_started: this.toDbDate(this.$dt_started.val()),
                    date_ended: this.toDbDate(this.$dt_ended.val()),
                    xforms: this.$xforms.val(),
                    uforms: this.$uforms.val(),
                };
            
            for (var i in fields) {
                field = fields[i];
                if (_(['xforms','uforms']).contains(field)) {
                    if (_.isNull(changes[field]))
                        changes[field] = [];
                } else if (this.project && this.project.get(field) == changes[field]) {
                    delete changes[field];
                } else if (_.isEqual(changes[field], "")) {
                    changes[field] = null;
                }
            }

            if (isUpdate) {
                // include id to indicate record to update
                changes.id = (this.project.has('_id')
                                  ? this.project.get('_id').$oid
                                  : this.project.get('id'));
            }
            return changes;
        }
    });
    
    
    
    // register views
    app.views.ApiServiceView = ApiServiceView;
    app.views.AdminXFormView = AdminXFormView;
    app.views.AdminXFormListView = AdminXFormListView;
    app.views.AdminProjectListView = AdminProjectListView;
    app.views.AdminProjectFormView = AdminProjectFormView;
    
    app.views.MultiViewManager = MultiViewManager;
    app.views.AdminStationFormView = AdminStationFormView;
    app.views.AdminStationListView = AdminStationListView;
    
})(jQuery, Backbone, _, app);