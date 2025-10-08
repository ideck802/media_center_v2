/* eslint-disable quotes */

function initEvents() {
  guy.on("change_tab", changeTab);
  guy.on("change_chevron", changeChevron);
  guy.on("change_browse", changeBrowseType);
  guy.on("go_back", goBack);
  guy.on("render_sidebar", renderSidebar);
  guy.on("draw_browse", drawBrowse);
  guy.on("highlight_action", highlightAction);
  guy.on("focus_toggle", focusToggle);
  guy.on("change_playpause", changePlayPause);
  guy.on("render_prog", renderProgBar);
  guy.on("render_playlist", renderPlaylist);
  guy.on("render_playing_notif", renderPlayingNotif);
}
