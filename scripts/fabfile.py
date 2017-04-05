from elixr.deploy.fab import DjangoFabHelper



class CentrakFab(DjangoFabHelper):

    class Meta(DjangoFabHelper.Meta):
        project = 'centrak'
        uses_celeryd = True
        pip_rfile = 'requirements/base.txt'
        repo_url = 'https://github.com/hkmshb/centrak.git'
        site_subdirs = DjangoFabHelper.Meta.site_subdirs \
                     + ['instance/log', 'instance/var']

        ## database settings
        db_name  = 'CENTrak'
        mdb_name = 'centrak'


def deploy(project=None, staging=True, repo_url=None, **extras):
    fab = CentrakFab(project, staging, repo_url, **extras)
    fab.deploy()
    