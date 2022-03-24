// SPDX-License-Identifier: MIT


pragma solidity ^0.8.1;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract CommunityConnect {
    using SafeMath for uint;
    // holds the ETH address of the main customer
    // allows the account owner to receive withdrawal payments at their Ethereum address
    address nonProfit = 0x6A11B707EcAE548501Ba9ab92a114C4b98378A08;
    address payable supplier;
    // This Ethereum address will represent a third-party account that's authorized to receive withdrawal payments.
    address authorizedRecipient= 0x29f413f693525Cc5C7B9aBd8346F399641F2e852;
    // holds the ETH address of the main customer
    address requestOwner;
    // holds account balance
    uint256 public contractBalance;
    // address for approved supplier who fills the request
    address payable approvedSupplier;
    string supplierLocation;
    // request product info
    string productName;
    string productType;
    uint256 productCount;
    string requestStatus;
    string requestLocation;
    // cash request info
    address payable cashRecipient;
    uint256 cashRequested;
    string cashRequestStatus;
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
    //IPFS hash string
    string IPFSHash;

    mapping(address => uint256) balances;

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
    function registerRequest(address newRequestOwner, 
        string memory newName, 
        string memory newProductType, 
        uint256 newProductCount,
        string memory newRequestLocation
        ) public {
        requestOwner = newRequestOwner;
        productName = newName;
        productType = newProductType;
        productCount = newProductCount;
        requestLocation=newRequestLocation;
        requestStatus = "Open";
    }
    
    // This function allows Suppliers to see the requests made by Users
    function viewRequest() view public returns ( 
            address, 
            string memory, 
            string memory, 
            uint256, 
            string memory,
            string memory
        ) {
        return (
            requestOwner, 
            productName, 
            productType, 
            productCount, 
            requestLocation,
            requestStatus 
        );
    }

    
    // Just viewing the offer status of a request
    /*function getOfferStatus() view public returns(bool) {
        return isOffer;
    }*/
    
    // This function is a check for Suppliers to call when they agree to fill the request
    function fillRequest(
            address payable newSupplier, 
            uint256 compensation, 
            uint256 newInvoiceNumber
            //string memory newSupplierLocation
        ) public returns (
            address, 
            uint256, 
            uint256
        ) {
            isOffer = true;
            supplier = newSupplier;
            compensationRequested = compensation;
            invoiceNumber = newInvoiceNumber;
            requestStatus = "Fill Offered";
            //supplierLocation = newSupplierLocation;

        return(supplier, compensationRequested, invoiceNumber);
    }
    
    // Users can view request fill offers
    function viewFillOffer() view public returns (
            address, 
            uint256, 
            uint256, 
            string memory, 
            string memory, 
            uint256
        ) {
            require (isOffer == true, "No fill offers to view");
        return (
            supplier, 
            compensationRequested, 
            invoiceNumber, 
            productName, 
            productType, 
            productCount
        );
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
        contractBalance = contractBalance.sub(compensationApproved);
        invoicePaid = true;
        requestStatus = "Request Filled";
    }


    function updateIPFSHash(string memory newHash) public {
        IPFSHash = newHash;
    }

    function getIPFSHash() view public returns (string memory) {
        return (IPFSHash);
    }

    // viewer function to see invoice payment status
    /*function getPaidStatus() view public returns (bool) {
        return invoicePaid;
    }*/
    function requestCash(address payable recipient, uint cashAmount) public {
        require (recipient == authorizedRecipient, "You are not authorized to receive cash");
        require(cashAmount <= address(this).balance);
        cashRecipient = recipient;
        cashRequested = cashAmount;
        cashRequestStatus = "open";
    }    
    
    
    function viewCashRequest() view public returns (address, uint256, string memory) {
        return (cashRecipient, cashRequested, cashRequestStatus);
    }

    // This function allows the nonprofit to send cash assistance to users
    function sendCash(uint value, address payable recipient, address sender) public {
        require(sender == nonProfit && recipient == authorizedRecipient, "The recipient address is not authorized!");
        require(value <= address(this).balance, " The Non-Profit does not have the available funds at this time!");
        recipient.transfer(value);
        //contractBalance = address(this).balance;
    }    
    
    // accepts ETH even if it gets sent without using the `deposit` function
    fallback() external payable {}
}