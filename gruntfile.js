module.exports = function(grunt) {
    var destJS = 'fbower_comps/_libs/js/',
        destCSS = 'fbower_comps/_libs/css/',
        destFONT = 'fbower_comps/_libs/fonts/';
    
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        
        less: {
            dist: {
                options: {
                    x_style: 'compressed'
                },
                files: {
                    'centrak/main/static/css/site.css': 'centrak/main/static/less/site.less',
                    'centrak/main/static/css/account.css': 'centrak/main/static/less/account.less',
                } 
            }
        },
        watch: {
            css: {
                files: ['centrak/main/static/less/*.less'],
                tasks: ['less'],
                options: {
                    spawn: false,
                }
            }
        },
        copy: {
            main: {
                files: [
                    // style-sheets
                    {dest:destCSS, src:['fbower_comps/bootstrap/dist/css/bootstrap.min.css'], expand:true, flatten:true},
                    {dest:destCSS, src:['fbower_comps/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css'], expand:true, flatten:true},
                    {dest:destCSS, src:['fbower_comps/select2/dist/css/select2.min.css'], expand:true, flatten:true},
                    {dest:destCSS, src:['fbower_comps/select2-bootstrap-theme/dist/select2-bootstrap.min.css'], expand:true, flatten:true},
                    {dest:destCSS, src:['fbower_comps/font-awesome/css/font-awesome.min.css'], expand:true, flatten:true},

                    // fonts
                    {dest:destFONT, src:['fbower_comps/bootstrap/dist/fonts/*.*'], expand:true, flatten:true},
                    {dest:destFONT, src:['fbower_comps/font-awesome/fonts/*.*'], expand:true, flatten:true},
                    
                    // scripts
                    {dest:destJS, src:['fbower_comps/jquery/dist/jquery.min.js'], expand:true, flatten:true},
                    {dest:destJS, src:['fbower_comps/jquery-validation/dist/jquery.validate.min.js'], expand:true, flatten:true},
                    {dest:destJS, src:['fbower_comps/underscore/underscore-min.js'], expand:true, flatten:true},
                    {dest:destJS, src:['fbower_comps/backbone/backbone-min.js'], expand:true, flatten:true},
                    {dest:destJS, src:['fbower_comps/moment/min/moment.min.js'], expand:true, flatten:true},
                    {dest:destJS, src:['fbower_comps/humanize-plus/dist/humanize.min.js'], expand:true, flatten:true},
                    {dest:destJS, src:['fbower_comps/bootstrap/dist/js/bootstrap.min.js'], expand:true, flatten:true},
                    {dest:destJS, src:['fbower_comps/select2/dist/js/select2.min.js'], expand:true, flatten:true},
                    {dest:destJS, src:['fbower_comps/eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js'], expand:true, flatten:true},
                ]
            }
        }
    });
    
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-copy');
    
    grunt.registerTask('default', ['less', 'watch']);
}