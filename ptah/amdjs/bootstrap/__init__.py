# bootstrap http://getbootstrap.com


def includeme(config):
    config.include('ptah.amdjs')

    # static assets
    config.add_static_view('_amdjs_bootstrap/static', 'ptah.amdjs.bootstrap:static/')
    
    config.add_amd_js(
        'bootstrap',
        'ptah.amdjs.bootstrap:static/bootstrap-3.2.0/js/bootstrap.min.js',
        'Bootstrap Javascript Library', ('jquery',))
    config.add_amd_css(
        'bootstrap-css',
        'ptah.amdjs.bootstrap:static/bootstrap-3.2.0/css/bootstrap.min.css',
        'Bootstrap CSS Library')
    config.add_amd_css(
        'bootstrap-theme-css',
        'ptah.amdjs.bootstrap:static/bootstrap-3.2.0/css/bootstrap-theme.min.css',
        'Bootstrap CSS Theme Library)')
