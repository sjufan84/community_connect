// SPDX-License-Identifier: MIT
pragma experimental ABIEncoderV2;
pragma solidity ^0.8.1;


import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/Counters.sol";


contract CommunityConnect {

    using SafeMath for uint;

    // Establishing counters for all of our lists
    using Counters for Counters.Counter;
    Counters.Counter private _cashRequests;
    Counters.Counter private _suppliesRequests;
    Counters.Counter private _rideRequests;
    Counters.Counter private _fillOffers;
    Counters.Counter private _authorizedCashRecipients;
    //Counters.Counter private _invoices;
    

    // holds the ETH address of the main customer
    // allows the account owner to receive withdrawal payments at their Ethereum address
    address nonProfit = 0x1A983C577B098b9C203D75cda21C984a365F93DB;
    address payable supplier;
    // This Ethereum address will represent a third-party account that's authorized to receive withdrawal payments.
    // @ TODO update way for outside wallets to access contract (javascript)
    address authorizedRecipient= 0x29f413f693525Cc5C7B9aBd8346F399641F2e852;
    // holds account balance
    uint256 public contractBalance;
    // address for approved supplier who fills the request
    address payable approvedSupplier;
    string supplierLocation;
    
    // cash request info
    address payable[] authorizedCashRecipients;
    uint256 newCashRecipientId;
    uint256 newCashRequestId;
    // invoice data
    uint256 invoiceNum;
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

    uint256 newSupplyRequestId;
    uint256 newFillOfferId;

    //Adding structs that can be mapped and hold variables related to our most common data types

    struct cashRequest {
        address cashRequestSender;
        uint256 cashRequestAmount;
        string cashRequestStatus;
        bool isApproved;
        bool isPaid;
        uint cashRequestId;
    }

    struct fillOffer {
        address payable offerSupplier;
        string supplierLocation;
        uint256 compensationRequested;
        uint256 compensationApproved;
        uint256 supplyRequestNumber;
        bool isApproved;
    }

    struct suppliesRequest {
        address supplyRequestOwner;
        string productName;
        string productType;
        uint256 productCount;
        string requestLocation;
        string requestStatus;
        uint256 supplyRequestId;
        bool isOffer;
        bool isFilled;
    }

    uint256 suppliesRequestsCount;

    struct invoice {
        uint256 invoiceNumber;
        uint256 compensationRequested;
        uint256 compensationApproved;
        address payable supplier;
        bool isPaid;
    }
    

    mapping(address => uint256) balances;
    mapping(uint256 => suppliesRequest) public SuppliesRequests;
    mapping(uint256 => cashRequest) public CashRequests;
    //mapping(uint256 => rideRequest) public RideRequests;
    mapping(uint256 => fillOffer) public FillOffers;
    mapping(uint256 => invoice) public Invoices;

    // adds ETH to smart contract.  include `payable` modifer so contract accepts ETH that gets sent to this function
    // Donors can send Eth to contract
    function deposit(uint256 donation) public payable {
        require(msg.value == donation);
        contractBalance = address(this).balance;
    }
  
     // This function allows Users to make supplies requests to the contract
    function registerRequest(address newRequestOwner, 
        string memory newName, 
        string memory newProductType, 
        uint256 newProductCount,
        string memory newRequestLocation
        ) public {
        newSupplyRequestId = _suppliesRequests.current();
        suppliesRequestsCount = newSupplyRequestId + 1;
        _suppliesRequests.increment();


        SuppliesRequests[newSupplyRequestId].supplyRequestOwner = newRequestOwner;
        SuppliesRequests[newSupplyRequestId].productName = newName;
        SuppliesRequests[newSupplyRequestId].productType = newProductType;
        SuppliesRequests[newSupplyRequestId].productCount = newProductCount;
        SuppliesRequests[newSupplyRequestId].supplyRequestId = newSupplyRequestId;
        SuppliesRequests[newSupplyRequestId].requestStatus = "Open";
        SuppliesRequests[newSupplyRequestId].requestLocation = newRequestLocation;
        SuppliesRequests[newSupplyRequestId].isOffer = false;
        SuppliesRequests[newSupplyRequestId].isFilled = false;
    }
    
    // This function allows Suppliers to see the requests made by Users
    function viewRequest(uint _supplyRequestNumber) view public returns ( 
            address, 
            string memory, 
            string memory, 
            uint256, 
            string memory,
            string memory,
            uint256
        ) {
        return (
            SuppliesRequests[_supplyRequestNumber].supplyRequestOwner, 
            SuppliesRequests[_supplyRequestNumber].productName, 
            SuppliesRequests[_supplyRequestNumber].productType, 
            SuppliesRequests[_supplyRequestNumber].productCount, 
            SuppliesRequests[_supplyRequestNumber].requestLocation,
            SuppliesRequests[_supplyRequestNumber].requestStatus,
            SuppliesRequests[_supplyRequestNumber].supplyRequestId
        );
    }

    function viewRequests() public view returns (suppliesRequest[] memory) {
        suppliesRequest[]    memory id = new suppliesRequest[](_suppliesRequests.current());
      for (uint i = 0; i < suppliesRequestsCount; i++) {
          suppliesRequest storage supplyRequest = SuppliesRequests[i];
          id[i] = supplyRequest;
      }
      return id;
    }

    // This function is a check for Suppliers to call when they agree to fill the request
    function offerFill(
            uint256 _supplyRequestNumber,
            address payable newSupplier, 
            uint256 _compensationRequested, 
            string memory newSupplierLocation
        ) public {
            _fillOffers.increment();
            newFillOfferId = _fillOffers.current();
            
            SuppliesRequests[_supplyRequestNumber].requestStatus = "Fill Offered";
            SuppliesRequests[_supplyRequestNumber].isOffer = true;
            
            FillOffers[newFillOfferId].offerSupplier = newSupplier;
            FillOffers[newFillOfferId].supplierLocation = newSupplierLocation;
            FillOffers[newFillOfferId].compensationRequested = _compensationRequested;
            FillOffers[newFillOfferId].supplyRequestNumber = _supplyRequestNumber;
            FillOffers[newFillOfferId].isApproved = false;
    }
    
    // Users can view request fill offers
    function viewFillOffers(uint256 _supplyRequestNumber, uint _fillOfferNumber) view public returns (
            address, 
            string memory, 
            uint256, 
            uint256, 
            bool
        ) {
            require (SuppliesRequests[_supplyRequestNumber].isOffer == true, "No fill offers to view");
            
            return (
            FillOffers[_fillOfferNumber].offerSupplier,
            FillOffers[_fillOfferNumber].supplierLocation,
            FillOffers[_fillOfferNumber].compensationRequested,
            FillOffers[_fillOfferNumber].supplyRequestNumber,
            FillOffers[_fillOfferNumber].isApproved
        );
    }

    // non-profit can approve fillOffer here
    function approveFillOffer(uint256 _fillOfferNumber) public {
        require(msg.sender == nonProfit, "You are not allowed to approve offers");
        
        FillOffers[_fillOfferNumber].isApproved = true;
        FillOffers[_fillOfferNumber].compensationApproved =  FillOffers[_fillOfferNumber].compensationRequested;
        invoiceNum = FillOffers[_fillOfferNumber].supplyRequestNumber;

        Invoices[invoiceNum].invoiceNumber = invoiceNum;
        Invoices[invoiceNum].compensationRequested = FillOffers[_fillOfferNumber].compensationRequested;
        Invoices[invoiceNum].compensationApproved = FillOffers[_fillOfferNumber].compensationApproved;
        Invoices[invoiceNum].supplier = FillOffers[_fillOfferNumber].offerSupplier;
        Invoices[invoiceNum].isPaid = false;
      
        SuppliesRequests[invoiceNum].requestStatus = "Fill Approved";
    }


    // This function allows the Nonprofit to see the invoice Suppliers have sent
    function viewInvoice(uint256 _invoiceNum) view public returns(uint256, uint256, uint256, address, bool) {
        return (
            Invoices[_invoiceNum].invoiceNumber,
            Invoices[_invoiceNum].compensationRequested,
            Invoices[_invoiceNum].compensationApproved, 
            Invoices[_invoiceNum].supplier,
            Invoices[_invoiceNum].isPaid
            );
    }

    function payInvoice(uint256 _invoiceNum) public payable {
        require(msg.sender == nonProfit, "You are not authorized to pay invoices");
        require (FillOffers[_invoiceNum].isApproved == true, "Fill offer has not been approved!");
        //require(received == true, "Order has not been received!");
        require (Invoices[_invoiceNum].compensationApproved <= address(this).balance, "Not enough money in contract to pay supplier");
        Invoices[_invoiceNum].supplier.transfer(Invoices[_invoiceNum].compensationApproved);
        contractBalance = contractBalance.sub(Invoices[_invoiceNum].compensationApproved);
        Invoices[_invoiceNum].isPaid = true;
        SuppliesRequests[_invoiceNum].requestStatus = "Request Filled";
    }


    function updateIPFSHash(string memory newHash) public {
        IPFSHash = newHash;
    }

    function getIPFSHash() view public returns (string memory) {
        return (IPFSHash);
    }

    function addAuthorizedCashRecipient(address payable _newRecipient) public {
        require (msg.sender == nonProfit, "You are not authorized to add cash recipients!");

        _authorizedCashRecipients.increment();
        newCashRecipientId = _authorizedCashRecipients.current();
        authorizedCashRecipients[newCashRecipientId] = _newRecipient;
    }

    function viewAuthorizedCashRecipients(uint _cashRecipientId) view public returns (address) {
        return authorizedCashRecipients[_cashRecipientId];
    }
        
    function newCashRequest(uint256 _cashRequestAmount, address payable _recipient, uint256 _recipientId) public {
        _cashRequests.increment();
        newCashRequestId = _cashRequests.current();
        require(authorizedCashRecipients[_recipientId] == _recipient, "You are not authorized to reqest cash assistance, please check with the system administrator for help."); 

        CashRequests[newCashRequestId].cashRequestSender = _recipient;
        CashRequests[newCashRequestId].cashRequestStatus = "Open";
        CashRequests[newCashRequestId].cashRequestAmount = _cashRequestAmount;
        CashRequests[newCashRequestId].isApproved = false;
        CashRequests[newCashRequestId].isPaid = false;
        CashRequests[newCashRequestId].cashRequestId = newCashRequestId;
    }
        
    
    function viewCashRequests(uint256 _cashRequestId) view public returns (address, string memory, uint256, bool, bool, uint256) {
        return (
            CashRequests[_cashRequestId].cashRequestSender,
            CashRequests[_cashRequestId].cashRequestStatus, 
            CashRequests[_cashRequestId].cashRequestAmount,
            CashRequests[_cashRequestId].isApproved,
            CashRequests[_cashRequestId].isPaid,
            CashRequests[_cashRequestId].cashRequestId
        );
    }

    // This function allows the nonprofit to send cash assistance to users
    function sendCash(uint256 _cashRequestAmount, address payable _recipient, uint256 _cashRequestId) public {
        require(msg.sender == nonProfit, "You are not authorized to send cash assistance");
        require(_recipient == CashRequests[_cashRequestId].cashRequestSender, "This is not the recipient who requested the funds!");
        require(_cashRequestAmount <= address(this).balance, " The Non-Profit does not have the available funds at this time!");
        _recipient.transfer(_cashRequestAmount);
    }  
    
    // accepts ETH even if it gets sent without using the `deposit` function
    //receive ether function receives ether if no other function is called and payment is sent
    //receive() external payable {}

    //fallback() external payable {}
} 

