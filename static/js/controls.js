/* eslint-disable quotes */

document.addEventListener("keydown", function(event) {
  switch (event.key.toLowerCase()) {
    case "w":
      // Handle W key
      guy.emit('highlight_action', 'up');
      break;
    case "a":
      // Handle A key
      guy.emit('highlight_action', 'left');
      break;
    case "s":
      // Handle S key
      guy.emit('highlight_action', 'down');
      break;
    case "d":
      // Handle D key
      guy.emit('highlight_action', 'right');
      break;
    case "e":
      // Handle E key
      guy.emit('change_tab', 'right');
      break;
    case "q":
      // Handle Q key
      guy.emit('change_tab', 'left');
      break;
    case "arrowup":
      // Handle Up Arrow key
      self.expand_gui();
      break;
    case "arrowdown":
      // Handle Down Arrow key
      self.shrink_gui();
      break;
    case "1":
      //handle 1 key
      guy.emit('change_browse', 'left');
      break;
    case "3":
      //handle 3 key
      guy.emit('change_browse', 'right');
      break;
    case "backspace":
      guy.emit('go_back');
      break;
    case "enter":
      guy.emit('highlight_action', 'action1');
      break;
    case "p":
      guy.emit('focus_toggle');
      break;
    default:
      // Ignore other keys
      break;
  }
});

const controls = document.querySelector('#controls');

let highlightedAction = -1;
let activeArea = 'browse';

const actionableAreas = {'controls': {'class_name': '.ctrl-btn', 'cols': 'actionables.length', 'rows': '1',
  'action1': 'document.querySelector(".highlighted").click()'},
'browse': {'class_name': '.dir-item', 'cols': '1', 'rows': 'actionables.length',
  'focus': 'document.querySelector(".highlighted").click()',
  'action1': 'document.querySelectorAll(".highlighted button")[0]?.click()'}};

function highlightAction(direction) {
  const info = actionableAreas[activeArea];
  const actionables = document.querySelectorAll(info.class_name);
  let cols = eval(info.cols);
  let rows = eval(info.rows);

  let index = highlightedAction;

  // If one row, many columns (horizontal)
  if (rows === 1 && cols > 1) {
    if (direction === 'right') { index = Math.min(index + 1, cols - 1); }
    if (direction === 'left') { index = Math.max(index - 1, 0); }
    // Up/Down do nothing or could wrap/focus elsewhere
  }
  // If one column, many rows (vertical)
  else if (cols === 1 && rows > 1) {
    if (direction === 'down') { index = Math.min(index + 1, rows - 1); }
    if (direction === 'up') { index = Math.max(index - 1, 0); }
    // Left/Right do nothing or could wrap/focus elsewhere
  }
  // If grid (multiple rows and columns)
  else if (cols > 1 && rows > 1) {
    if (direction === 'down') { index = Math.min(index + cols, actionables.length - 1); }
    if (direction === 'up') { index = Math.max(index - cols, 0); }
    if (direction === 'right') { index = Math.min(index + 1, actionables.length - 1); }
    if (direction === 'left') { index = Math.max(index - 1, 0); }
  }

  actionables.forEach((item, i) => {
    item.classList.toggle('highlighted', i === index);
    if (i === index && activeArea === 'browse') {
      item.scrollIntoView({ block: 'center', behavior: 'smooth', container: 'nearest' });
    }
  });

  if ('focus' in info) { eval(info.focus); }
  if (direction === 'action1') { eval(info.action1); }
  if (direction === 'action2' && 'action2' in info) { eval(info.action2); }
  if (direction === 'action3' && 'action3' in info) { eval(info.action3); }

  highlightedAction = index;
}

function focusToggle(jump = false) {
  highlightAction = -1;

  const highlighted = document.querySelector('.highlighted');
  if (highlighted) {
    highlighted.classList.remove('highlighted');
  }

  if (activeArea !== 'controls' && !jump) {
    activeArea = 'controls';
    controls.classList.remove('unfocused');
  } else {
    const tabs = Array.from(tabBtns).map(btn => btn.id.replace("_btn", ""));
    let activeIdx = tabs.findIndex(tabName =>
      document.querySelector(`#${tabName}_btn`).classList.contains("active")
    );
    activeArea = tabs[activeIdx];
    controls.classList.add('unfocused');
  }
}
