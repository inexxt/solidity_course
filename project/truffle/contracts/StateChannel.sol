pragma solidity ^0.4.23;

// import 'https://github.com/OpenZeppelin/openzeppelin-solidity/contracts/ownership/Ownable.sol';
// import 'https://github.com/OpenZeppelin/openzeppelin-solidity/contracts/math/SafeMath.sol';

import './Ownable.sol';
import './SafeMath.sol';


contract StateChannel is Ownable {

	using SafeMath for uint256; // TODO

    uint256 public constant PUNISHMENT = 1 ether;  // TODO should be ~10% of value - solidity doesnt have floats, so better to do it that way
    uint256 public constant WAITING_PERIOD = 10; // 4 * 2880;  // after "close" call, we're waiting ~48h for challenge (new block appears - on average - every 15 seconds)
    bool public accepting_new_channels = true;

    enum Stage {
        Open,
        WaitingForChallengeByOwner,
        Closed
    }

    struct StateS {
        Stage stage;
        uint256 cap;
        uint256 closed_at;
        uint256 funds_used;
    }

    mapping (address => uint256) public available_channel; // since one user can have multiple channels, this mapping holds the minimal available number
    mapping (address => mapping (uint256 => StateS)) public state;  // the client is responsible for remembering the number - he get's it after initialization

    event CreatedChannel(address user, uint256 channel_number, uint256 cap);

    constructor(bool _accepting_new_channels) public payable {
        changeAcceptanceStatus(_accepting_new_channels);
    }

    function changeAcceptanceStatus(bool _accepting_new_channels) public onlyOwner {
        accepting_new_channels = _accepting_new_channels;
    }

    function createNewChannel(uint256 cap) public payable returns(uint256) {
        require (msg.value == (cap + PUNISHMENT));
        // require (accepting_new_channels);

        uint256 channel_number = available_channel[msg.sender];
        available_channel[msg.sender] = channel_number + 1;
        state[msg.sender][channel_number] = StateS({
            stage: Stage.Open, 
            cap: cap,
            closed_at: 0,
            funds_used: 0
        });

        emit CreatedChannel(msg.sender, channel_number, cap);
        return channel_number;
    }

    function startClosingByUser (uint256 channel_number, uint256 funds_used) public {
        StateS storage st = state[msg.sender][channel_number];

        require (st.stage == Stage.Open);

        st.funds_used = funds_used;
        st.closed_at = block.number + WAITING_PERIOD;
        st.stage = Stage.WaitingForChallengeByOwner;
    }

    function closeByOwner (
        address user, 
        uint256 channel_number, 
        uint256 funds_used, 
        uint8 v, 
        bytes32 r, 
        bytes32 s) public onlyOwner {
        StateS storage st = state[user][channel_number];

        require (st.stage == Stage.Open);
        require (verifyReceipt(funds_used, user, channel_number, v, r, s));
        
        st.stage = Stage.Closed;

        uint256 funds_left = st.cap - funds_used;
        
        owner.transfer(funds_used);
        user.transfer(funds_left + PUNISHMENT);  // return PUNISHMENT to user, since he didn't cheat
    }
    
    function challengeByOwner (address user, 
        uint256 channel_number, 
        uint256 funds_used, 
        uint8 v, 
        bytes32 r, 
        bytes32 s) public {
    	StateS storage st = state[user][channel_number];

    	require (st.stage == Stage.WaitingForChallengeByOwner);
    	require (st.funds_used < funds_used);  // we can only challenge if we propose higher funds_used
    	require (st.cap >= funds_used); // and we can only propose lower funds than cap
        require (verifyReceipt(funds_used, user, channel_number, v, r, s));

        st.stage = Stage.Closed;
        
        // It appears the owner is right - user should then pay PUNISHMENT and return funds to user
        uint256 funds_left = st.cap - funds_used;
        
        owner.transfer(funds_used + PUNISHMENT);
        user.transfer(funds_left);
    }

    function closeByUser (uint256 channel_number) public {
        StateS storage st = state[msg.sender][channel_number];

        require (st.stage == Stage.WaitingForChallengeByOwner);
        require (st.closed_at < block.number);
        
        st.stage = Stage.Closed;

        // It appears the user didn't cheat
        uint256 funds_left = st.cap - st.funds_used;
        
        owner.transfer(st.funds_used);
        msg.sender.transfer(funds_left + PUNISHMENT);
    }
    
    function verifyReceipt (
        uint256 funds_used, 
        address user, 
        uint256 channel_number, 
        uint8 v, 
        bytes32 r, 
        bytes32 s) public view returns(bool) {

        require (state[user][channel_number].cap >= funds_used);

        // converting everything to uint256 because otherwise nothing works
        return verify(hash(uint256(funds_used), uint256(user), uint256(channel_number)), v, r, s) == user;
    }

    function hash(uint256 funds_used, uint256 user, uint256 channel_number) public pure returns(bytes32) {
        return sha3(funds_used, user, channel_number);
    }

    function verify(bytes32 message, uint8 v, bytes32 r, bytes32 s) public pure returns(address) {
        bytes memory prefix = "\x19Ethereum Signed Message:\n32";
        bytes32 prefixedHash = sha3(prefix, message);
        address addr = ecrecover(prefixedHash, v, r, s);
        return addr;
    }
}