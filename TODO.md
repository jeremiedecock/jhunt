# TODO

## Version 0.1

- [x] Gtk.TreeView: add sorting, ellipsis
- [x] Update the Gtk.ListStore (model)
- [x] Use Gtk.Dialog instead "print(...)"
- [x] Use Gtk.Grid instead Gtk.Box
- [ ] Add a feature: edit/save job adverts (use a Gtk.Paned container)
- [ ] GtkTreeView: add filtering (from a search entry)
- [ ] URL cliquable (+ icone) in Gtk.TreeView
- [ ] Add + Save/Edit: add "Filling of candidature" (envoi de candidature) + date (or None by default)
    - [ ] Use the Gtk Calendar widget
- [ ] Save/Edit: add "Tracking application" (suivi de candidature) + TextView (dates, personnes, description des entretiens, ...)
- [ ] Save/Edit: "State" ("en cours", "refusé", ...)
- [ ] Clean...
- [ ] Add a locking system to avoid multiple instanciation of the application (and data lose)...
    - [ ] Use the Gtk.Application method (see http://stackoverflow.com/questions/19072161/preventing-multiple-instances-of-a-gtk-application )

## Version 0.2

- [ ] Score: select nothing by default

## Version 1.0

- [ ] Add a README.md file
- [ ] Add a Gtk.Menu and/or Toolbar (like a regular Gnome app)

## Later ?

- [ ] Solve the redundancy problem of data/model: Gtk.ListStore (model) + dictionnaire "data" => redundant
