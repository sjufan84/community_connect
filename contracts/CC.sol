pragma solidity ^0.5.0;

import "github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/math/SafeMath.sol";
contract CommunityConnect {
    using SafeMath for uint;
    // holds the ETH address of the main customer
    // allows the account owner to receive withdrawal payments at their Ethereum address
    address payable nonProfit = 0x6A11B707EcAE548501Ba9ab92a114C4b98378A08;
    address payable supplier = 0x2c8e3e5EC4064612d4936970dc27e2d930f78245;
    // This Ethereum address will represent a third-party account that's authorized to receive withdrawal payments.
    address payable authorizedRecipient= 0x29f413f693525Cc5C7B9aBd8346F399641F2e852;
    // holds the ETH address of the main customer
    address payable accountOwner;
    // holds account balance
    uint public contractBalance;
    string name;
    string productType;
    uint256 productCount;
    uint256 amount;
    uint256 invoiceNumber;
    bool _isFill = false;


    mapping(address => uint) balances;

    // adds ETH to smart contract.  include `payable` modifer so contract accepts ETH that gets sent to this function
    // Donors can send Eth to contract
    function deposit(uint256 donation) public payable {
        require(msg.value == donation);
        contractBalance = address(this).balance;
    }
    
    // This function allows anyone to check the balance of any address
    function getBalance(address recipient) public view returns(uint256) {
        //return balances[recipient];
        return address(recipient).balance;
    }
    // This function allows view of info
    function getInfo() view public returns(address, address payable, uint) {
        return (nonProfit, authorizedRecipient, contractBalance);
    }
    // This function allows Users to make requests to the contract
    function registerRequest(address payable newAccountOwner, string memory newName, string memory newProductType, uint256 newProductCount) public {
        accountOwner = newAccountOwner;
        name = newName;
        productType = newProductType;
        productCount = newProductCount;
    }
    // This function allows Suppliers to see the requests made by Users
    function viewRequest() view public returns(address, string memory, string memory, uint256) {
        return (accountOwner, name, productType, productCount);
    }
    // This function is a check for Suppliers to call when they agree to fill the request
    function fillRequest() public {
        _isFill = true;
    }
    // This function allows the Nonprofit to send cash assistance to users, I think we should change this to the contract sends cash to users
    function sendRemittance(uint value, address payable recipient, address sender) public {
    require(sender == nonProfit && recipient == authorizedRecipient, "The recipient address is not authorized!");
    recipient.transfer(value);
    contractBalance = address(this).balance;
    }
    // This function allows the Suppliers to send an invoice to contract
     function sendInvoice(address payable newSupplier, uint256 newAmount, uint256 newInvoiceNumber) public {
        require(_isFill == true);
        supplier = newSupplier;
        amount = newAmount;
        invoiceNumber = newInvoiceNumber;
        
    }
    // This function allows the Nonprofit to see the invoice Suppliers have sent
    function viewInvoice() view public returns(address, uint256, uint256) {
        return (supplier, amount, invoiceNumber);
    }
    // This function allows the Nonprofit to pay the Supplier, I think we should change this to the Nonprofit sends the money but it comes from contract 
    function payInvoice(uint value, address payable recipient) public payable{
        require(recipient == supplier, "This address is not authorized to receive cash assistance!");
        nonProfit.transfer(value);
        
    }
    
    // accepts ETH even if it gets sent without using the `deposit` function
    function() external payable {}
}
// User enters there request with registerRequest
// Supplier can see there request
// Supplier agrees to fillRequest
// Supplier fills out the invoice with sendInvoice
// Nonprofit can see the suppliers invoice 
=======
// Nonprofit sends compensation

