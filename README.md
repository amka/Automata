# Automata

A modern, local-first project management application designed for C-level managers. Built for GNOME with GTK4 and Libadwaita, Automata provides a sleek and intuitive interface for managing projects, tasks, and notes without relying on cloud services.

## Features

- **Local-First**: All your data stays on your device. No accounts, no subscriptions, no data leaks.
- **Extensible**: Customize and extend functionality with plugins.
- **Modern UI**: Built with GTK4 and Libadwaita for a native GNOME experience.
- **Task Management**: Organize tasks with projects, tags, and priorities.
- **Note Taking**: Capture ideas and notes seamlessly.
- **Dashboard**: Get an overview of your projects and tasks at a glance.
- **Inbox**: Manage incoming tasks and requests efficiently.

## Installation

### Prerequisites

- GNOME Desktop Environment
- Python 3.10 or later
- Meson build system
- Ninja build tool

### Build and Install

1. Clone the repository:
   ```bash
   git clone https://github.com/amka/Automata.git
   cd automata
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Build the project:
   ```bash
   meson setup builddir
   ninja -C builddir
   ```

4. Install:
   ```bash
   sudo ninja -C builddir install
   ```

5. Run Automata:
   ```bash
   automata
   ```

## Usage

After installation, launch Automata from your applications menu or run `automata` in the terminal.

- Use the dashboard to see an overview of your projects.
- Create new projects and add tasks.
- Organize tasks with tags and due dates.
- Capture quick notes in the inbox.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [COPYING](COPYING) file for details.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.
