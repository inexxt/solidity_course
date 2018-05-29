pragma solidity ^0.4.19;
import "./SafeMath.sol";
// import 'https://github.com/OpenZeppelin/openzeppelin-solidity/blob/master/contracts/ownership/Ownable.sol';
import 'zeppelin-solidity/contracts/ownership/Ownable.sol';


contract Game is Ownable{
    using SafeMath for uint256;

    enum Stage {
        WaitingForPlayer2,
        WaitingForPlayer1Guess,
        WaitingForPlayer2Proof,
        Finished
    }

    Stage public stage;
    uint256 public starting_block; 
    address public player2;
    bytes32 public merkle_root; 
    uint256 public player1_guess;

    modifier atStage(Stage _stage) {
        require(stage == _stage);
        _;
    }

    function Escrow() public payable {
        require (msg.value == 2 ether);
        stage = Stage.WaitingForPlayer2;
    }

    function challenge(bytes32 _merkle_root) public payable atStage(Stage.WaitingForPlayer2){
    	require(msg.value == 2 ether); // I think that was the puropose
    	player2 = msg.sender;
    	merkle_root = _merkle_root;
    	stage = Stage.WaitingForPlayer1Guess;
    }

    function guess(uint256 _player1_guess) public onlyOwner atStage(Stage.WaitingForPlayer1Guess) {
    	require(_player1_guess >= 0 && _player1_guess < 2048);
    	player1_guess = _player1_guess;
        starting_block = block.number;
    	stage = Stage.WaitingForPlayer2Proof;
    }

    function player2_withdraw(bytes32[10] proof) public atStage(Stage.WaitingForPlayer2Proof) {
    	require(msg.sender == player2);
    	require(block.number.sub(starting_block) <= 256);
        require(verify_merkle_proof(proof, merkle_root, keccak256(player1_guess)));
        
        player2.transfer(4 ether);
        stage = Stage.Finished;
    }

    function player1_withdraw() onlyOwner atStage(Stage.WaitingForPlayer2Proof) {
    	require(block.number.sub(starting_block) > 256);
    	owner.transfer(4 ether);
    	stage = Stage.Finished;
    }
    

    function verify_merkle_proof(bytes32[10] proof, bytes32 root, bytes32 leaf) pure returns(bool) {
    	bytes32 curr_hash = keccak256(leaf);
    	for (uint i = 0; i < proof.length; i++) {
    		curr_hash = keccak256(curr_hash, proof[i]);
    	}
    	return (root == curr_hash);
    }
}