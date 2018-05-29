pragma solidity ^0.4.21;

import "zeppelin-solidity/contracts/math/SafeMath.sol";
import "./ERC20.sol";

// doesn't work
// import "https://github.com/OpenZeppelin/openzeppelin-solidity/blob/master/contracts/token/ERC20/ERC20.sol";
// import "https://github.com/OpenZeppelin/openzeppelin-solidity/blob/master/contracts/token/ERC20/ERC20.sol";

contract Splitter {

    using SafeMath for uint256; // I don't really use safe math

    address [] beneficiares;
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
        
        for (uint8 i=0; i < beneficiares.length; i++) {

	        // this is not needed, since div implements just normal /
            token.transferFrom(
            	msg.sender, 
            	beneficiares[i], 
            	overallValue.div(beneficiares.length));
        }

        emit Splitted(msg.sender, value);
    }
}