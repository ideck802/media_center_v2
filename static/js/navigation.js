/* eslint-disable quotes */

const pathBar = document.querySelector("#path_bar");
const fileView = document.querySelector("#file_view");
const browseCats = document.querySelectorAll(".browse-cat");
const browseSidebar = document.querySelector("#browse_sidebar");

let currFolderCont = [];
let currPath = '';
let lastPaths = {'music': '', 'movie': '', 'show': '', 'all': ''};
let currTab = 'music';

function changeBrowseType(cat) {
  const tabs = Array.from(browseCats).map(btn => btn.id.replace("browse-", ""));
  let activeIdx = tabs.findIndex(tabName =>
    document.querySelector(`.browse-${tabName}`).classList.contains("active")
  );

  lastPaths[tabs[activeIdx]] = currPath;

  let targetIdx;
  if (cat === "left") {
    targetIdx = (activeIdx - 1 + tabs.length) % tabs.length;
    cat = tabs[targetIdx];
  } else if (cat === "right") {
    targetIdx = (activeIdx + 1) % tabs.length;
    cat = tabs[targetIdx];
  } else if (cat === "current") {
    cat = tabs[activeIdx];
  }

  browseCats.forEach((btn) => {
    btn.classList.remove("active");
  });

  document.querySelector(`.browse-${cat}`).classList.add("active");

  if (lastPaths[cat] !== '') {
    if (cat !== 'all') {
      drawBrowse(lastPaths[cat]);
    }
  } else {
    if (cat !== 'all') {
      drawBrowse(settings[cat + "Path"]);
    }
  }

  currTab = cat;
}

function urlExists(url) {
  console.log('testing: ' + url);
  var http = new XMLHttpRequest();
  http.open('HEAD', url, false);
  http.send();
  return http.status != 404;
}

function getParentFolder(path, ancestor = 1) {
  const parts = path.replace("\\", "/").split("/");
  return parts[parts.length - (ancestor + 1)];
}

