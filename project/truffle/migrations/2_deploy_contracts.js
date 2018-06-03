var Ownable = artifacts.require("./Ownable.sol");
var SafeMath = artifacts.require("./SafeMath.sol");

var StateChannel = artifacts.require("./StateChannel.sol");

module.exports = function(deployer) {
  deployer.deploy(Ownable);
  deployer.deploy(SafeMath);
  deployer.link(Ownable, StateChannel);
  deployer.link(SafeMath, StateChannel);
  
  deployer.deploy(StateChannel, true);
};
