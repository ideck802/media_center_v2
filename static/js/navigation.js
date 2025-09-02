/* eslint-disable quotes */

const fileView = document.querySelector("#file_view");
const browseCats = document.querySelectorAll(".browse-cat");
const browseSidebar = document.querySelector("#browse_sidebar");

function changeBrowseType(cat) {
  const tabs = Array.from(browseCats).map(btn => btn.id.replace("browse-", ""));
  let activeIdx = tabs.findIndex(tabName =>
    document.querySelector(`.browse-${tabName}`).classList.contains("active")
  );

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

  if (cat !== 'all') {
    drawBrowse(settings[cat + "Path"]);
  }
}

function renderSidebar(file) {
  browseSidebar.innerHTML = '';


}

async function drawBrowse(path) {
  const contents = await self.read_folder(path);

  fileView.innerHTML = '';
  let html = '';
  contents.forEach(item => {
    if (item.type == 'folder') {
      html += `<div class="dir-item">${item.name}</div>`;
    } else if (item.type == 'file') {
      html += `<div class="dir-item">${item.name}</div>`;
    }
  });
  fileView.innerHTML = html;
}
