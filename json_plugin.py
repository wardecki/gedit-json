# gedit JSON plugin - One click JSON pretty formatting.
# Copyright (C) 2016 Piotr Wardecki dev@wardecki.com.pl
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GObject, Gtk, Gedit, GtkSource
from gettext import gettext as _
from json import loads, dumps

MENU_ENTRY = """<ui>
  <menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_2">
        <menuitem name="Format JSON" action="FormatJson"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""


class JsonPluginWindow(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "JsonPluginWindow"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self._register_menu()

    def do_deactivate(self):
        self._unregister_menu()

    def do_update_state(self):
        if self._action_group is not None:
            is_any_doc_active = self.window.get_active_document() is not None
            self._action_group.set_sensitive(is_any_doc_active)

    def _register_menu(self):
        manager = self.window.get_ui_manager()

        self._action_group = Gtk.ActionGroup("JsonPluginActions")
        self._action_group.add_actions([("FormatJson", None, _("Format JSON"), '<Primary><Alt>j',
                                       _("Format JSON"), self._on_format_json_action)])

        manager.insert_action_group(self._action_group, -1)
        self._ui_id = manager.add_ui_from_string(MENU_ENTRY)

    def _unregister_menu(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self._ui_id)
        manager.remove_action_group(self._action_group)
        manager.ensure_update()
        self._action_group = None

    def _show_error_dialog(self, primary, secondary):
        dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR,
                                   Gtk.ButtonsType.CLOSE, _(primary))
        dialog.format_secondary_text(_(secondary))
        dialog.run()
        dialog.destroy()

    @staticmethod
    def _set_json_language(doc):
        manager = GtkSource.LanguageManager()
        if 'json' in manager.get_language_ids():
            doc.set_language(manager.get_language('json'))

    def _on_format_json_action(self, action):
        document = self.window.get_active_document()
        if document is None:
            return
        try:
            start, end = document.get_bounds()
            json_content = loads(document.get_text(start, end, False))
            document.set_text(dumps(json_content, indent=2))
            self._set_json_language(document)
        except ValueError as error:
            self._show_error_dialog("Unable to parse JSON: ", str(error))