async function renderSidebar(fileIndex) {

  browseSidebar.innerHTML = `<div class="sidebar-extra" id="sidebar_extra"></div>
    <div class="name">
      <p>Loading...</p>
    </div>
    <div class="desc">
      <p></p>
    </div>`;

  const file = currFolderCont[fileIndex];
  let url = ['', ''];

  // check which type of media metadata we have
  if (urlExists(`${window.location.origin}/cached_metadata/movies/${file.name}_txt.json`)) {
    // either a movie file
    url = [`./cached_metadata/movies/${file.name}_`, 'movie'];

  } else if (urlExists(`${window.location.origin}/cached_metadata/shows/${file.name}/txt.json`)) {
    // a show folder
    url = [`./cached_metadata/shows/${file.name}/`, 'show'];

  } else if (file.type == 'folder') {
    // get parent folder name and extract season number
    const parent = getParentFolder(file.path);
    const seasonNum = parseInt(file.path.replace(/\D/g, "")).toString();
    if (urlExists(`${window.location.origin}/cached_metadata/shows/${parent}/season_${seasonNum}/txt.json`)) {
      // a season folder
      url = [`./cached_metadata/shows/${parent}/season_${seasonNum}/`, 'season'];
    }

  } else if (file.type != 'folder') {
    const parent = getParentFolder(file.path, 2);
    const seasonNum = parseInt(getParentFolder(file.path).replace(/\D/g, "")).toString();
    const episodeNum = parseInt(file.name.replace(/.*?e(\d+).*/i, "$1")).toString();
    // eslint-disable-next-line max-len
    if (urlExists(`${window.location.origin}/cached_metadata/shows/${parent}/season_${seasonNum}/${episodeNum}_txt.json`)) {
      // or an episode file
      url = [`./cached_metadata/shows/${parent}/season_${seasonNum}/${episodeNum}_`, 'episode'];
    }
  }

  console.log(url);

  let metadata = null;
  if (url[0] !== '') {
    const response = await fetch(`${url[0]}txt.json`);
    metadata = await response.json();
    console.log(metadata);
  }

  let html = '<div class="sidebar-extra" id="sidebar_extra">';

  if (file.type == 'folder') {
    if ((url[1] === 'show' || url[1] === 'season') && metadata !== null) {
      html += `<div class="picture">
        <img src="${url[0]}img.jpg">
      </div>`;
    } else {
      html += `<div class="picture"><i class="fa-solid fa-folder"></i></div>`;
    }
  } else if (['mp3', 'wav', 'flac'].includes(file.type)) {
    html += `<div class="picture"><i class="fa-solid fa-file-audio"></i></div>`;
  } else if (['jpg', 'png', 'jpeg', 'gif'].includes(file.type)) {
    html += `<div class="picture"><i class="fa-solid fa-file-image"></i></div>`;
  } else if (['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'm4v'].includes(file.type)) {
    if (metadata !== null) {
      html += `<div class="picture">
        <img src="${url[0]}img.jpg">
      </div>`;
    } else {
      html += `<div class="picture"><i class="fa-solid fa-file-video"></i></div>`;
    }
  } else {
    html += `<div class="picture"><i class="fa-solid fa-file"></i></div>`;
  }

  if (metadata == null) {
    html += `</div>
    <div class="name">
      <p>${file.name}</p>
    </div>
    <div class="desc">
      <p></p>
    </div>`;
  } else {
    html += `</div>
    <div class="name">
      <p>${metadata.title}</p>
    </div>
    <div class="desc">
      <p>${metadata.desc}</p>
    </div>`;
  }

  browseSidebar.innerHTML = html;
}

function goBack() {
  // get current active browse tab
  const tabs = Array.from(browseCats).map(btn => btn.id.replace("browse-", ""));
  let activeIdx = tabs.findIndex(tabName =>
    document.querySelector(`.browse-${tabName}`).classList.contains("active")
  );

  if (currPath !== settings[tabs[activeIdx] + "Path"] && tabs[activeIdx] !== 'all') {
    // get the path of the folder above by removing the last segment
    drawBrowse(currPath.split('/').slice(0, -1).join('/'));
  } else {
    drawBrowse(currPath);
  }
}

async function drawBrowse(path) {
  currPath = path;
  currFolderCont = [];
  const contents = await self.read_folder(path);
  const watchedList = await self.get_watched();

  pathBar.innerHTML = `<button onclick="guy.emit('go_back')">
      <i class="fa-solid fa-arrow-left"></i>
    </button>
    <p>${path}</p>`;

  fileView.innerHTML = '';
  let html = '';
  contents.forEach(item => {

    // figure out if the file/folder is on the watched list
    let watched = false;
    if (item.name.toLowerCase().includes('season')) {
      // if its a season
      const showName = getWatchedName(getParentFolder(item.path));
      if (showName in watchedList) {
        if (getWatchedName(item.name, 's') in watchedList[showName]) {
          watched = watchedList[showName][getWatchedName(item.name, 's')]['watched'];
        }
      }
    } else if (getParentFolder(item.path).toLowerCase().includes('season')) {
      // if its an episode
      const showName = getWatchedName(getParentFolder(item.path, 2));
      const seasonName = getWatchedName(getParentFolder(item.path), 's');
      if (showName in watchedList) {
        if (seasonName in watchedList[showName]) {
          if (getWatchedName(item.name, 'e') in watchedList[showName][seasonName]) {
            watched = watchedList[showName][seasonName][getWatchedName(item.name, 'e')];
          }
        }
      }
    } else if (item.type != 'folder') {
      // if its a movie file
      if (getWatchedName(item.name) in watchedList) {
        watched = watchedList[getWatchedName(item.name)];
      }
    } else {
      // if its the root show folder
      if (getWatchedName(item.name) in watchedList) {
        if (watchedList[getWatchedName(item.name)].watched === true) {
          watched = true;
        }
      }
    }

    currFolderCont.push(item);
    if (item.type == 'folder') {
      html += `<div class="dir-item" onclick="guy.emit('render_sidebar', ${currFolderCont.length - 1})">
        ${item.name}
        <button onclick="guy.emit('draw_browse', '${item.path.replace('\\', '/')}')">Open</button>
        <button onclick="self.handle_media('${item.path.replace('\\', '/')}','play-folder')">Play</button>
        <button onclick="self.handle_media('${item.path.replace('\\', '/')}','enqueue-folder')">Enqueue</button>
        <button onclick="self.dwnld_metadata('${currTab}','${item.path.replace('\\', '/')}')">Get Metadata</button>`;
    } else {
      html += `<div class="dir-item" onclick="guy.emit('render_sidebar', ${currFolderCont.length - 1})">
        ${item.name}`;
      if (['mp3', 'wav', 'flac', 'aac', 'ogg'].includes(item.type) ||
          ['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'm4v'].includes(item.type)) {
        html += `<button onclick="self.handle_media('${item.path.replace('\\', '/')}','play-file')">Play</button>
        <button onclick="self.handle_media('${item.path.replace('\\', '/')}','enqueue-file')">Enqueue</button>`;
      }
    }

    if (watched) {
      html += `<button onclick="self.set_watched('${item.path.replaceAll('\\', '/').replaceAll("'", "\\'")}', false)">
        <i class="fa-regular fa-eye-slash"></i>
      </button>`;
    } else {
      html += `<button onclick="self.set_watched('${item.path.replaceAll('\\', '/').replaceAll("'", "\\'")}')">
        <i class="fa-regular fa-eye"></i>
      </button>`;
    }
    html += `</div>`;

  });
  fileView.innerHTML = html;
}
