function Player(name, marker) {
  this.name = name;
  this.marker = marker;
  this.sayName = function() {
    console.log(this.name);
  }
}

const playerOne = new Player("Tim", "X");
const playerTwo = new Player("Jen", "O");

function printName(player) {
  console.log(player.name);
}

function gameOver(winningPlayer){
  console.log("Congratulations!");
  console.log(winningPlayer.name + " is the winner!");
}

playerOne.sayName();