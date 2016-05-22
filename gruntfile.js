module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        
        less: {
            dist: {
                options: {
                    x_style: 'compressed'
                },
                files: {
                    'centrak/static/css/site.css': 'centrak/static/less/site.less',
                } 
            }
        },
        watch: {
            css: {
                files: ['centrak/static/less/*.less'],
                tasks: ['less'],
                options: {
                    spawn: false,
                }
            }
        }
    });
    
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-less');
    
    grunt.registerTask('default', ['less', 'watch']);
}