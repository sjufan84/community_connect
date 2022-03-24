// contracts/cc_cashRequestTokens.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.1;
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";


contract CashRequest is ERC721URIStorage {
    using Counters for Counters.Counter;
    Counters.Counter private _cashRequestIds;

    constructor() ERC721("CashRequest", "CASH") public {
    }

    struct cashRequest {
        address payable cashRequestOwner;
        uint256 cashRequestAmount;
        string cashRequestStatus;
        string cashRequestURI;
        bool isApproved;
        bool isPaid;
        uint cashRequestId;
    }
    
    mapping(uint256 => cashRequest) public CashRequests;
    
    function newCashRequest(address payable recipient, string memory requestURI) public returns (uint256) {
        _cashRequestIds.increment();

        uint256 newCashRequestId = _cashRequestIds.current();
        _mint(recipient, newCashRequestId);
        _setTokenURI(newCashRequestId, requestURI);

        CashRequests[newCashRequestId].cashRequestOwner = recipient;
        CashRequests[newCashRequestId].cashRequestStatus = "Open";
        CashRequests[newCashRequestId].cashRequestURI = requestURI;
        CashRequests[newCashRequestId].isApproved = false;
        CashRequests[newCashRequestId].isPaid = false;
        CashRequests[newCashRequestId].cashRequestId = newCashRequestId;

        return newCashRequestId;
    }
}