import sublime
import sublime_plugin

import base64
import mimetypes
import urllib


# data:[<media type>][;base64],<data>


# -----------------------------------------------------------------------------


def plugin_loaded():
    # TODO: Watch for settings changes and see if the view listeners should
    # change.
    uri_setting.obj = sublime.load_settings("DataURITool.sublime-settings")
    uri_setting.default = {
        "active_scopes": [],
        "check_timeout": 2
    }


def uri_setting(key):
    """
    Get an package setting from a cached settings object.
    """
    default = uri_setting.default.get(key, None)
    return uri_setting.obj.get(key, default)


# -----------------------------------------------------------------------------


class CreateDataUriCommand(sublime_plugin.WindowCommand):
    """
    Copy a data URI for the tab currently active in the window to the
    clipboard. This works with plain text and image files, or really any binary
    file for that matter.
    """
    def run(self):
        sheet = self.window.active_sheet()
        file_name = sheet.file_name()
        file_type = mimetypes.guess_type(file_name)[0] or "text/plain"
        is_binary = not file_type.startswith("text/")
        data = self.get_file_content(file_name, is_binary)
        if data is not None:
            uri = 'data:{type}{binary},{data}'.format(
                    type=file_type,
                    binary=';base64' if is_binary else '',
                    data=data)
            sublime.set_clipboard(uri)
            self.window.status_message('data URI copied!')

    def get_file_content(self, file_name, is_binary):
        """
        Given a file name, return back a base64 encoded version of the content
        of the file. is_binary is used to determine how we should fetch the
        data out of the file.

        None is returned if the file is not accessible.
        """
        file_mode = "rb" if is_binary else "r"
        try:
            with open(file_name, file_mode) as handle:
                data = handle.read()
                if is_binary:
                    return base64.b64encode(data).decode('utf-8')
                else:
                    return urllib.parse.quote(data)

        except Exception as e:
            self.window.status_message('Unable to access file: %s' % str(e))

        return None

    def is_enabled(self):
        """
        Ensure that we're only enabled for files that have been persisted to
        disk.
        """
        return self.window.active_sheet().file_name() is not None


# -----------------------------------------------------------------------------


class UriHoverEventListener(sublime_plugin.ViewEventListener):
    """
    Watch for file changes and hovers in configured files to see if we should
    be displaying any previews or not, and if so from what URI's.
    """
    pending_count = 0

    @classmethod
    def is_applicable(cls, settings):
        this_syntax = settings.get("syntax")
        for syntax in sublime.list_syntaxes():
            for scope in uri_setting("active_scopes"):
                if syntax.path == this_syntax:
                    if sublime.score_selector(syntax.scope, scope):
                        return True

        return False

    def on_modified_async(self):
        self.pending_count += 1
        sublime.set_timeout_async(lambda: self.trigger_check(), uri_setting("check_timeout") * 1000)

    # Look for regions once a file opens.
    on_load = on_modified_async

    def trigger_check(self):
        self.pending_count -= 1
        if self.pending_count != 0:
            return

        self.view.add_regions('datas',
            self.view.find_all(r'data:((?:\w+\/(?:(?!;).)+)?)((?:;[\w\W]*?[^;])*),(.+?)(?=[\s"])', 0),
            "comment", flags=sublime.DRAW_NO_FILL)

    def on_hover(self, point, zone):
        if zone != sublime.HOVER_TEXT:
            return

        regions = self.view.get_regions('datas')
        if not regions:
            return

        for region in regions:
            if region.contains(point):
                uri = self.view.substr(region)
                if uri.startswith("data:image/"):
                    self.preview_uri(uri, point)
                return

    def preview_uri(self, uri, point):
        self.view.show_popup(
            '<img src="%s" />' % uri,
            sublime.HIDE_ON_MOUSE_MOVE_AWAY,
            point)


# -----------------------------------------------------------------------------
