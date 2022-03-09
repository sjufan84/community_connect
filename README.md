# Community Connect

![solidity](Resources/CommunityConnect_image.png)

A decentralized application to facilitate an ecosystem of donors, non-profits, and end users in the distribution of aid. Community Connect allows Donors and Philanthropists to Donate money with the Trust that All the Money goes to Charitable works. We have Automated the process of receiving donations, requests in the form of cash assistance, reguests for Goods, Rides and then fullfillment of the Requests. Donors and users of the dapp are able to verify all activity on the blockchain.

## Technologies

This dApp was developed with Python, Solidity and the following packages and libraries:

- Streamlit
- web3
- Pandas
- Json

Community Connect was tested with Ganache and Metamask to simulate characteristics of a blockchain. 

What is Ganache?

Ganache is a personal blockchain for rapid Ethereum and Corda distributed application development. You can use Ganache across the entire development cycle; enabling you to develop, deploy, and test your dApps in a safe and deterministic environment.
To install Ganache please see this link:  [Ganache](https://trufflesuite.com/ganache/) and select the installer for your OS.

What is Metamask?

MetaMask is the easiest way to interact with dapps in a browser. It is an extension for Chrome or Firefox that connects to an Ethereum network without running a full node on the browser's machine. It can connect to the main Ethereum network, any of the testnets (Ropsten, Kovan, and Rinkeby), or a local blockchain such as the one created by Ganache or Truffle Develop.
To install Metamask please see this link: [MetaMask](https://metamask.io/download/) and select your OS.

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

To simulate a Local Blockchain please download 
## Requirements
Create a `.env` file
* Specify the address that the Web3 provider will use for the local `Ganache` blockchain.
`WEB3_PROVIDER_URI=HTTP://127.0.0.1:7545`

* Specify the address of the deployed contract.  You can find this address in the Remix IDE when displaying the deployed contract.  See example below.
`SMART_CONTRACT_ADDRESS='<YOUR_DEPLOYED_CONTRACT_ADDRESS_HERE>'`

* 
## Usage

## Contributors

Additional updates/ uploads for usability was added by [Dave Thomas](mailto:sjufan84@gmail.com)

Additional updates/ uploads for usability was added by [Stephen Thomas](mailto:stephenthomas43@gmail.com)

Additional updates/ uploads for usability was added by [Christina San Diego](mailto:cbuted@gmail.com)

## License

MIT License
