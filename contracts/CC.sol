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
    // address for approved supplier who fills the request
    address payable approvedSupplier;
    // request product info
    string productName;
    string productType;
    uint256 productCount;
    string requestStatus;
    // cash request info
    //address payable cashRecipient;
    uint256 cashRequested;
    // invoice data
    uint256 invoiceNumber;
    uint256 compensationRequested;
    uint256 compensationApproved;
    uint256 approvedInvoiceNumber;
    //booleans
    bool isOffer = false;
    bool isApproved = false;
    //bool isReceived = false;
    bool invoicePaid = false;
    bool cashRequestedStatus = false;

    mapping(address => uint) balances;

    // adds ETH to smart contract.  include `payable` modifer so contract accepts ETH that gets sent to this function
    // Donors can send Eth to contract
    function deposit(uint256 donation) public payable {
        require(msg.value == donation);
        contractBalance = address(this).balance;
    }
  
    // This function allows view of info
    /*function getInfo() view public returns(address, address payable, uint) {
        return (nonProfit, authorizedRecipient, contractBalance);
    }*/
    
    // This function allows Users to make requests to the contract
    function registerRequest(address payable newAccountOwner, string memory newName, string memory newProductType, uint256 newProductCount) public {
        accountOwner = newAccountOwner;
        productName = newName;
        productType = newProductType;
        productCount = newProductCount;
        requestStatus = "Open";
    }
    
    // This function allows Suppliers to see the requests made by Users
    function viewRequest() view public returns(address, string memory, string memory, uint256, string memory) {
        return (accountOwner, productName, productType, productCount, requestStatus);
    }

    
    // Just viewing the offer status of a request
    /*function getOfferStatus() view public returns(bool) {
        return isOffer;
    }*/
    
    // This function is a check for Suppliers to call when they agree to fill the request
    function fillRequest(address payable newSupplier, uint256 compensation, uint256 newInvoiceNumber) public returns(address, uint256, uint256) {
        isOffer = true;
        supplier = newSupplier;
        compensationRequested = compensation;
        invoiceNumber = newInvoiceNumber;
        requestStatus = "Fill Offered";

        return(supplier, compensationRequested, invoiceNumber);
    }
    
    // Users can view request fill offers
    function viewFillOffer() view public returns (address, uint256, uint256, string memory, string memory, uint256) {
        require(isOffer == true, "No fill offers to view");
        return (supplier, compensationRequested, invoiceNumber, productName, productType, productCount);
    }

    // non-profit can approve fillOffer here
    function approveFillOffer() public {
        require(msg.sender == nonProfit, "You are not allowed to approve offers");
        isApproved = true;
        compensationApproved = compensationRequested;
        approvedInvoiceNumber = invoiceNumber;
        approvedSupplier = supplier;
        requestStatus = "Fill Approved";
    }

    // This function allows the Nonprofit to see the invoice Suppliers have sent
    function viewApprovedInvoice() view public returns(address, uint256, uint256) {
        return (approvedSupplier, compensationApproved, approvedInvoiceNumber);
    }
    
    // user signifies they received the goods/service
    /*function userReceived() public {
        require (msg.sender == accountOwner || msg.sender == nonProfit, "You are not approved to receive this order");
        isReceived=true;
    }*/
    
    // view received status 
    /*function getReceivedStatus() view public returns(bool) {
        return isReceived;
    }*/

    // This function allows the Nonprofit to pay the Supplier, I think we should change this to the Nonprofit sends the money but it comes from contract 
    function payInvoice(uint256 invoiceNum, bool received) public payable {
        require (invoiceNum == approvedInvoiceNumber, "This invoice number has not been approved");
        require(msg.sender == nonProfit, "You are not authorized to pay invoices");
        require (isApproved == true, "Fill offer has not been approved!");
        require(received == true, "Order has not been received!");
        require(compensationApproved <= address(this).balance, "Not enough money in contract to pay supplier");
        approvedSupplier.transfer(compensationRequested);
        contractBalance -= compensationApproved;
        invoicePaid = true;
        requestStatus = "Request Filled";
    }


    function update IPFSHash (string memory hash) public {
        IPFSHash = hash;
    }

    function getIPFSHash () view public returns (string memory) {
        return (IPFSHash);
    }

    // viewer function to see invoice payment status
    /*function getPaidStatus() view public returns (bool) {
        return invoicePaid;
    }
    
    // This function allows Users to make requests of cash to the contract
    function requestCash(address payable, uint256 amount) public {
        cashRequested = amount;
        cashRequestStatus = true;
    }
    function viewCashRequest() view public returns (address, uint256, bool) {
        return (authorizedRecipient, cashRequested, cashRequestStatus);
    }


    // This function allows the nonprofit to send cash assistance to users
    function sendRemittance(address payable recipient) public {
        require(msg.sender == nonProfit && recipient == authorizedRecipient, "The recipient address is not authorized!");
        require(cashRequestStatus == true, "This request is not open!");
        cashRequestStatus = false;
        recipient.transfer(value);
        contractBalance = address(this).balance;
    }    
    
    // accepts ETH even if it gets sent without using the `deposit` function
    function() external payable {}
}

// Flow of Operations
// User enters there request with registerRequest
// Supplier can see there request with viewRequest call
// Supplier agrees to fill Request with fillRequest(bool), then enters inputs to sendInvoice function
// Nonprofit can view the invoice with viewInvoice call
// Nonprofit can see the suppliers invoice, check to see if the amount in invoice == amount in viewRequest, check to see if user received the goods with getReceivedStatus
// Nonprofit sends compensation that equals the amount in invoice