pragma solidity ^0.4.19;
import "zeppelin-solidity/contracts/math/SafeMath.sol";
import 'zeppelin-solidity/contracts/ownership/Ownable.sol';


contract Escrow is Ownable{
    using SafeMath for uint256;

    uint256 public price;
    bool public confirmedPurchase;
    bool public confirmedReceived;
    bool public canceled;
    address public buyer;

    function Escrow() public payable {
        require (msg.value % 2 == 0);
        price = msg.value / 2;
    }

    function cancel() public onlyOwner {
        // the seller cancels created Smart Contract
        require(!confirmedPurchase && !confirmedReceived && !canceled);
        address self = address(this);
        owner.send(self.balance);
        canceled = true;
    }

    function confirmPurchase() payable public {
        require(!confirmedPurchase && !confirmedReceived && !canceled);
        require(msg.value == price * 2);
        confirmedPurchase = true;
        buyer = msg.sender;
    }

    function confirmReceived() public {
        require(confirmedPurchase && !confirmedReceived && !canceled);
        require(msg.sender == buyer);
        owner.send(price * 3);
        buyer.send(price);
        confirmedReceived = true;
    }
}