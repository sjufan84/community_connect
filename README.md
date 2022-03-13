# Community Connect

![solidity](Resources/CommunityConnect_image.png)

A decentralized application to facilitate an ecosystem of donors, non-profits, and end users in the distribution of aid. Community Connect allows Donors and Philanthropists to Donate money with the Trust that All the Money goes to Charitable works. We have Automated the process of receiving donations, requests in the form of cash assistance, reguests for Goods, Rides and then fullfillment of the Requests. Donors and users of the dapp are able to verify all activity on the blockchain.
This dApp was built to solve the transparency and efficiency issues. We do this by introducing smart contracts to automate processes and print All transactions to the blockchain. We think that the non-profit sector has a lot to gain from a dApp like Community Connect.

## Technologies

This dApp was developed with Python, Solidity and the following packages and libraries:

- Streamlit
- web3
- Pandas
- Json

Community Connect was tested with Ganache and Metamask to simulate characteristics of a blockchain. We have also used IPFS to store all blockchain transactions. 

What is Ganache?

Ganache is a personal blockchain for rapid Ethereum and Corda distributed application development. You can use Ganache across the entire development cycle; enabling you to develop, deploy, and test your dApps in a safe and deterministic environment.
To install Ganache please see this link:  [Ganache](https://trufflesuite.com/ganache/) and select the installer for your OS.

What is Metamask?

MetaMask is the easiest way to interact with dapps in a browser. It is an extension for Chrome or Firefox that connects to an Ethereum network without running a full node on the browser's machine. It can connect to the main Ethereum network, any of the testnets (Ropsten, Kovan, and Rinkeby), or a local blockchain such as the one created by Ganache or Truffle Develop.
To install Metamask please see this link: [MetaMask](https://metamask.io/download/) and select your OS.

What is IPFS?

The InterPlanetary File System is a protocol and peer-to-peer network for storing and sharing data in a distributed file system. IPFS uses content-addressing to uniquely identify each file in a global namespace connecting all computing devices.


## Installation Guide

Community Connect web app requires a few installations before launching. If the user wants to interact with the dApp, add features, ect. Please install the following: To get started using this application please go to [Python Download](https://www.python.org/downloads/) and select the version for your operating system. Then install the following libraries and packages.

``` sudo apt install python3-pip ```. This will install the pip that will make it easier to install the libraries.

``` pip install pandas ```

``` pip install streamlit ```

``` pip install web3 ```

``` pip install jsonlib ```

``` pip install python-dotenv ```

``` pip install yfinance ```

``` pip install requests ```

``` pip install plotly ```


## Requirements
Create a `.env` file and include the following:
* Specify the address that the Web3 provider will use for the local `Ganache` blockchain.
`WEB3_PROVIDER_URI=<YOR_WEB3_PROVIDER_URI>'`

* Specify the address of the deployed contract. 
`SMART_CONTRACT_ADDRESS='0xcF6DdE7878513412eA42bA16074De35A6c6C0317'`

* Specify your Pinata API key and Secret API key.
`PINATA_API_KEY='<YOUR_API_KEY_HERE>'`
`PINATA_SECRET_API_KEY='<YOUR_SECRET_API_KEY_HERE>'`

* Specify your Mapbox Access token.
`MAPBOX_ACCESS_TOKEN = '<YOUR_MAPBOX_ACCESS_TOKEN_HERE>'`

## Usage

To use this dApp, First clone this repository into a folder onto your computer. Navigate into the new Community Connect folder and build a .env file. In this .env file you will store all the requirements from above. Open an integrated terminal in the Community Connect folder and run ``` streamlit run app.py ```. 

## Workflow of dApp

- Donate USD into the Contract on ``` Make a Donation ``` page.
- Users can make a request for goods on the ``` Request for Goods ``` page.
- Suppliers will offer to fill the request on ``` Viewing Open Goods Request ```  and send an invoice for compensation.
- Non-profit approves the offer from supplier on ``` View Fill Goods Offers ``` page and then pay supplier by hitting the pay invoice button on ``` Pay Supplier Invoice ``` page.
- User's can make a request for cash assistance, and the non-profit has a chance to review the request and approve by hitting the ``` Approve Cash Request ``` button.
- Anyone can check account balances on the ``` Get Balances ``` page.
- Anyone can verify all transactions on the ``` View Contract Ledger ``` page. 


## Contributors

Additional updates/ uploads for usability was added by [Dave Thomas](mailto:sjufan84@gmail.com)

Additional updates/ uploads for usability was added by [Stephen Thomas](mailto:stephenthomas43@gmail.com)

Additional updates/ uploads for usability was added by [Christina San Diego](mailto:cbuted@gmail.com)

## License

MIT License
