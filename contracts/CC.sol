pragma solidity ^0.5.0;

contract CommunityConnect {
    // holds the ETH address of the main customer
    // allows the account owner to receive withdrawal payments at their Ethereum address
    address payable nonProfit = 0x6A11B707EcAE548501Ba9ab92a114C4b98378A08;
    // holds account balance
    uint public contractBalance;
    // This Ethereum address will represent a third-party account that's authorized to receive withdrawal payments.
    address payable authorizedRecipient= 0x29f413f693525Cc5C7B9aBd8346F399641F2e852;
    address payable accountOwner;
    string name;
    string productType;
    uint256 productCount;
    
    mapping(address => uint) balances;

    function getInfo() view public returns(address, address payable, uint) {
        return (nonProfit, authorizedRecipient, contractBalance);
    }

    function registerRequest(address payable newAccountOwner, string memory newName, string memory newProductType, uint256 newProductCount) public {
        accountOwner = newAccountOwner;
        name = newName;
        productType = newProductType;
        productCount = newProductCount;
    }
    
    function viewRequest() view public returns(address, string memory, string memory, uint256) {
        return (accountOwner, name, productType, productCount);
    }

        function sendRemittance(uint amount, address payable recipient) public {
        // enforce rule that only the account owner or the authorized recipient can receive either from the contract balance
        require(recipient == nonProfit || recipient == authorizedRecipient, "The recipient address is not authorized!");
        recipient.transfer(amount);
        contractBalance = address(this).balance;
    }

    // adds ETH to smart contract.  include `payable` modifer so contract accepts ETH that gets sent to this function
    function deposit(uint256 amount) public payable {
        require(msg.value == amount);
        contractBalance = address(this).balance;
    }

    function getBalance(address recipient) public view returns(uint256) {
        //return balances[recipient];
        return address(recipient).balance;
    }
    /*function requestFood() public {
    }
    recipient.balance+=amount
    function requestRide() public {
    }
    function requestGoods() public {
    } 
    */

    function sendCash(uint amount, address payable recipient) public {
        require(recipient == authorizedRecipient, "This address is not authorized to receive cash assistance!");
        nonProfit.transfer(amount);
        contractBalance = address(this).balance;
    }

    // accepts ETH even if it gets sent without using the `deposit` function
    function() external payable {}
}