/* eslint-disable quotes */

const playingCont = document.querySelector("#playing_cont");
const playingNotif = document.querySelector("#playing_notif");

async function renderPlaylist() {
  const playlist = await self.get_playlist();
  playingCont.innerHTML = '';
  let html = ``;

  if (playlist.length === 0) {
    html += `<p class="no-media">No media in playlist</p>`;
  } else {
    playlist.forEach((item) => {
      html += `<div class="media-item ${item.isPlaying ? 'playing' : ''}">
        <p>${item.name}</p>
      </div>`;
    });
  }

  playingCont.innerHTML = html;
}

function renderPlayingNotif(media) {
  playingNotif.innerHTML = '';
  let html = `<div class='marquee'>
    <p class="media-name">${media}</p>
  </div>`;

  playingNotif.innerHTML = html;
  playingNotif.style.display = 'flex';
}

function hidePlayingNotif() {
  playingNotif.style.display = 'none';
}
