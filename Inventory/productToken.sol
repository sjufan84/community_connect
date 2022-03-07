pragma solidity ^0.5.5;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721Full.sol";

contract ProductInventory is ERC721Full {
    constructor() public ERC721Full("ProductInventory", "INV") {}

    struct Product {
        string name;
        string productType;
        uint256 productCost;
        string productLocation;
        // bool isAvailable;
        // bool isDeliverable;
        uint productCount;
        string uploadDate;
        //string claimDate;
        //address payable owner;

    }

    mapping(uint256 => Product) public inventory;

    // event Appraisal(uint256 token_id, uint256 appraisalValue, string reportURI);

    function registerProduct(
        address payable owner,
        string memory name,
        string memory productType,
        uint256 productCost,
        string memory productLocation,
        uint productCount,
        string memory uploadDate,
        string memory TokenURI
       // string memory claimDate
    ) public returns (uint256) {
        uint256 TokenId = totalSupply();

        _mint(owner, TokenId);
        _setTokenURI(TokenId, TokenURI);

        inventory[TokenId] = Product(name, productType,
            productCost, productLocation, productCount, uploadDate);
        
        return TokenId;
    }

    /*function claimItem(
        uint256 productId,
        uint256 payment,
        string memory productURI;
    ) public returns (uint256) {
        inventory[productId].productCount.sub(1);
        inventory[productId].claimDate = timestamp.now;
        inventory[productId].claimLocation = address of pantry. 


        emit Appraisal(tokenId, newAppraisalValue, reportURI);

        return artCollection[tokenId].appraisalValue;
    } */
}