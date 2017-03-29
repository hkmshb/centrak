from fabric.api import cd, env, local, run, sudo
from dolfin_deploy import *



def pre_deploy(site_name=None, proj_name=None, repo_url=None):
    env.site_name = site_name or 'centrak'
    env.proj_name = proj_name or 'centrak'
    env.site_dir  = "/opt/webapps/%s" % env.site_name
    env.repo_url  = repo_url
    if not repo_url:
        raise Exception("repo_url not provided.")


def post_deploy():
    fn.update_django_settings()
    fn.update_django_settings_ext()


def service(name, action):
    sudo('service %(name)s %(action)s' % {'name':name, 'action':action})


#+============================================================================+
#| override base behaviours
#+============================================================================+
def create_site_directories(**dirnames):
    directories = [
        dirnames.get('source_dir_name', 'source'),
        dirnames.get('public_dir_name', 'public'),
        dirnames.get('venv_dir_name', 'venv'),
        dirnames.get('inst_dir_name', 'instance'),
        dirnames.get('log_dir_name', 'instance/log'),
        dirnames.get('var_dir_name', 'instance/var'),
    ]
    
    for d in directories:
        env.d_ = d
        fullpath = "%(site_dir)s/%(d_)s" % env
        run("mkdir -p %s" % fullpath)
        env["%s_dir" % d] = fullpath


def update_virtualenv():
    run(("if [ ! -f %(venv_dir)s/bin/pip ]; then"
         "  virtualenv --python=python3.5 %(venv_dir)s; "
         "fi; "
         "%(venv_dir)s/bin/pip install -r %(source_dir)s/requirements/base.txt") % env)


def update_django_settings_ext():
    dir_path = "%(source_dir)s/%(proj_name)s/%(proj_name)s" % env
    filepath = "%s/settings.py" % dir_path

    run(("sed -e 's/_MONGODB_NAME = .*$/_MONGODB_NAME = \"centrak2\"/g'"
         " -e 's/# mongoengine/mongoengine/g'"
         " -i " + filepath) % env)


#+============================================================================+
#| configure env
#+============================================================================+
fn.pre_deploy = pre_deploy
fn.post_deploy = post_deploy
fn.update_virtualenv = update_virtualenv
fn.create_site_directories = create_site_directories
fn.update_django_settings_ext = update_django_settings_ext
