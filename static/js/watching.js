/* eslint-disable dot-notation */

/* ---------------------------------------
              MOVE TO PYTHON
      AND PREVENT IF NOT MOVIE OR SHOW
----------------------------------------*/


let watchedList = null;

function getWatchedName(name, type = null) {
  if (type == 's') {
    // if its a season
    return name.toLowerCase().replace('season ', 's');
  } else if (type == 'e') {
    // if its an episode
    const episodeNum = name.replace(/.*?e(\d+).*/i, '$1');
    return `e${episodeNum}`;
  } else {
    return name.toLowerCase().replace(/\.[^/.]+$/, '').replaceAll(' ', '-').replaceAll("'", '');
  }
}
