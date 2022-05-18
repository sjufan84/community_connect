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
    bytes32 public constant SUPPLIER_ROLE = keccak256("VENDOR_ROLE");
    bytes32 public constant DRIVER_ROLE = keccak256("DRIVER_ROLE");


  
    

    // initially establish the owner of the contract and give them the owner role
    constructor () {
        address payable contractOwner = payable(msg.sender);
        _setupRole(OWNER_ROLE, contractOwner);
    }

    using SafeMath for uint;

    // Establishing counters for all of our lists
    using Counters for Counters.Counter;
    Counters.Counter private _patientsCount;
    Counters.Counter private _requestsCount;
    Counters.Counter private _invoices;
    Counters.Counter private _driversCount;

    // structs for commonly used data types
    struct Patient {
        string _patientName;
        address payable _patientWallet;
        uint256 _patientId;
    }
    address payable patientWallet;
    uint256 patientId;


    struct Manager {
        address payable _managerWallet;
    }

    struct Provider {
        address payable _providerWallet;
    }
    address payable providerWallet;
   
    struct Request {
        address payable _providerWallet;
        uint256 _patientId;
        uint256 _requestId;
    }
    uint256 requestId;

    struct Driver {
        address payable _driverWallet;
        uint256 _driverId;
    }
    uint256 driverId;
    address payable driverWallet;
    
    struct Supplier {
        address payable _supplierWallet;
    }
    address payable supplierWallet;
    
    // mappings for easy lookup
    mapping(address => Provider) public _providers;
    mapping(address => Supplier) public _suppliers;
    mapping(address => Driver) public _drivers;
    mapping(uint256 => Patient) public _patients;
    mapping(uint256 => Request) public _requests;
   
    event logNewProvider(address indexed _providerWallet);
    event updateProvider(address indexed _providerWallet);

    
    // add a provider -- only owners and managers can do this
    function addProvider(
        address payable _providerWallet
    ) public returns (address payable) {
        require (hasRole(OWNER_ROLE, msg.sender) || hasRole(MANAGER_ROLE,msg.sender), "You do not have permission to add providers.");
        //if(isProvider(_providerWallet)) revert;
        _providers[_providerWallet]._providerWallet = _providerWallet;
        _setupRole(PROVIDER_ROLE, _providerWallet);
        
        emit logNewProvider(
            _providerWallet
        );
        return _providerWallet;
    }


    event logNewPatient (
        address payable _patientWallet,
        uint256 patientId
    );
    
    event updatePatient (
        address payable _patientWallet,
        uint256 patientId
    );


     // add patient function -- owners, managers, and providers can do this
    function addPatient(
        address payable _patientWallet
    ) public {
        require (hasRole(OWNER_ROLE, msg.sender) || hasRole(MANAGER_ROLE, msg.sender) || hasRole(PROVIDER_ROLE, msg.sender), "You do not have permission to add patients!.");
        
        patientId = _patientsCount.current();
        _patients[patientId]._patientWallet = _patientWallet;
        _setupRole(PATIENT_ROLE, _patientWallet);
        _patientsCount.increment();

        
        emit logNewPatient (
            _patientWallet,
            patientId
        );
    }

    
    event logNewRequest (
        uint256 indexed _patientId,
        uint256 indexed requestId,
        address payable indexed _providerWallet
    );
  

    function newRequest(
        address payable _providerWallet,
        uint256 _patientId
    ) public returns (uint256) {
        require (hasRole(OWNER_ROLE, msg.sender) || hasRole(MANAGER_ROLE, msg.sender) || hasRole(PROVIDER_ROLE, msg.sender), "You do not have permission to make requests!");    
        requestId = _requestsCount.current();
        _requests[requestId]._patientId = _patientId;
        _requests[requestId]._requestId = requestId;
        _requests[requestId]._providerWallet = _providerWallet;
        _requestsCount.increment();

        emit logNewRequest (
            _patientId = _patientId,
            requestId = requestId,
            _providerWallet = payable(_providerWallet)
        );

        return (requestId);
    }


    event logNewSupplier (
        address indexed _supplierWallet
    );
    
    event logSupplierUpdate (
        address indexed _supplierWallet
    );


    // add supplier function -- owners and managers can do this
    function addSupplier(
        address payable _supplierWallet

        ) public returns (address payable) {
        require (hasRole(OWNER_ROLE, msg.sender) || hasRole(MANAGER_ROLE, msg.sender), "You do not have permission to add patients!.");
        
        supplierWallet = _supplierWallet;
        _suppliers[supplierWallet]._supplierWallet = _supplierWallet;
        _setupRole(SUPPLIER_ROLE, supplierWallet);

        
        emit logNewSupplier (
        _supplierWallet
        );

        return _supplierWallet;
    }
    

    // add supplier function -- owners and managers can do this
    function updateSupplier(
        address payable _supplierWallet
        ) public {
        require (hasRole(OWNER_ROLE, msg.sender) || hasRole(MANAGER_ROLE, msg.sender), "You do not have permission to add patients!.");
        
        supplierWallet = _supplierWallet;
        _suppliers[supplierWallet]._supplierWallet = _supplierWallet;

        emit logSupplierUpdate (
        _supplierWallet
        );
    }
    

    event logNewDriver (
        address indexed _driverWallet,
        uint256 indexed _driverId
    );
    
    event logDriverUpdate (
        address indexed _driverWallet,
        uint256 indexed _driverId
    );


    // add driver function -- owners and managers can do this
    function addDriver(   
        address payable _driverWallet
    ) public returns (address payable) {
        require (hasRole(OWNER_ROLE, msg.sender) || hasRole(MANAGER_ROLE, msg.sender), "You do not have permission to add patients!.");
        
        driverId = _driversCount.current();
        driverWallet = _driverWallet;
        _drivers[driverWallet]._driverWallet = _driverWallet;
        _drivers[driverWallet]._driverId = driverId;
        _setupRole(DRIVER_ROLE, driverWallet);
        _driversCount.increment();
        
        emit logNewDriver (
        _driverWallet,
        driverId   
        );

        return (driverWallet);
    }
    

    // add driver function -- owners and managers can do this
    function updateDriver(     
        address payable _driverWallet,
        uint256 _driverId
        ) public {
        require (hasRole(OWNER_ROLE, msg.sender) || hasRole(MANAGER_ROLE, msg.sender), "You do not have permission to add patients!.");
        
        driverWallet = _driverWallet;
        _drivers[driverWallet]._driverWallet = _driverWallet;
        _drivers[driverWallet]._driverId = _driverId;
       
        emit logDriverUpdate (
        _driverWallet,
        _driverId    
        );
    }
}