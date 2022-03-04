pragma solidity ^0.5.0;

contract CommunityConnect {
    address payable nonProfit = 0x6A11B707EcAE548501Ba9ab92a114C4b98378A08;
    address payable authorizedRecipient = 0x29f413f693525Cc5C7B9aBd8346F399641F2e852;
    uint public accountBalance;

    function requestFood() public {

    }
    
    function requestRide() public {

    }


    function requestGoods() public {

    } 

    function sendCash(uint amount, address payable recipient) public {
        require(recipient == authorizedRecipient, "This address is not authorized to receive cash assistance!");
        nonProfit.transfer(amount);
        accountBalance = address(this).balance;
    }

     function deposit() public payable {
        accountBalance = address(this).balance;
    }

    function() external payable {}
    } 
