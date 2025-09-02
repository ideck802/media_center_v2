/* eslint-disable quotes */

document.addEventListener("keydown", function(event) {
  switch (event.key.toLowerCase()) {
    case "w":
      // Handle W key
      console.log("W pressed");
      break;
    case "a":
      // Handle A key
      console.log("A pressed");
      break;
    case "s":
      // Handle S key
      console.log("S pressed");
      break;
    case "d":
      // Handle D key
      console.log("D pressed");
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
    default:
      // Ignore other keys
      break;
  }
});
