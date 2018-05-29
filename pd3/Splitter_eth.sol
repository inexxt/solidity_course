contract Splitter {
    address benficary1;
    
    address benficary2;
    function Splitter(address _benficary1, address _benficary2) public {
        benficary1 = _benficary1;
        benficary2 = _benficary2;
    }
    function () payable public {
        uint amount = msg.value / 2;
        benficary1.transfer(amount);
        benficary2.transfer(msg.value - amount);
    }
}