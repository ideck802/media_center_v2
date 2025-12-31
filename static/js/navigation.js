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
  var http = new XMLHttpRequest();
  http.open('HEAD', url, false);
  http.send();
  return http.status != 404;
}

async function renderSidebar(fileIndex) {

  browseSidebar.innerHTML = '';

  const file = currFolderCont[fileIndex];

  let metadata = null;
  if (urlExists(`${window.location.origin}/cached_metadata/${file.name}_img.jpg`) &&
    ['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'm4v'].includes(file.type)) {
    const response = await fetch(`./cached_metadata/${file.name}_txt.txt`);
    metadata = await response.json();
    console.log(metadata);
  }

  let html = '<div class="sidebar-extra" id="sidebar_extra">';

  if (file.type == 'folder') {
    html += `<div class="picture"><i class="fa-solid fa-folder"></i></div>`;
  } else if (['mp3', 'wav', 'flac'].includes(file.type)) {
    html += `<div class="picture"><i class="fa-solid fa-file-audio"></i></div>`;
  } else if (['jpg', 'png', 'jpeg', 'gif'].includes(file.type)) {
    html += `<div class="picture"><i class="fa-solid fa-file-image"></i></div>`;
  } else if (['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'm4v'].includes(file.type)) {
    if (metadata !== null) {
      html += `<div class="picture">
        <img src="./cached_metadata/${file.name}_img.jpg">
      </div>`;
    } else {
      html += `<div class="picture"><i class="fa-solid fa-file-video"></i></div>`;
    }
  } else {
    html += `<div class="picture"><i class="fa-solid fa-file"></i></div>`;
  }

  if (metadata == null) {
    html += `</div>
    <p>${file.name}</p>`;
  } else {
    html += `</div>
    <p>${metadata.title}</p>`;
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

  pathBar.innerHTML = `<button onclick="guy.emit('go_back')">
      <i class="fa-solid fa-arrow-left"></i>
    </button>
    <p>${path}</p>`;

  fileView.innerHTML = '';
  let html = '';
  contents.forEach(item => {
    currFolderCont.push(item);
    if (item.type == 'folder') {
      html += `<div class="dir-item" onclick="guy.emit('render_sidebar', ${currFolderCont.length - 1})">
        ${item.name}
        <button onclick="guy.emit('draw_browse', '${item.path.replace('\\', '/')}')">Open</button>
        <button onclick="self.handle_media('${item.path.replace('\\', '/')}','play-folder')">Play</button>
        <button onclick="self.handle_media('${item.path.replace('\\', '/')}','enqueue-folder')">Enqueue</button>
        <button onclick="self.dwnld_metadata('${currTab}','${item.path.replace('\\', '/')}')">Get Metadata</button>
      </div>`;
    } else {
      html += `<div class="dir-item" onclick="guy.emit('render_sidebar', ${currFolderCont.length - 1})">
        ${item.name}`;
      if (['mp3', 'wav', 'flac', 'aac', 'ogg'].includes(item.type) ||
          ['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'm4v'].includes(item.type)) {
        html += `<button onclick="self.handle_media('${item.path.replace('\\', '/')}','play-file')">Play</button>
        <button onclick="self.handle_media('${item.path.replace('\\', '/')}','enqueue-file')">Enqueue</button>`;
      }
      html += `</div>`;
    }
  });
  fileView.innerHTML = html;
}
