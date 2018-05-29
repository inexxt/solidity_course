pragma solidity ^0.4.19;

import 'https://github.com/OpenZeppelin/openzeppelin-solidity/blob/master/contracts/ownership/Ownable.sol';
import 'https://github.com/OpenZeppelin/openzeppelin-solidity/blob/master/contracts/math/SafeMath.sol'

contract StateChannel is Ownable {
    uint256 PUNISHMENT = 1 ether;  // TODO should be ~10% of value - solidity doesnt have floats, so better to do it that way
    uint256 MINVAL = 1 ether;  // minimal value
    uint256 LIFETIME = 100;  // channels can be closed after 100 blocks
    bool ACCEPTING_NEW_CHANNELS;

    enum Stage {
        WaitingForOwnerToDeposit, // if owner won't deposit after exiting_after, contract finishes
        Open,
        WaitingForChallengeByClient,
        WaitingForChallengeByOwner,
        Finished
    }

    struct StateS {
        Stage stage;
        uint256 cap;
        uint256 created_on;
        uint256 closed_at;
        bytes32 pubic_key;
    }

    mapping (address => uint256) available_channel; // since one user can have multiple channels, this mapping the minimal available number
    mapping (address => mapping (uint256 => StateS)) state;  // The client is responsible for the number - he get's it after initialization

    event CreatedChannel(address creator, uint256 cap, bytes32 public_key, uint256 closed_at, uint256 channel_number)

    // modifier atStage(uint256 channel_num, Stage _stage) {
    //     require(state[msg.sender][channel_num].stage == _stage);
    //     _;
    // }

    modifier acceptingNewChannels() {
        require(ACCEPTING_NEW_CHANNELS);
        _;
    }

    function StateChannel(bool _ACCEPTING_NEW_CHANNELS) public payable {
        change_acceptance_status(_ACCEPTING_NEW_CHANNELS);
    }

    function change_acceptance_status(bool _ACCEPTING_NEW_CHANNELS) public onlyOwner {
	    ACCEPTING_NEW_CHANNELS = _ACCEPTING_NEW_CHANNELS;
    }

    function createNewChannel(uint256 cap, bytes32 public_key) public payable acceptingNewChannels returns(uint256) {
        require (msg.value == cap + PUNISHMENT);
        uint256 number = available_channel[msg.sender];
        available_channel[msg.sender] = number + 1;
        state[msg.sender][number] = StateS({
        	stage: Stage.WaitingForOwnerToDeposit, 
        	cap: cap,
        	closed_at: block.number + LIFETIME,
        	public_key: public_key
        });

        CreatedChannel(msg.sender, cap, public_key, block.number + LIFETIME, number)
    }

    function acceptNewChannel(address user, uint256 channel_number) public payable onlyOwner {
    	require (state[user][channel_number].stage == Stage.WaitingForOwnerToDeposit);
    	require (msg.value == PUNISHMENT);
    	state[user][channel_number].state = Stage.Open;
    }

    function closeChannelByUser (uint256 channel_number) public {
    	require (state[msg.sender][channel_number].stage == Stage.Open);
    	//TODO
    }

    function closeChannelByOwner (address user, uint256 channel_number) public onlyOwner {
    	require (state[user][channel_number].stage == Stage.Open);
    	//TODO
    }

    
    
    function verify_merkle_proof(bytes32[10] proof, bytes32 root, bytes32 leaf) pure returns(bool) {
        bytes32 curr_hash = keccak256(leaf);
        for (uint i = 0; i < proof.length; i++) {
            curr_hash = keccak256(curr_hash, proof[i]);
        }
        return (root == curr_hash);
    }    
} 