module.exports = function(grunt) {
    var destJS = 'static/js/libs'
      , destCSS = 'static/css/libs'
      , destFONT = 'static/fonts';
    
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        
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
                files: ['static/less/*.less'],
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
                    {dest:destCSS, src:['fbower_comps/font-awesome/css/font-awesome.min.css'], expand:true, flatten:true},

                    // fonts
                    {dest:destFONT, src:['fbower_comps/bootstrap/dist/fonts/*.*'], expand:true, flatten:true},
                    {dest:destFONT, src:['fbower_comps/font-awesome/fonts/*.*'], expand:true, flatten:true},

                    // scripts
                    {dest:destJS, src:['fbower_comps/jquery/dist/jquery.min.js'], expand:true, flatten:true},
                    {dest:destJS, src:['fbower_comps/jquery-validation/dist/jquery.validate.min.js'], expand:true, flatten:true},
                    {dest:destJS, src:['fbower_comps/bootstrap/dist/js/bootstrap.min.js'], expand:true, flatten:true},
                ],
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('default', ['less', 'watch']);
};