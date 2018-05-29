pragma solidity ^0.4.21;

import "zeppelin-solidity/contracts/math/SafeMath.sol";
import "./ERC20.sol";

// doesn't work
// import "https://github.com/OpenZeppelin/openzeppelin-solidity/blob/master/contracts/token/ERC20/ERC20.sol";

contract Splitter {

    using SafeMath for uint256; // I don't really use safe math

    address [] beneficiares;
    mapping (address => uint256) withdrawable;

    address feeCollector;
    
    uint256 constant FEE = 1 finney;
    
    // ICON token
    ERC20 public token = ERC20(0xb5A5F22694352C15B00323844aD545ABb2B11028);

    event Splitted(address sender, uint256 value);

    function Splitter(address [] _beneficiares, address _feeCollector) public {
        require(_feeCollector > 0);
        require(_beneficiares.length > 0);

        beneficiares = _beneficiares;
        feeCollector = _feeCollector;
    }

    function split(uint256 overallValue) payable public {
        require(msg.value == FEE);
        require (overallValue > 0);
        require (overallValue % beneficiares.length == 0);
        require (token.allowance(msg.sender, this) > overallValue);

        
        feeCollector.transfer(msg.value);
        token.transferFrom(msg.sender, this, overallValue);
        
        uint256 value = overallValue.div(beneficiares.length);

        for (uint8 i=0; i < beneficiares.length; i++) {
            withdrawable[beneficiares[i]] = withdrawable[beneficiares[i]].add(value);
        }
    
        emit Splitted(msg.sender, value);
    }

    function withdraw(uint256 value) public {
        require(withdrawable[msg.sender] >= value);
        withdrawable[msg.sender] = withdrawable[msg.sender].sub(value);
        token.transfer(msg.sender, value);
    }
}