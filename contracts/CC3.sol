// SPDX-License-Identifier: MIT
pragma experimental ABIEncoderV2;
pragma solidity ^0.8.1;


import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/Counters.sol";


contract CommunityConnect is AccessControl {

    // establishing role frameworks for later use
    bytes32 public constant OWNER_ROLE = keccak256("OWNER_ROLE");
    bytes32 public constant MANAGER_ROLE = keccak256("MANAGER_ROLE");
    bytes32 public constant PROVIDER_ROLE = keccak256("PROVIDER_ROLE");
    bytes32 public constant PATIENT_ROLE = keccak256("PATIENT_ROLE");
    bytes32 public constant NEW_PROVIDER_ROLE = keccak256("NEW_PROVIDER_ROLE");



    // establishing iterable lists for access later
    address payable[] _ownersList;
    address payable[] _managersList;
    address payable[] _providersList;
    

    // initially establish the owner of the contract and give them the owner role
    constructor () {
        address payable contractOwner = payable(msg.sender);
        _setupRole(OWNER_ROLE, contractOwner);
        _ownersList.push(contractOwner);
    }

    using SafeMath for uint;

    // Establishing counters for all of our lists
    using Counters for Counters.Counter;
    Counters.Counter private _patientsCount;
    Counters.Counter private _requestsCount;
    //Counters.Counter private _providersCount;
    //Counters.Counter private _authorizedCashRecipients;
    //Counters.Counter private _invoices;

    
    // structs for commonly used data types
    struct Patient {
        bool _needsDelivery;
        string _patientLocation;
        //address payable patientWallet;
        bool _doesConsent;
        string _deliveryReason;
        bool _isQuarantined;
        string _preferredLanguage;
        string _patientName;
        uint _patientAge;
        string _patientPhoneNumber;
        string _patientNeighborhood;
        string _organizationMember;
        uint256 _patientId;
    }
    uint256 patientId;


    struct Manager {
        string managerName;
        address payable managerWallet;
        string managerPhoneNumber;
        string managerOrganization;
        string managerEmail;
    }

    struct Provider {
        string providerName;
        address payable providerWallet;
        string clinic;
        string providerEmail;
        uint providerIndex;
    }

   
    struct Request {
        address payable _providerWallet;
        uint256 _patientId;
        uint256 _requestId;
        string _requestIPFS;
    }
    string requestListIPFS;

    
    // mappings for easy lookup
    mapping(address => Provider) public _providers;
    mapping(uint256 => Patient) public _patients;
    mapping(uint256 => Request) public _requests;
   

    event logNewProvider(address indexed _providerWallet, uint _providerIndex, string _providerEmail, string indexed _providerName, string indexed _clinic);
    event updateProvider(address indexed _providerWallet, uint _providerIndex, string providerEmail, string indexed _providerName, string indexed _clinic);

    // quick way to verify a provider's status
    function isProvider(address _providerWallet)
    public view
    returns (bool _isProvider) 
    {
    if(_providersList.length == 0) return false;
    return (_providersList[_providers[_providerWallet].providerIndex] == _providerWallet);
    }

    
    // add a provider -- only owners and managers can do this
    function addProvider(
        string memory _providerName,
        address payable _providerWallet,
        string memory _clinic,
        string memory _providerEmail
    ) public {
        _setupRole(NEW_PROVIDER_ROLE, msg.sender);
        require (hasRole(OWNER_ROLE, msg.sender) || hasRole(MANAGER_ROLE,msg.sender) || hasRole(NEW_PROVIDER_ROLE, msg.sender), "You do not have permission to add providers.");
        //if(isProvider(_providerWallet)) revert;
        _providers[_providerWallet].providerWallet = _providerWallet;
        _providers[_providerWallet].providerName = _providerName;
        _providers[_providerWallet].clinic = _clinic;
        _providers[_providerWallet].providerEmail = _providerEmail;
        _providersList.push(_providerWallet);
        _providers[_providerWallet].providerIndex = _providersList.length - 1; 
        _setupRole(PROVIDER_ROLE, _providerWallet);
        
        emit logNewProvider(
            _providerWallet,
            _providers[_providerWallet].providerIndex,
            _providerEmail,
            _providerName,
            _clinic
        );
    }


    event logNewPatient (
        string indexed _patientName,
        string indexed _patientLocation,
        bool _doesConsent,
        string  _deliveryReason,
        bool _isQuarantined,
        bool _needsDelivery,
        string _preferredLanguage,
        string _patientPhoneNumber,
        string indexed _patientNeighborhood,
        string _organizationMember,
        //address payable _patientWallet,
        uint _patientAge,
        uint256 patientId
    );
    
    event updatePatient (
        string indexed _patientName,
        string indexed _patientLocation,
        bool _doesConsent,
        string  _deliveryReason,
        bool _isQuarantined,
        bool _needsDelivery,
        string _preferredLanguage,
        string _patientPhoneNumber,
        string indexed _patientNeighborhood,
        string _organizationMember,
        //address payable _patientWallet,
        uint _patientAge,
        uint256 patientId
    );


     // add patient function -- owners, managers, and providers can do this
    function addPatient(
        string memory _patientLocation,
        string memory _patientName,
        bool _doesConsent,
        string memory _deliveryReason,
        bool _isQuarantined,
        bool _needsDelivery,
        string memory _preferredLanguage,
        string memory _patientPhoneNumber,
        string memory _patientNeighborhood,
        string memory _organizationMember,
        //address payable _patientWallet,
        uint _patientAge

    ) public {
        require (hasRole(OWNER_ROLE, msg.sender) || hasRole(MANAGER_ROLE, msg.sender) || hasRole(PROVIDER_ROLE, msg.sender), "You do not have permission to add patients!.");
        
        patientId = _patientsCount.current();
        _patients[patientId]._patientName = _patientName;
        _patients[patientId]._doesConsent = _doesConsent;
        _patients[patientId]._deliveryReason = _deliveryReason;
        _patients[patientId]._isQuarantined = _isQuarantined;
        _patients[patientId]._needsDelivery = _needsDelivery;
        _patients[patientId]._preferredLanguage = _preferredLanguage;
        _patients[patientId]._patientPhoneNumber = _patientPhoneNumber;
        _patients[patientId]._patientNeighborhood = _patientNeighborhood;
        _patients[patientId]._organizationMember = _organizationMember;
        _patients[patientId]._patientAge = _patientAge;
        _patients[patientId]._patientId = patientId;
        //_setupRole(PATIENT_ROLE, patientId);
        _patientsCount.increment();

        
        emit logNewPatient (
            _patientName,
            _patientLocation,
            _doesConsent,
            _deliveryReason,
            _isQuarantined,
            _needsDelivery,
            _preferredLanguage,
            _patientPhoneNumber,
            _patientNeighborhood,
            _organizationMember,
            //address payable _patientWallet,
            _patientAge,
            patientId
        );
    }

    function getSinglePatient (uint i) public view returns (Patient memory) {
        Patient storage _singlePatient = _patients[i];
        return (_singlePatient);
    }


    event logNewRequest (
        uint256 indexed _patientId,
        uint256 indexed requestId,
        address payable indexed _providerWallet,
        string _requestIPFS,
        string _requestListIPFS
    );
  

    function newRequest(
        address payable _providerWallet,
        uint256 _patientId,
        string memory _requestIPFS,
        string memory _requestListIPFS
    ) public returns (uint256) {
        require (hasRole(OWNER_ROLE, msg.sender) || hasRole(MANAGER_ROLE, msg.sender) || hasRole(PROVIDER_ROLE, msg.sender), "You do not have permission to make requests!");    
        uint256 requestId = _requestsCount.current();
        _requests[requestId]._patientId = _patientId;
        _requests[requestId]._requestId = requestId;
        _requests[requestId]._requestIPFS = _requestIPFS;
        _requests[requestId]._providerWallet = _providerWallet;
        requestListIPFS = _requestListIPFS;
        _requestsCount.increment();

        emit logNewRequest (
            _patientId = _patientId,
            requestId = requestId,
            _providerWallet = payable(_providerWallet),
            _requestIPFS = _requestIPFS,
            _requestListIPFS = _requestListIPFS
        );

        return (requestId);
    }
}
  

    