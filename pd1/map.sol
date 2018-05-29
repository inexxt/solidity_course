pragma solidity ^0.4.21;
import 'zeppelin-solidity/contracts/ownership/Ownable.sol';


// probably sth like https://github.com/ethereum/dapp-bin/blob/master/library/iterable_mapping.sol

contract Map is Ownable{
    bytes32[] public keys;
    uint8 public size;

    mapping(bytes32 => bytes32) public map;
    
    function pos_in_map(bytes32 key) public view returns (int8) {
        for (int8 i = 0; i<size; i++) {
            if (keys[i] == key) { return i; }
        }
        return -1;
    }
            
    function add(bytes32 key, bytes32 val) public onlyOwner {
        int8 pos = pos_in_map(key);
        require(pos == -1);
        keys.push(key)
        map[key] = val;
        size += 1;
    }
    
    function modify(bytes32 key, bytes32 val) public onlyKeys(key) {
        int8 pos = pos_in_map(key);
        require(pos > 0);
        map[key] = val;
    }
    
    function get(bytes32 key) public view returns (bytes32) {
        int8 pos = pos_in_map(key);
        require(pos > 0);
        return map[key];
    }
}