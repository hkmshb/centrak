'use strict';

module.exports = function(grunt) {
    require('time-grunt')(grunt);
    require('jit-grunt')(grunt);

    // configuration paths for resx
    var conf = {
        bowr: 'fbower_comps',
        node: 'node_modules',
        font: 'static/libs/fonts',
        css: 'static/libs/css',
        js: 'static/libs/js',
    };

    grunt.initConfig({
        // settings
        p: conf,

        // copy third-party resources to appropriate dir
        copy: {
            main: {
                files: [{
                    // styles
                    expand:true, flatten:true, dest:'<%= p.css %>', src:'<%= p.bowr %>/bootstrap/dist/css/bootstrap.min.css' }, {
                    expand:true, flatten:true, dest:'<%= p.css %>', src:'<%= p.bowr %>/font-awesome/css/font-awesome.min.css' }, {
                    expand:true, flatten:true, dest:'<%= p.css %>', src:'<%= p.bowr %>/bootstrap-datepicker/dist/css/bootstrap-datepicker3.min.css' }, {
                    expand:true, flatten:true, dest:'<%= p.css %>', src:'<%= p.bowr %>/bootstrap-select/dist/css/bootstrap-select.min.css' }, {
                    
                    // fonts:
                    expand:true, flatten:true, dest:'<%= p.font %>', src:'<%= p.bowr %>/bootstrap/dist/fonts/*.*' }, {
                    expand:true, flatten:true, dest:'<%= p.font %>', src:'<%= p.bowr %>/font-awesome/fonts/*.*' }, {
                    
                    // scripts:
                    expand:true, flatten:true, dest:'<%= p.js %>', src:'<%= p.bowr %>/jquery/dist/jquery.min.js' }, {
                    expand:true, flatten:true, dest:'<%= p.js %>', src:'<%= p.bowr %>/jquery-validation/dist/jquery.validate.min.js' }, {
                    expand:true, flatten:true, dest:'<%= p.js %>', src:'<%= p.bowr %>/bootstrap/dist/js/bootstrap.min.js' }, {
                    expand:true, flatten:true, dest:'<%= p.js %>', src:'<%= p.bowr %>/bootstrap-datepicker/dist/js/bootstrap-datepicker.min.js' }, {
                    expand:true, flatten:true, dest:'<%= p.js %>', src:'<%= p.bowr %>/underscore/underscore-min.js' }, {
                    expand:true, flatten:true, dest:'<%= p.js %>', src:'<%= p.bowr %>/backbone/backbone-min.js' }, {
                    expand:true, flatten:true, dest:'<%= p.js %>', src:'<%= p.bowr %>/moment/min/moment.min.js' }, {
                    expand:true, flatten:true, dest:'<%= p.js %>', src:'<%= p.bowr %>/chart.js/dist/Chart.min.js' }, {
                    expand:true, flatten:true, dest:'<%= p.js %>', src:'<%= p.bowr %>/bootstrap-select/dist/js/bootstrap-select.min.js'
                }]
            }
        },
        less: {
            dist: {
                files: {
                    'static/css/site.css': 'static/less/site.less',
                    'static/css/account.css': 'static/less/account.less',
                }
            }
        },
        watch: {
            css: {
                options: { spawn: false },
                files: ['static/less/*.less'],
                tasks: ['less']
            }
        }
    });

    grunt.registerTask('default', ['less', 'watch']);
};