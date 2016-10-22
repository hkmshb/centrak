/* jshint: laxcomma:true */

(function($, Backbone, _, app) {
    'use strict';

    // ::: views :::
    var FormView = Backbone.View.extend({
        el: '.content-pane',
        events: {
            'click button.save': 'submit'
        },
        submit: function() {
            $('form', this.$el).submit();
        },
        serializeForm: function(form) {
            return _.object(_.map(form.serializeArray(), function(item) {
                return [item.name, item.value];
            }));
        }
    }),

    ApiServiceView = Backbone.View.extend({
        el: '.content-pane',
        apiPoint: 'apiservices/',
        events: {
            'submit .auth-form': 'getToken',
            'submit .token-form': 'applyToken',
            'click a.clear-token': 'clearToken'
        },
        initialize: function() {
            Backbone.View.prototype.initialize.apply(this, arguments);
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
                $('.progress-col', this.$el).removeClass('hide');
                $.ajax({
                    // hack: prevents browser from using cached credentials from a
                    // successful authentication thus api_url is caused to change.
                    url: urlAuth + '?t' + tstamp,
                    beforeSend: function(xhr) {
                        xhr.setRequestHeader("Authorization", "Basic " + cred);
                    }
                }).success($.proxy(this.displayToken, this))
                  .fail($.proxy(this.displayError, this));
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

                self.displayMessage(message, 'success');
                $('label.api_token', this.$el).text(token !== null? token: "-");
            }).fail(function(xhr, status, error) {
                self.displayMessage(error, 'danger');
            });
        },
        displayToken: function(data) {
            var $p = $('.progress-col', this.$el)
              , $f = $('.token-form', this.$el)
              , $t = $('.token', $f);

            $p.addClass('hide');
            $f.removeClass('hide');
            $t.val(data.api_token);
        },
        displayError: function(xhr, status, error) {
            $('.progress-col', this.$el).addClass('hide');
            this.displayMessage(status + ": " + error, 'danger');
        },
        displayMessage: function(message, alert_tag) {
            var $alert = $('.js.alert');
            $alert.removeClass('alert-danger').removeClass('alert-success');
            if (!_.isEmpty(message)) {
                $alert.removeClass('hide')
                      .addClass('alert-' + alert_tag)
                      .find('.alert-board')
                      .text(message);
            } else {
                $alert.addClass('hide');
            }
        }
    });

    // ::: registery
    app.views.FormView = FormView;
    app.views.ApiServiceView = ApiServiceView;

})(jQuery, Backbone, _, app);