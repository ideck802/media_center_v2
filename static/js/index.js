/* eslint-disable quotes */

const tabBtns = document.querySelectorAll(".tab-btn");
const tabCont = document.querySelectorAll(".tab-cont");
const shrinkArrow = document.querySelector("#resize_btn");
const playpauseBtn = document.querySelector("#play_btn");
const progBar = document.querySelector("#progBar");

let settings = '';

function init(newSettings) {
  settings = newSettings;

  initEvents();
  if (settings.fileDisp === 'grid') {
    document.querySelector("#browse_sidebar").classList.add('hide-medium');
    document.querySelector("#file_view").classList.add('grid');
  } else if (settings.fileDisp === 'list') {
    document.querySelector("#file_view").classList.add('list');
  }

  guy.emit('change_browse', 'music');
}

function changeTab(tab) {

  const tabs = Array.from(tabBtns).map(btn => btn.id.replace("_btn", ""));
  let activeIdx = tabs.findIndex(tabName =>
    document.querySelector(`#${tabName}_btn`).classList.contains("active")
  );

  let targetIdx;
  if (tab === "left") {
    targetIdx = (activeIdx - 1 + tabs.length) % tabs.length;
    tab = tabs[targetIdx];
  } else if (tab === "right") {
    targetIdx = (activeIdx + 1) % tabs.length;
    tab = tabs[targetIdx];
  }

  tabBtns.forEach((btn) => {
    btn.classList.remove("active");
  });
  tabCont.forEach((cont) => {
    cont.classList.remove("active");
  });

  document.querySelector(`#${tab}_btn`).classList.add("active");
  document.querySelector(`#${tab}_cont`).classList.add("active");

  // if switching to browse tab, rerender current sub-tab
  if (tab === 'browse') {
    guy.emit('change_browse', 'current');
  } else if (tab === 'playing') {
    renderPlaylist();
  }
}

function changeChevron(direction) {
  shrinkArrow.innerHTML = "<i class='fa-solid fa-chevron-" + direction + "'></i>";
}

function changePlayPause(state) {
  if (state === 'play') {
    playpauseBtn.innerHTML = "<i class='fa-solid fa-pause'></i>";
  } else if (state === 'pause') {
    playpauseBtn.innerHTML = "<i class='fa-solid fa-play'></i>";
  }
}

function renderProgBar(len, pos, time) {
  progBar.innerHTML = '';
  let marker = `<p class='media-time'>
  ` + time + `</p><div class='marker-cont'>
  <div class='marker' style='width: ` + pos + `%;'>.</div>
  </div><p class='media-len'>` + len + '</p>';
  progBar.innerHTML = marker;
}
