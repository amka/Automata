application_id = 'com.tenderowl.automata'

scalable_dir = 'hicolor' / '48x48' / 'apps'
install_data(
  scalable_dir / ('@0@.png').format(application_id),
  install_dir: get_option('datadir') / 'icons' / scalable_dir
)

symbolic_dir = 'hicolor' / '256x256' / 'apps'
install_data(
  symbolic_dir / ('@0@.png').format(application_id),
  install_dir: get_option('datadir') / 'icons' / symbolic_dir
)
