blueprints = custom_target(
    'blueprints',
    input: files(
        'ui/dashboard.blp',
        'ui/goals_page.blp',
        'ui/inbox.blp',
        'ui/persons-page.blp',
        'ui/projects_page.blp',
        'ui/setup-wizard.blp',
        'ui/shortcuts-dialog.blp',
        'ui/sidebar.blp',
        'ui/task_list_row.blp',
        'ui/window.blp',
    ),
    output: '.',
    command: [
        find_program('blueprint-compiler'),
        'batch-compile',
        # '--minify',
        '@OUTPUT@',
        '@CURRENT_SOURCE_DIR@',
        '@INPUT@',
    ],
)

gnome.compile_resources(
    'automata',
    'automata.gresource.xml',
    dependencies: blueprints,
    gresource_bundle: true,
    install: true,
    install_dir: pkgdatadir,
)

desktop_file = i18n.merge_file(
    input: 'com.tenderowl.automata.desktop.in',
    output: 'com.tenderowl.automata.desktop',
    type: 'desktop',
    po_dir: '../po',
    install: true,
    install_dir: get_option('datadir') / 'applications',
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
    test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

appstream_file = i18n.merge_file(
    input: 'com.tenderowl.automata.metainfo.xml.in',
    output: 'com.tenderowl.automata.metainfo.xml',
    po_dir: '../po',
    install: true,
    install_dir: get_option('datadir') / 'metainfo',
)

appstreamcli = find_program('appstreamcli', required: false, disabler: true)
test(
    'Validate appstream file',
    appstreamcli,
    args: ['validate', '--no-net', '--explain', appstream_file],
)

install_data(
    'com.tenderowl.automata.gschema.xml',
    install_dir: get_option('datadir') / 'glib-2.0' / 'schemas',
)

compile_schemas = find_program('glib-compile-schemas', required: false, disabler: true)
test(
    'Validate schema file',
    compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()],
)

service_conf = configuration_data()
service_conf.set('bindir', get_option('prefix') / get_option('bindir'))
configure_file(
    input: 'com.tenderowl.automata.service.in',
    output: 'com.tenderowl.automata.service',
    configuration: service_conf,
    install_dir: get_option('datadir') / 'dbus-1' / 'services',
)

subdir('icons')
