/* jshint: laxcomma:true */

(function($, Backbone, _, app) {
    'use strict';

    // ::: views :::
    var TemplateView = Backbone.View.extend({
        innerEl: '',
        templateName: '',
        el: '.content-pane',
        initialize: function() {
            this.$alert = $('.js.alert', this.$el);
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
            return null;
        },
        render: function() {
            var context = this.getContext();
            if (_.isEmpty(context)) return;

            var _template = _.template($(this.templateName).html())
              , html = _template(context)
              , canvas = this.getCanvas();
            
            canvas.html(html);
            this.showMessage(null);
            $('.loading').addClass('hide');
            this.postRender();
        },
        serializeForm: function(form) {
            return _.object(_.map(form.serializeArray(), function(item) {
                return [item.name, item.value];
            }));
        },
        handleError: function(xhr, status, error) {
            $('.handleError-ind', this.$el).addClass('hide');
            this.showMessage(error || status);
        },
        showMessage: function(message, alert_tag) {
            if (_.isEmpty(message)) {
                this.$alert.addClass('hide');
            } else {
                this.$alert
                    .removeClass('hide alert-danger alert-success')
                    .addClass('alert-' + (alert_tag || 'danger'))
                    .find('.alert-board').text(message);
            }
        },
        postRender: function() {
            // do nothing...
        }
    }), 
    
    FormView = TemplateView.extend({
        events: {
            'click button.save': 'submit'
        },
        initialize: function() {
            TemplateView.prototype.initialize.apply(this, arguments);
        },
        submit: function() {
            $('form', this.$el).submit();
        }
    }),

    ToggledListView = TemplateView.extend({
        events: {
            'click input.toggler': 'togglerChanged',
            'click input.icheckbox': 'childChanged',
        },
        initialize: function() {
            TemplateView.prototype.initialize.apply(this, arguments);
        },
        postRender: function() {
            this.$toggler = $('input.toggler', this.$innerEl);
            this.$children = $('input.icheckbox', this.$innerEl);
        },
        togglerChanged: function(e) {
            var status = this.$toggler.is(':checked');
            this.$children.each(function() {
                $(this).prop('checked', status);
            });
        },
        childChanged: function(e) {
            var totalCount = this.$children.length
              , checkCount = $('input.icheckbox:checked', this.$innerEl).length;
            
            if (totalCount == checkCount) {
                if (!this.$toggler.is(':checked')) {
                    this.$toggler.prop('checked', true)
                                 .prop('indeterminate', false);
                }
            } else if (totalCount > checkCount && checkCount > 0) {
                this.$toggler.prop('checked', false)
                             .prop('indeterminate', true);
            } else {
                this.$toggler.prop('checked', false)
                             .prop('indeterminate', false);
            }
        }
    }),

    ApiServiceView = TemplateView.extend({
        el: '.content-pane',
        apiPoint: 'apiservices/',
        events: {
            'submit .auth-form': 'getToken',
            'submit .token-form': 'applyToken',
            'click a.clear-token': 'clearToken'
        },
        initialize: function() {
            TemplateView.prototype.initialize.apply(this, arguments);
            this.serviceKey = $('label.key', this.$el).text();
        },
        applyToken: function() {
            event.preventDefault();
            var $f = $(event.currentTarget)
              , token = $('input.token', this.$el).val();
            this.setToken(token);
        },
        clearToken: function() {
            var self = this
              , message = "Are you sure you want to clear the associated token? "
                        + "This operation cannot be undone.";

            app.$ck.dialog.confirm('CENTrak', message, function() {
                self.setToken(null);
            });
        },
        getToken: function(event) {
            event.preventDefault();
            var $form = $(event.currentTarget)
              , tstamp = new Date().getTime()
              , $usr = $('input.username', $form)
              , $pwd = $('input.password', $form)
              , cred = btoa($usr.val() + ":" + $pwd.val())
              , urlAuth = $('label.api-auth', this.$el).text();

            if (!_.isEmpty(urlAuth)) {
                $usr.attr('disabled', '');
                $pwd.attr('disabled', '');
                $('.processing', this.$el).removeClass('hide');
                $.ajax({
                    // hack: prevents browser from using cached credentials from a
                    // successful authentication thus api_url is caused to change.
                    url: urlAuth + '?t' + tstamp,
                    beforeSend: function(xhr) {
                        xhr.setRequestHeader("Authorization", "Basic " + cred);
                    }
                }).success($.proxy(this.displayToken, this))
                  .fail($.proxy(this.handleError, this));
              }
        },
        setToken: function(token) {
            var self = this;
            $.ajax({
                url: app.conf.apiRoot + self.apiPoint + self.serviceKey + "/",
                type: 'PATCH', data: {'api_token': token}
            }).done(function(data){
                var message = token === null
                            ? "API Token has been unset successfully."
                            : "API Token has been set successfully.";

                self.showMessage(message, 'success');
                $('label.api_token', this.$el).text(token !== null? token: "-");
            }).fail(function(xhr, status, error) {
                self.showMessage(error, 'danger');
            });
        },
        displayToken: function(data) {
            var $p = $('.processing', this.$el)
              , $f = $('.token-form', this.$el)
              , $t = $('.token', $f);

            $p.addClass('hide');
            $f.removeClass('hide');
            $t.val(data.api_token);
        },
        handleError: function(xhr, status, error) {
            $('.processing', this.$el).addClass('hide');
            $('input.username', this.$el).removeAttr('disabled');
            $('input.password', this.$el).removeAttr('disabled');
            TemplateView.prototype.handleError.apply(this, arguments);
        }
    }),
    
    SurveyXFormView = ToggledListView.extend({
        innerEl: '.xform-list',
        templateName: '#list-template',
        events: function() {
            return _.extend({}, ToggledListView.prototype.events, {
                'click button.import': 'importForms'
            });
        },
        initialize: function() {
            TemplateView.prototype.initialize.apply(this, arguments);
            this.bs_data = JSON.parse($('#bootstrap').text());

            var self = this;
            app.externalXForms.fetch({
                cache: false,
                beforeSend: self.setAuth,
                success: $.proxy(self.render, self),
                error: $.proxy(self.handleError, self)
            });
        },
        importForms: function() {
            var self = this, today = moment().format() 
              , selected = this._getSelectedXForms()
              , dispatch = function(m, resp, opts) {
                    var $td = $('#c' + m.get('object_id'), self.$innerEl);
                    $td.html('<i class="fa fa-fw fa-check"></i>');
                };
            
            _(selected).each(function(m) {
                m.set('date_imported', today);
                m.set('object_id', m.get('id'));
                if (_.isEmpty(m.get('description')))
                    m.unset('description');
                
                m.unset('id');
                app.xforms.create(m, {
                    wait: true,
                    success: dispatch,
                });
            });
        },
        setAuth: function(xhr) {
            xhr.setRequestHeader(
                'Authorization',
                'Token ' + app.$ck.getCookie('survey_auth_token'));
        },
        getContext: function() {
            var context = {'xforms': null};
            if (app.externalXForms.length == 0) {
                if (!_.isEmpty(this._error)) {
                    context['_error'] = this._error;
                    return context;
                }
                return null;
            }
            context['xforms'] = app.externalXForms;
            context['object_ids'] = this.bs_data.object_ids;
            return context;
        },
        handleError: function(coll, resp, options) {
            this._error = resp;
            this.render();
        },
        _getSelectedXForms: function() {
            var entry = null, selected = [];
            _($('input.icheckbox:checked')).each(function(e) {
                entry = app.externalXForms.findWhere({id: Number($(e).val())});
                if (!_.isEmpty(entry)) {
                    selected.push(entry.clone());
                }
            });
            return selected;
        }
    }),
    
    ImportView = TemplateView.extend({
        el: '.content-pane',
        events: {
            'click button.import': 'submit'
        },
        submit: function(e) {
            e.preventDefault();
            var tmpl = $('#progress', this.$el)
              , form = $('form', this.$el)
              , file = $('input[name=file]', form);
            
            if (file.val() == "") {
                $('.form-group.file-wrap', form).addClass('has-error');
            } else {
                form.submit();
                $('.import-pane').html(tmpl.html());
            }
        }
    }),

    PaperCaptureView = TemplateView.extend({
        el: '.form-compact',
        events: {
            'click input.fx': 'toggleInputFreeze',
            'change select': 'handleSelectChange',
        },
        initialize: function() {
            TemplateView.prototype.initialize.apply(this, arguments);
            var self = this;
            $(document).ready(function() {
                _($('input.fx:checked')).each(function(e) {
                    self.toggleInputFreeze({target: e});
                });
            });
        },
        handleSelectChange: function(e) {
            // var fx = 'input[name=fx_' + e.target.name + ']';
            // if ($(fx, this.$el).is(':checked')) {
            // }
        },
        toggleInputFreeze: function(e) {
            var checked = $(e.target).is(':checked')
              , name = e.target.name.replace('fx_', '')
              , ctrl = $('input[name=' + name + ']')
              , attr = 'readonly';
            
            if (ctrl.length == 0) {
                ctrl = $('select[name=' + name + ']');
            }
            if (checked) {
                ctrl.attr(attr, attr);
                ctrl.attr('tabIndex', '-1');
            } else if (name !== 'date_captured') {
                ctrl.removeAttr(attr);
                ctrl.attr('tabIndex', ctrl.data('ti'));
                ctrl.focus();
            }
        }
    }),

    // ::: NON ADMIN VIEWS
    
    PaperCaptureListView = TemplateView.extend({
        el: 'content-pane',
        initialize: function() {
            TemplateView.prototype.initialize.apply(this, arguments);
            var self = this;
            $(document).ready(function() {
                $('.datepicker-inline').datepicker({
                    format: 'yyyy-mm-dd', todayHighlight: true,
                }).on('changeDate', self.dateChanged);
            });
        },
        dateChanged: function(e) {
            var dt = e.format('yyyy-mm-dd') 
              , url = app.conf.urlRoot + "?date_digitized=" + dt;
            window.location.href = url;
        }
    });

    // ::: registery
    app.views.FormView = FormView;
    app.views.ToggledListView = ToggledListView;
    app.views.ApiServiceView = ApiServiceView;
    app.views.SurveyXFormView = SurveyXFormView;
    app.views.ImportView = ImportView;
    app.views.PaperCaptureView = PaperCaptureView;

    // ::: NON ADMIN
    app.views.PaperCaptureListView = PaperCaptureListView;

})(jQuery, Backbone, _, app);